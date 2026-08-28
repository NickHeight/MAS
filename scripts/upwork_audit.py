#!/usr/bin/env python3
"""Audit ~/Upwork/ root: classify zones, map client bundles, detect gaps, write inventory."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from models import (
    ClientBundle,
    ClientBundlePaths,
    FourPillarStatus,
    GitRepoInfo,
    MessageBackupZone,
    OrphanFile,
    ReadmeTableRow,
    SystemEntry,
    UpworkInventory,
    ZoneClass,
)

MAS_ROOT = Path(__file__).resolve().parent.parent
AUDITS_DIR = MAS_ROOT / "llm_wiki" / "audits"
GLOBAL_KB_ENTITIES = Path.home() / ".claude" / "kb" / "wiki" / "entities"
UPWORK_PATHS_YAML = MAS_ROOT / "orchestrator" / "upwork_paths.yaml"

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".obsidian"}

# Known client bundles — extend as audit discovers new clients
KNOWN_BUNDLES: list[dict] = [
    {
        "slug": "turo",
        "display_name": "Coastal Lux / Turo (Marc Walden)",
        "reference": ["clients/coastal-lux", "clients/turo"],
        "projects": ["projects/turo-fleet-automation-system"],
        "wiki": "llmwiki/Turo",
        "global_kb_entity": "marc-walden-turo-fleet.md",
        "modules": ["web", "automation"],
        "sms_contacts": ["Marc Walden"],
    },
    {
        "slug": "openclaw",
        "display_name": "OpenClaw / HIRO (Elijah Booker)",
        "reference": [],
        "projects": ["projects/Elijah B - OpenClaw AI Agent 3 Businesses"],
        "wiki": "llmwiki/OpenClaw",
        "global_kb_entity": "elijah-booker-hiro-openclaw.md",
        "modules": ["ai_agents", "automation"],
        "sms_contacts": ["HIRO", "Elijah Booker"],
    },
]

ARCHIVED_BUNDLES: list[dict] = [
    {
        "slug": "inner-mastery",
        "display_name": "Inner Mastery / Luke Duffy (archived)",
        "reference": ["_archive/clients/inner-mastery", "_archive/clients/luke-duffy"],
        "projects": [],
        "wiki": None,
        "global_kb_entity": "inner-mastery-luke-duffy.md",
        "modules": [],
    },
    {
        "slug": "joshua",
        "display_name": "Joshua / EthosOne (archived)",
        "reference": [],
        "projects": [],
        "wiki": "llmwiki/_archive/clients/Joshua",
        "global_kb_entity": None,
        "modules": [],
    },
    {
        "slug": "hatefreefuture",
        "display_name": "HateFreeFuture / Nina (archived)",
        "reference": [],
        "projects": [],
        "wiki": "llmwiki/_archive/clients/HateFreeFuture",
        "global_kb_entity": None,
        "modules": [],
    },
]

# Wiki zones that are internal frameworks, not client bundles
WIKI_FRAMEWORKS: list[dict] = [
    {
        "name": "PremiumWebDesign",
        "path": "llmwiki/PremiumWebDesign",
        "purpose": "High-value proposal website framework (playbooks, palettes, demo workflow)",
        "linked_systems": ["websites"],
    },
]

INTERNAL_SYSTEMS: list[dict] = [
    {"name": "proposal-system", "path": "proposal-system", "class": ZoneClass.INTERNAL_PIPELINE, "purpose": "Upwork client acquisition pipeline"},
    {"name": "websites", "path": "websites", "class": ZoneClass.PORTFOLIO, "purpose": "Website demo portfolio for proposals"},
    {"name": "llmwiki", "path": "llmwiki", "class": ZoneClass.WIKI_REPO, "purpose": "Cross-client LLM wiki"},
    {"name": "height-consulting-site", "path": "height-consulting-site", "class": ZoneClass.AGENCY, "purpose": "Agency marketing site"},
    {"name": "_archive", "path": "_archive", "class": ZoneClass.ARCHIVE, "purpose": "Historical material"},
    {"name": "Messages", "path": "Messages", "class": ZoneClass.MESSAGES, "purpose": "Legacy per-device Upwork DM exports (see external message_backups in upwork_paths.yaml)"},
]

LOOSE_FILE_EXTENSIONS = {".md", ".json", ".jsonl", ".blueprint.json", ".txt", ".csv", ".pdf"}

ORPHAN_DEST_RULES: list[tuple[str, str]] = [
    (r"\.blueprint\.json$|make\.com", "_suggested: nearest projects/*/blueprints/ or automation_workflows/"),
    (r"proposal|cover.?letter", "_suggested: proposal-system/proposals/"),
    (r"\.md$", "_suggested: llmwiki/_shared/ or clients/ reference zone"),
]


def load_message_backup_path() -> Path:
    """Read canonical SMS backup path from orchestrator/upwork_paths.yaml."""
    default = Path("~/OneDrive - Height Consulting/Apps/SMS Backup and Restore/UpworkMsgs").expanduser()
    if not UPWORK_PATHS_YAML.exists():
        return default
    text = UPWORK_PATHS_YAML.read_text(encoding="utf-8")
    match = re.search(r'local_path:\s*["\']?([^"\']+)["\']?', text)
    if match:
        return Path(match.group(1).strip()).expanduser()
    return default


def scan_message_backup_zone(backup_root: Path) -> MessageBackupZone | None:
    """Index SMS Backup & Restore XML exports and map contacts to client slugs."""
    if not backup_root.is_dir():
        return None

    from scan_message_backups import CONTACT_TO_SLUG, scan_backup_root

    summary = scan_backup_root(backup_root)
    if "error" in summary:
        return None

    linked_slugs = sorted(set(CONTACT_TO_SLUG.values()) & set(summary.get("messages_by_client_slug", {}).keys()))
    # include all mapped slugs even if zero messages in scan
    linked_slugs = sorted(set(linked_slugs) | set(CONTACT_TO_SLUG.values()))

    return MessageBackupZone(
        local_path=str(backup_root),
        file_count=summary.get("file_count", 0),
        contacts=summary.get("contacts", {}),
        linked_slugs=linked_slugs,
    )


def attach_message_backups(bundles: list[ClientBundle], zone: MessageBackupZone | None) -> list[ClientBundle]:
    if not zone:
        return bundles
    updated: list[ClientBundle] = []
    for b in bundles:
        data = b.model_dump()
        data["paths"]["message_backups"] = zone.local_path
        for spec in KNOWN_BUNDLES:
            if spec["slug"] == b.slug:
                data["sms_contacts"] = spec.get("sms_contacts", [])
                break
        updated.append(ClientBundle.model_validate(data))
    return updated


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def get_git_remote(path: Path) -> str | None:
    if not (path / ".git").exists():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def find_git_repos(root: Path, max_depth: int = 4) -> list[GitRepoInfo]:
    repos: list[GitRepoInfo] = []
    seen: set[str] = set()

    def walk(current: Path, depth: int) -> None:
        if depth > max_depth:
            return
        if (current / ".git").exists():
            r = rel(root, current)
            if r not in seen:
                seen.add(r)
                repos.append(
                    GitRepoInfo(
                        local_path=r,
                        remote_url=get_git_remote(current),
                        immutable=True,
                    )
                )
            return  # don't recurse into nested .git subdirs from submodules oddly
        try:
            for entry in current.iterdir():
                if entry.is_dir() and entry.name not in SKIP_DIRS:
                    walk(entry, depth + 1)
        except PermissionError:
            pass

    walk(root, 0)
    return repos


def parse_readme_table(readme_path: Path) -> list[ReadmeTableRow]:
    if not readme_path.exists():
        return []
    text = readme_path.read_text(encoding="utf-8", errors="replace")
    rows: list[ReadmeTableRow] = []
    in_table = False
    for line in text.splitlines():
        if line.startswith("| Local path"):
            in_table = True
            continue
        if in_table:
            if not line.startswith("|"):
                if rows:
                    break
                continue
            if re.match(r"^\|[-| ]+\|$", line):
                continue
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 3 and parts[0].startswith("`"):
                local = parts[0].strip("`")
                purpose = parts[1]
                repo_match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", parts[2])
                github = repo_match.group(1) if repo_match else parts[2] or None
                rows.append(ReadmeTableRow(local_path=local, purpose=purpose, github_repo=github))
    return rows


def path_exists(root: Path, rel_path: str) -> bool:
    return (root / rel_path.replace("/", os.sep)).exists()


def infer_modules(project_path: Path) -> list[str]:
    modules: list[str] = []
    if not project_path.exists():
        return modules
    names = " ".join(p.name.lower() for p in project_path.rglob("*") if p.is_file())[:50000]
    if any(x in names for x in ("package.json", "next.config", "vite.config", "src/app")):
        modules.append("web")
    if any(x in names for x in ("blueprint.json", "make.com", "n8n", "scenario")):
        modules.append("automation")
    if any(x in names for x in ("openclaw", "hermes", "agent", "soul.md", "prompts/")):
        modules.append("ai_agents")
    return list(dict.fromkeys(modules))


def check_four_pillars(root: Path, bundle: dict) -> FourPillarStatus:
    status = FourPillarStatus()
    projects = bundle.get("projects", [])
    wiki = bundle.get("wiki")
    entity = bundle.get("global_kb_entity")

    status.project_filesystem = any(path_exists(root, p) for p in projects)
    status.upwork_wiki = bool(wiki and path_exists(root, wiki))
    if entity:
        status.global_kb_entity = (GLOBAL_KB_ENTITIES / entity).exists()
    if wiki and path_exists(root, wiki):
        overview = root / wiki / "00_overview.md"
        readme = root / wiki / "README.md"
        content = ""
        if overview.exists():
            content = overview.read_text(encoding="utf-8", errors="replace")
        elif readme.exists():
            content = readme.read_text(encoding="utf-8", errors="replace")
        status.monday_workspace = "Monday" in content and ("board" in content.lower() or "workspace" in content.lower())

    for p in projects:
        claude = root / p / "CLAUDE.md"
        if claude.exists():
            status.claude_md_in_primary_project = True
            break

    return status


def build_gaps(root: Path, bundle: dict, status: FourPillarStatus) -> list[str]:
    gaps: list[str] = []
    if not status.project_filesystem and bundle.get("projects"):
        gaps.append(f"Missing project path: {bundle['projects']}")
    if not status.upwork_wiki and bundle.get("wiki"):
        gaps.append(f"Missing wiki: {bundle['wiki']}")
    elif bundle.get("wiki") and path_exists(root, bundle["wiki"]):
        overview = root / bundle["wiki"] / "00_overview.md"
        if not overview.exists():
            gaps.append(f"Missing wiki 00_overview.md: {bundle['wiki']}/00_overview.md")
        else:
            content = overview.read_text(encoding="utf-8", errors="replace")
            if "Filesystem map" not in content and "## Filesystem" not in content:
                gaps.append(f"Wiki missing Filesystem map section: {bundle['wiki']}/00_overview.md")
    if bundle.get("global_kb_entity") and not status.global_kb_entity:
        gaps.append(f"Missing Global KB entity: {GLOBAL_KB_ENTITIES / bundle['global_kb_entity']}")
    if status.project_filesystem and not status.claude_md_in_primary_project:
        gaps.append(f"Missing CLAUDE.md in primary project: {bundle['projects'][0] if bundle.get('projects') else '?'}")
    for ref in bundle.get("reference", []):
        if not path_exists(root, ref):
            gaps.append(f"Missing reference folder: {ref}")
    return gaps


def build_client_bundle(root: Path, spec: dict, all_repos: list[GitRepoInfo]) -> ClientBundle:
    paths = ClientBundlePaths(
        reference=[p for p in spec.get("reference", []) if path_exists(root, p)],
        projects=[p for p in spec.get("projects", []) if path_exists(root, p)],
        wiki=spec.get("wiki") if spec.get("wiki") and path_exists(root, spec["wiki"]) else None,
        global_kb_entity=str(GLOBAL_KB_ENTITIES / spec["global_kb_entity"]) if spec.get("global_kb_entity") and (GLOBAL_KB_ENTITIES / spec["global_kb_entity"]).exists() else None,
    )

    bundle_prefixes = set(spec.get("reference", []) + spec.get("projects", []))
    if spec.get("wiki"):
        bundle_prefixes.add(spec["wiki"])

    repos = [r for r in all_repos if any(r.local_path == p or r.local_path.startswith(p + "/") for p in bundle_prefixes)]

    modules = list(spec.get("modules", []))
    for p in paths.projects:
        inferred = infer_modules(root / p)
        for m in inferred:
            if m not in modules:
                modules.append(m)

    status = check_four_pillars(root, spec)
    gaps = build_gaps(root, spec, status)

    return ClientBundle(
        slug=spec["slug"],
        display_name=spec["display_name"],
        paths=paths,
        git_repos=repos,
        four_pillar_status=status,
        modules=modules,
        gaps=gaps,
    )


ROOT_ALLOWLIST_FILES = {"README.md", ".gitignore"}


def find_orphans(root: Path) -> list[OrphanFile]:
    orphans: list[OrphanFile] = []
    try:
        for entry in root.iterdir():
            if entry.name in ROOT_ALLOWLIST_FILES:
                continue
            if entry.is_file() and entry.suffix.lower() in LOOSE_FILE_EXTENSIONS:
                suggestion = "_suggested: move into appropriate zone subfolder"
                for pattern, dest in ORPHAN_DEST_RULES:
                    if re.search(pattern, entry.name, re.I):
                        suggestion = dest
                        break
                orphans.append(
                    OrphanFile(
                        source=entry.name,
                        suggested_destination=suggestion,
                        reason="Loose file at Upwork root",
                    )
                )
    except PermissionError:
        pass
    return orphans


def list_reference_folders(root: Path) -> list[str]:
    clients_dir = root / "clients"
    if not clients_dir.is_dir():
        return []
    return [rel(root, p) for p in clients_dir.iterdir() if p.is_dir()]


def list_unmapped_wiki_clients(root: Path, bundles: list[ClientBundle]) -> list[str]:
    wiki_dir = root / "llmwiki"
    if not wiki_dir.is_dir():
        return []
    mapped = {b.paths.wiki.split("/")[-1] for b in bundles if b.paths.wiki}
    for spec in ARCHIVED_BUNDLES:
        if spec.get("wiki"):
            mapped.add(spec["wiki"].split("/")[-1])
    skip = {"_shared", "CRM", "Hermes", ".obsidian", "_archive", "PremiumWebDesign"}
    unmapped = []
    for p in wiki_dir.iterdir():
        if p.is_dir() and not p.name.startswith(".") and p.name not in skip and p.name not in mapped:
            unmapped.append(p.name)
    return sorted(unmapped)


def render_gap_report(inventory: UpworkInventory) -> str:
    lines = [
        "# Upwork Gap Report",
        "",
        f"**Audited:** {inventory.audited_at}",
        f"**Root:** `{inventory.upwork_root}`",
        "",
        "## Client bundles",
        "",
    ]
    for b in inventory.client_bundles:
        lines.append(f"### {b.display_name} (`{b.slug}`)")
        lines.append("")
        lines.append("| Pillar | Status |")
        lines.append("|--------|--------|")
        fp = b.four_pillar_status
        lines.append(f"| Project filesystem | {'OK' if fp.project_filesystem else 'MISSING'} |")
        lines.append(f"| Upwork wiki | {'OK' if fp.upwork_wiki else 'MISSING'} |")
        lines.append(f"| Global KB entity | {'OK' if fp.global_kb_entity else 'MISSING'} |")
        lines.append(f"| CLAUDE.md in project | {'OK' if fp.claude_md_in_primary_project else 'MISSING'} |")
        lines.append(f"| Monday documented | {'OK' if fp.monday_workspace else 'UNKNOWN/MISSING'} |")
        lines.append("")
        if b.paths.reference:
            lines.append("**Reference paths:**")
            for p in b.paths.reference:
                lines.append(f"- `{p}`")
        if b.paths.projects:
            lines.append("**Project paths:**")
            for p in b.paths.projects:
                lines.append(f"- `{p}`")
        if b.paths.wiki:
            lines.append(f"**Wiki:** `{b.paths.wiki}`")
        if b.paths.global_kb_entity:
            lines.append(f"**Global KB:** `{b.paths.global_kb_entity}`")
        if b.paths.message_backups:
            lines.append(f"**Message backups (SMS XML):** `{b.paths.message_backups}`")
        if b.sms_contacts:
            lines.append(f"**SMS contacts:** {', '.join(b.sms_contacts)}")
        if b.git_repos:
            lines.append("")
            lines.append("**Git repos (immutable):**")
            for r in b.git_repos:
                lines.append(f"- `{r.local_path}` → {r.remote_url or 'local only'}")
        if b.gaps:
            lines.append("")
            lines.append("**Gaps to fix:**")
            for g in b.gaps:
                lines.append(f"- {g}")
        lines.append("")

    lines.extend(["## Internal systems", ""])
    for s in inventory.systems:
        lines.append(f"- **{s.name}** (`{s.local_path}`) — {s.purpose}")
    lines.append("")

    lines.extend(["## Wiki frameworks (not client bundles)", ""])
    for fw in WIKI_FRAMEWORKS:
        lines.append(f"- **{fw['name']}** (`{fw['path']}`) — {fw['purpose']}")
    lines.append("")

    lines.extend(["## Archived client bundles", ""])
    for spec in ARCHIVED_BUNDLES:
        lines.append(f"- **{spec['display_name']}** (`{spec['slug']}`)")
        if spec.get("wiki"):
            lines.append(f"  - Wiki: `{spec['wiki']}`")
        if spec.get("reference"):
            lines.append(f"  - Reference: {', '.join(f'`{p}`' for p in spec['reference'])}")
    lines.append("")

    if inventory.unmapped_wiki_clients:
        lines.extend(["## Unmapped wiki clients", ""])
        for w in inventory.unmapped_wiki_clients:
            lines.append(f"- `llmwiki/{w}/` — not linked to a client bundle")
        lines.append("")

    if inventory.orphans:
        lines.extend(["## Orphan files at root", ""])
        for o in inventory.orphans:
            lines.append(f"- `{o.source}` → {o.suggested_destination}")
        lines.append("")

    if inventory.reference_folders:
        lines.extend(["## All reference folders (clients/)", ""])
        for r in inventory.reference_folders:
            lines.append(f"- `{r}`")
        lines.append("")

    if inventory.message_backup_zone:
        z = inventory.message_backup_zone
        lines.extend(["## Message backups (OneDrive)", ""])
        lines.append(f"- **Path:** `{z.local_path}`")
        lines.append(f"- **Format:** {z.format} ({z.sync})")
        lines.append(f"- **XML files:** {z.file_count}")
        if z.contacts:
            lines.append("- **Contacts found:**")
            for name, count in sorted(z.contacts.items(), key=lambda x: -x[1]):
                lines.append(f"  - `{name}`: {count} message tags")
        lines.append(f"- **Linked client slugs:** {', '.join(z.linked_slugs)}")
        lines.append("")
        lines.append("Scan command: `python scripts/scan_message_backups.py`")
        lines.append("")

    return "\n".join(lines)


def audit(root: Path) -> UpworkInventory:
    root = root.expanduser().resolve()
    all_repos = find_git_repos(root)

    bundles = [build_client_bundle(root, spec, all_repos) for spec in KNOWN_BUNDLES]
    backup_root = load_message_backup_path()
    msg_zone = scan_message_backup_zone(backup_root)
    bundles = attach_message_backups(bundles, msg_zone)

    systems: list[SystemEntry] = []
    for spec in INTERNAL_SYSTEMS:
        p = root / spec["path"]
        if p.exists():
            repos = [r for r in all_repos if r.local_path == spec["path"] or r.local_path.startswith(spec["path"] + "/")]
            systems.append(
                SystemEntry(
                    name=spec["name"],
                    zone_class=spec["class"],
                    local_path=spec["path"],
                    purpose=spec["purpose"],
                    git_repos=repos,
                    immutable=True,
                )
            )

    return UpworkInventory(
        audited_at=datetime.now(timezone.utc).isoformat(),
        upwork_root=str(root),
        readme_rows=parse_readme_table(root / "README.md"),
        client_bundles=bundles,
        systems=systems,
        reference_folders=list_reference_folders(root),
        orphans=find_orphans(root),
        unmapped_wiki_clients=list_unmapped_wiki_clients(root, bundles),
        message_backup_zone=msg_zone,
    )


def apply_cross_links(root: Path, inventory: UpworkInventory, slugs: list[str], dry_run: bool) -> list[str]:
    """B1: Add Filesystem map sections and reference README cross-links."""
    actions: list[str] = []
    root = root.resolve()

    for bundle in inventory.client_bundles:
        if bundle.slug not in slugs:
            continue

        wiki_rel = bundle.paths.wiki
        if not wiki_rel:
            continue

        wiki_path = root / wiki_rel.replace("/", os.sep)
        overview_path = wiki_path / "00_overview.md"
        readme_path = wiki_path / "README.md"

        fs_section = _filesystem_map_section(bundle, root, inventory.message_backup_zone)

        target_paths = [overview_path]
        if readme_path.exists():
            target_paths.append(readme_path)

        for target in target_paths:
            if not target.exists():
                continue
            content = target.read_text(encoding="utf-8", errors="replace")
            if "Filesystem map" not in content:
                new_content = content.rstrip() + "\n\n" + fs_section
                label = "append Filesystem map"
            elif "Message backups" not in content and inventory.message_backup_zone:
                msg_rows = _message_backup_table_rows(bundle).strip()
                marker = "Do not move git-tracked repos"
                if marker in content:
                    new_content = content.replace(marker, msg_rows + "\n\n" + marker)
                else:
                    new_content = content.rstrip() + "\n" + msg_rows + "\n"
                label = "append Message backups rows"
            else:
                actions.append(f"Filesystem map already present: {target}")
                continue
            if dry_run:
                actions.append(f"[dry-run] would {label} to {target}")
            else:
                target.write_text(new_content, encoding="utf-8")
                actions.append(f"Updated {target}")

        if not overview_path.exists() and readme_path.exists() and bundle.slug == "openclaw":
            stub = f"# {bundle.display_name} — Overview\n\nSee [[README.md]] for full project state.\n\n{fs_section}"
            if dry_run:
                actions.append(f"[dry-run] would create {overview_path}")
            else:
                overview_path.write_text(stub, encoding="utf-8")
                actions.append(f"Created {overview_path}")

        # Reference folder cross-links
        for ref in bundle.paths.reference:
            ref_path = root / ref.replace("/", os.sep)
            link_readme = ref_path / "README.md"
            link_content = (
                f"# {ref_path.name} — Reference docs\n\n"
                f"Part of client bundle: **{bundle.display_name}** (`{bundle.slug}`)\n\n"
                f"## Linked paths\n\n"
                f"- Wiki: `{bundle.paths.wiki or 'N/A'}`\n"
            )
            for p in bundle.paths.projects:
                link_content += f"- Project: `{p}`\n"
            if bundle.paths.global_kb_entity:
                link_content += f"- Global KB: `{bundle.paths.global_kb_entity}`\n"
            link_content += f"\nManaged by MAS inventory. Re-run: `python scripts/upwork_audit.py --root ~/Upwork`\n"

            if link_readme.exists():
                actions.append(f"Reference README exists: {link_readme}")
            elif dry_run:
                actions.append(f"[dry-run] would create {link_readme}")
            else:
                ref_path.mkdir(parents=True, exist_ok=True)
                link_readme.write_text(link_content, encoding="utf-8")
                actions.append(f"Created {link_readme}")

        # Enrich Global KB entity with filesystem map pointer if missing
        entity_file = None
        for spec in KNOWN_BUNDLES:
            if spec["slug"] == bundle.slug and spec.get("global_kb_entity"):
                entity_file = GLOBAL_KB_ENTITIES / spec["global_kb_entity"]
                break
        if entity_file and entity_file.exists():
            content = entity_file.read_text(encoding="utf-8", errors="replace")
            additions = ""
            if "MAS inventory" not in content:
                additions += (
                    f"\n\n## MAS filesystem map (auto-maintained)\n\n"
                    f"- Inventory: `c:/Users/Nicol/MAS/llm_wiki/audits/upwork_inventory.json`\n"
                )
                for p in bundle.paths.reference:
                    additions += f"- Reference: `~/Upwork/{p}`\n"
                for p in bundle.paths.projects:
                    additions += f"- Project: `~/Upwork/{p}`\n"
                if bundle.paths.wiki:
                    additions += f"- Wiki: `~/Upwork/{bundle.paths.wiki}`\n"
            if bundle.paths.message_backups and "Message backups" not in content:
                additions += f"- Message backups: `{bundle.paths.message_backups}`\n"
                if bundle.sms_contacts:
                    additions += f"- SMS contacts: {', '.join(bundle.sms_contacts)}\n"
            if additions:
                if dry_run:
                    actions.append(f"[dry-run] would append MAS map to {entity_file}")
                else:
                    if "MAS filesystem map" not in content and additions.startswith("\n\n##"):
                        entity_file.write_text(content.rstrip() + additions, encoding="utf-8")
                    else:
                        entity_file.write_text(content.rstrip() + "\n" + additions.lstrip(), encoding="utf-8")
                    actions.append(f"Updated {entity_file}")

    return actions


def _message_backup_table_rows(bundle: ClientBundle) -> str:
    if not bundle.paths.message_backups:
        return ""
    lines = [
        "| Message backups (SMS XML) | `" + bundle.paths.message_backups + "` |",
    ]
    if bundle.sms_contacts:
        lines.append("| SMS contact filter | `" + ", ".join(bundle.sms_contacts) + "` |")
    return "\n".join(lines) + "\n"


def _filesystem_map_section(
    bundle: ClientBundle,
    root: Path,
    zone: MessageBackupZone | None = None,
) -> str:
    lines = [
        "## Filesystem map",
        "",
        f"Canonical client bundle: **{bundle.display_name}** (`{bundle.slug}`)",
        "",
        "| Zone | Path |",
        "|------|------|",
    ]
    for p in bundle.paths.reference:
        lines.append(f"| Reference docs | `~/Upwork/{p}` |")
    for p in bundle.paths.projects:
        lines.append(f"| Code / project | `~/Upwork/{p}` |")
    if bundle.paths.wiki:
        lines.append(f"| LLM Wiki | `~/Upwork/{bundle.paths.wiki}` |")
    if bundle.paths.global_kb_entity:
        lines.append(f"| Global KB entity | `{bundle.paths.global_kb_entity}` |")
    if bundle.paths.message_backups:
        lines.append(f"| Message backups (SMS XML) | `{bundle.paths.message_backups}` |")
        if bundle.sms_contacts:
            lines.append(f"| SMS contact filter | `{', '.join(bundle.sms_contacts)}` |")
    lines.append(f"| MAS inventory | `c:/Users/Nicol/MAS/llm_wiki/audits/upwork_inventory.json` |")
    lines.append("")
    lines.append("Do not move git-tracked repos — reconcile via cross-links only.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="MAS Upwork root auditor")
    parser.add_argument("--root", type=Path, default=Path.home() / "Upwork")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--use-gemini", action="store_true", help="Reserved for fuzzy matching (not required)")
    parser.add_argument("--apply-cross-links", action="store_true", help="Apply B1 cross-links for bundles")
    parser.add_argument("--bundles", default="turo,openclaw", help="Comma-separated slugs for --apply-cross-links")
    parser.add_argument("--apply-orphans", action="store_true", help="Move orphan root files (requires APPROVE)")
    args = parser.parse_args()

    if args.use_gemini:
        print("Note: --use-gemini reserved for future fuzzy matching; using heuristic bundles.")

    inventory = audit(args.root)
    AUDITS_DIR.mkdir(parents=True, exist_ok=True)

    inv_path = AUDITS_DIR / "upwork_inventory.json"
    gap_path = AUDITS_DIR / "upwork_gap_report.md"
    orphan_path = AUDITS_DIR / "orphan_moves.json"

    inv_json = json.dumps(inventory.model_dump(), indent=2)
    gap_md = render_gap_report(inventory)
    orphan_json = json.dumps([o.model_dump() for o in inventory.orphans], indent=2)

    if args.dry_run:
        print(inv_json)
        print("\n--- Gap report preview ---\n")
        print(gap_md[:3000])
        print(f"\n[dry-run] would write: {inv_path}, {gap_path}, {orphan_path}")
    else:
        inv_path.write_text(inv_json, encoding="utf-8")
        gap_path.write_text(gap_md, encoding="utf-8")
        orphan_path.write_text(orphan_json, encoding="utf-8")
        print(f"Inventory: {inv_path}")
        print(f"Gap report: {gap_path}")
        print(f"Orphans: {orphan_path}")

    if args.apply_cross_links:
        slugs = [s.strip() for s in args.bundles.split(",") if s.strip()]
        actions = apply_cross_links(args.root, inventory, slugs, dry_run=args.dry_run)
        for a in actions:
            print(a)

    if args.apply_orphans and inventory.orphans:
        if args.dry_run:
            print("\n[dry-run] orphan moves not applied")
        else:
            confirm = input("Type APPROVE to move orphan files: ")
            if confirm.strip() != "APPROVE":
                print("Aborted.")
                return 1
            for o in apply_orphan_moves(args.root, inventory.orphans):
                print(o)

    return 0


ORPHAN_MOVE_TARGETS: dict[str, str] = {
    "git-check-out.txt": "_archive/misc/git-check-out.txt",
    "Weekly-Review-2026-04-26.md": "_archive/weekly-reviews/Weekly-Review-2026-04-26.md",
}


def apply_orphan_moves(root: Path, orphans: list[OrphanFile]) -> list[str]:
    """Move known orphan root files into _archive/ subfolders."""
    actions: list[str] = []
    for orphan in orphans:
        dest_rel = ORPHAN_MOVE_TARGETS.get(orphan.source)
        if not dest_rel:
            actions.append(f"SKIP (no rule): {orphan.source}")
            continue
        src = root / orphan.source
        dest = root / dest_rel
        if not src.is_file():
            actions.append(f"SKIP (missing): {orphan.source}")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            actions.append(f"SKIP (exists): {dest_rel}")
            continue
        src.rename(dest)
        actions.append(f"MOVED: {orphan.source} -> {dest_rel}")
    return actions


if __name__ == "__main__":
    sys.exit(main())
