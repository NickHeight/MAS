#!/usr/bin/env python3
"""Provision four-pillar client workspace from MAS template."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

# Allow running as script from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent))

from models import ClientModule, ClientScaffoldRequest, ClientScaffoldResult, MondayChecklist
from models import ClientBundle, ClientBundlePaths, FourPillarStatus, UpworkInventory

MAS_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = MAS_ROOT / "templates" / "client-workspace"
UPWORK_ROOT = Path.home() / "Upwork"
UPWORK_PROJECTS = UPWORK_ROOT / "projects"
UPWORK_WIKI = UPWORK_ROOT / "llmwiki"
UPWORK_README = UPWORK_ROOT / "README.md"
INVENTORY_PATH = MAS_ROOT / "llm_wiki" / "audits" / "upwork_inventory.json"
GLOBAL_KB_ENTITIES = Path.home() / ".claude" / "kb" / "wiki" / "entities"

STANDARD_DIRS = [
    "docs/architecture",
    "docs/client",
    "docs/plans",
    "docs/reference",
    "docs/guides",
    "docs/research",
    "docs/assets",
    "scripts",
    "tests",
    "data",
    "communications_history/briefs",
    "communications_history/monday_logs",
    "config",
]

MODULE_DIRS = {
    ClientModule.WEB: "web_development",
    ClientModule.AUTOMATION: "automation_workflows/n8n_nodes",
    ClientModule.AI_AGENTS: "ai_agents/core",
}

MODULE_AUTOMATION_EXTRA = [
    "automation_workflows/make_scenarios",
    "automation_workflows/webhooks",
]

MODULE_WEB_EXTRA = ["web_development/src", "web_development/public"]


def wiki_name_from_slug(slug: str) -> str:
    """Convert acme-corp -> AcmeCorp for wiki folder naming."""
    parts = slug.split("-")
    return "".join(p.capitalize() for p in parts)


def render_template(content: str, context: dict[str, str]) -> str:
    for key, value in context.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    return content


def build_module_rules(modules: list[ClientModule]) -> str:
    rules = []
    if ClientModule.WEB in modules:
        rules.append("- Web assets: only edit files inside `web_development/`")
    if ClientModule.AUTOMATION in modules:
        rules.append("- Workflow JSON: output to `automation_workflows/n8n_nodes/` or `make_scenarios/`")
    if ClientModule.AI_AGENTS in modules:
        rules.append("- Agent code: only edit files inside `ai_agents/`")
    if not rules:
        rules.append("- No modules enabled; use `docs/` and `scripts/` only")
    return "\n".join(rules)


def build_context(req: ClientScaffoldRequest) -> dict[str, str]:
    modules_str = ", ".join(m.value for m in req.modules)
    wiki_name = wiki_name_from_slug(req.slug)
    today = date.today().isoformat()
    return {
        "CLIENT_NAME": req.name,
        "CLIENT_SLUG": req.slug,
        "CLIENT_WIKI_NAME": wiki_name,
        "DESCRIPTION": req.description or f"Client project for {req.name}.",
        "MODULES": modules_str or "none",
        "MODULES_JSON": json.dumps([m.value for m in req.modules]),
        "MODULE_RULES": build_module_rules(req.modules),
        "SCAFFOLD_DATE": today,
    }


def write_rendered_template(src: Path, dest: Path, context: dict[str, str], dry_run: bool) -> None:
    content = src.read_text(encoding="utf-8")
    rendered = render_template(content, context)
    if dry_run:
        print(f"  [dry-run] would write: {dest}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(rendered, encoding="utf-8")


def copy_static(src: Path, dest: Path, dry_run: bool) -> None:
    if dry_run:
        print(f"  [dry-run] would copy: {src} -> {dest}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        if dest.exists():
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            shutil.copytree(src, dest)
    else:
        shutil.copy2(src, dest)


def scaffold(req: ClientScaffoldRequest, dry_run: bool = False) -> ClientScaffoldResult:
    ctx = build_context(req)
    wiki_name = ctx["CLIENT_WIKI_NAME"]
    project_path = UPWORK_PROJECTS / req.slug
    wiki_path = UPWORK_WIKI / wiki_name
    entity_path = GLOBAL_KB_ENTITIES / f"{req.slug}.md"

    print(f"\nScaffolding client: {req.name} ({req.slug})")
    print(f"  Modules: {ctx['MODULES']}")
    print(f"  Dry run: {dry_run}\n")

    # --- Pillar 1: Project filesystem ---
    print("Pillar 1: Project filesystem")
    for subdir in STANDARD_DIRS:
        p = project_path / subdir
        if dry_run:
            print(f"  [dry-run] would mkdir: {p}")
        else:
            p.mkdir(parents=True, exist_ok=True)

    template_files = [
        (".cursorrules.template", ".cursorrules"),
        ("CLAUDE.md.template", "CLAUDE.md"),
        ("README.md.template", "README.md"),
        (".gitignore", ".gitignore"),
        ("docker-compose.yml", "docker-compose.yml"),
        ("config/env.example", "config/env.example"),
        ("config/settings.json.template", "config/settings.json"),
    ]
    for src_name, dest_name in template_files:
        write_rendered_template(
            TEMPLATE_ROOT / src_name,
            project_path / dest_name,
            ctx,
            dry_run,
        )

    for module in req.modules:
        base = MODULE_DIRS[module]
        if dry_run:
            print(f"  [dry-run] would mkdir: {project_path / base}")
        else:
            (project_path / base).mkdir(parents=True, exist_ok=True)

        if module == ClientModule.WEB:
            for extra in MODULE_WEB_EXTRA:
                p = project_path / extra
                if dry_run:
                    print(f"  [dry-run] would mkdir: {p}")
                else:
                    p.mkdir(parents=True, exist_ok=True)
            write_rendered_template(
                TEMPLATE_ROOT / "modules/web/package.json.template",
                project_path / "web_development/package.json",
                ctx,
                dry_run,
            )
            copy_static(
                TEMPLATE_ROOT / "modules/web/README.md",
                project_path / "web_development/README.md",
                dry_run,
            )
        elif module == ClientModule.AUTOMATION:
            for extra in MODULE_AUTOMATION_EXTRA:
                p = project_path / extra
                if dry_run:
                    print(f"  [dry-run] would mkdir: {p}")
                else:
                    p.mkdir(parents=True, exist_ok=True)
            copy_static(
                TEMPLATE_ROOT / "modules/automation/README.md",
                project_path / "automation_workflows/README.md",
                dry_run,
            )
        elif module == ClientModule.AI_AGENTS:
            copy_static(
                TEMPLATE_ROOT / "modules/ai_agents/README.md",
                project_path / "ai_agents/README.md",
                dry_run,
            )
            copy_static(
                TEMPLATE_ROOT / "modules/ai_agents/requirements.txt",
                project_path / "ai_agents/requirements.txt",
                dry_run,
            )

    # --- Pillar 2: Upwork LLM Wiki ---
    print("\nPillar 2: Upwork LLM Wiki")
    wiki_templates = [
        ("wiki/00_overview.md.template", "00_overview.md"),
        ("wiki/index.md.template", "index.md"),
        ("wiki/log.md.template", "log.md"),
    ]
    for subdir in ["entities", "concepts", "playbooks", "decisions", "sources"]:
        p = wiki_path / subdir
        if dry_run:
            print(f"  [dry-run] would mkdir: {p}")
        else:
            p.mkdir(parents=True, exist_ok=True)

    for src_name, dest_name in wiki_templates:
        write_rendered_template(
            TEMPLATE_ROOT / src_name,
            wiki_path / dest_name,
            ctx,
            dry_run,
        )

    # --- Pillar 3: Global KB entity ---
    print("\nPillar 3: Global KB entity")
    write_rendered_template(
        TEMPLATE_ROOT / "wiki/entity.md.template",
        entity_path,
        ctx,
        dry_run,
    )

    # --- Pillar 4: Monday checklist stub ---
    print("\nPillar 4: Monday.com (manual checklist)")
    checklist = MondayChecklist(client_name=req.name, slug=req.slug)
    rendered_checklist = checklist.render()
    for step in rendered_checklist:
        print(f"  - {step}")

    result = ClientScaffoldResult(
        project_path=str(project_path),
        wiki_path=str(wiki_path),
        entity_path=str(entity_path),
        modules=[m.value for m in req.modules],
        monday_checklist=rendered_checklist,
        dry_run=dry_run,
    )

    register_in_inventory(req, result, dry_run=dry_run)
    append_readme_row(req, dry_run=dry_run)

    print("\nScaffold complete.")
    return result


def register_in_inventory(req: ClientScaffoldRequest, result: ClientScaffoldResult, dry_run: bool) -> None:
    """Append new client to upwork_inventory.json."""
    wiki_name = wiki_name_from_slug(req.slug)
    project_rel = f"projects/{req.slug}"
    wiki_rel = f"llmwiki/{wiki_name}"

    new_bundle = ClientBundle(
        slug=req.slug,
        display_name=req.name,
        paths=ClientBundlePaths(
            reference=[],
            projects=[project_rel],
            wiki=wiki_rel,
            global_kb_entity=result.entity_path,
        ),
        four_pillar_status=FourPillarStatus(
            project_filesystem=True,
            upwork_wiki=True,
            global_kb_entity=True,
            claude_md_in_primary_project=True,
        ),
        modules=[m.value for m in req.modules],
        gaps=["Monday workspace not yet provisioned"],
    )

    if dry_run:
        print(f"  [dry-run] would register bundle in {INVENTORY_PATH}")
        return

    INVENTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if INVENTORY_PATH.exists():
        data = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        inventory = UpworkInventory.model_validate(data)
        inventory.client_bundles = [b for b in inventory.client_bundles if b.slug != req.slug]
        inventory.client_bundles.append(new_bundle)
    else:
        from datetime import datetime, timezone

        inventory = UpworkInventory(
            audited_at=datetime.now(timezone.utc).isoformat(),
            upwork_root=str(UPWORK_ROOT),
            client_bundles=[new_bundle],
        )

    INVENTORY_PATH.write_text(json.dumps(inventory.model_dump(), indent=2), encoding="utf-8")
    print(f"  Registered in inventory: {INVENTORY_PATH}")


def append_readme_row(req: ClientScaffoldRequest, dry_run: bool) -> None:
    """Append project row to Upwork/README.md active projects table."""
    if not UPWORK_README.exists():
        print("  WARN: Upwork/README.md not found — skip README update")
        return

    project_path = f"projects/{req.slug}/"
    row = f"| `{project_path}` | {req.description or req.name} | _TBD — run gh repo create_ |"
    content = UPWORK_README.read_text(encoding="utf-8")

    if project_path in content:
        print(f"  README already lists {project_path}")
        return

    marker = "## Non-code folders"
    if marker not in content:
        print("  WARN: Could not find README table anchor — add row manually:")
        print(f"    {row}")
        return

    insertion = row + "\n"
    new_content = content.replace(marker, insertion + marker)

    if dry_run:
        print(f"  [dry-run] would append README row: {row}")
        return

    UPWORK_README.write_text(new_content, encoding="utf-8")
    print(f"  Updated {UPWORK_README}")


def parse_modules(raw: str) -> list[ClientModule]:
    if not raw.strip():
        return []
    parts = [p.strip().lower() for p in raw.split(",") if p.strip()]
    valid = {m.value for m in ClientModule}
    for p in parts:
        if p not in valid:
            raise argparse.ArgumentTypeError(
                f"Invalid module '{p}'. Choose from: {', '.join(sorted(valid))}"
            )
    return [ClientModule(p) for p in parts]


def main() -> int:
    parser = argparse.ArgumentParser(description="MAS four-pillar client scaffolder")
    parser.add_argument("--name", required=True, help="Client display name")
    parser.add_argument("--slug", required=True, help="Client slug (lowercase-hyphenated)")
    parser.add_argument(
        "--modules",
        default="",
        type=parse_modules,
        help="Comma-separated: web,automation,ai_agents",
    )
    parser.add_argument("--description", default="", help="Project description")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing")
    args = parser.parse_args()

    try:
        req = ClientScaffoldRequest(
            name=args.name,
            slug=args.slug,
            modules=args.modules,
            description=args.description,
        )
        result = scaffold(req, dry_run=args.dry_run)
        print(json.dumps(result.model_dump(), indent=2))
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
