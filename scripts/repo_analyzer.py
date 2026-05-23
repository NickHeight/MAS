#!/usr/bin/env python3
"""Audit legacy client repos and propose migration to MAS standard layout."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import load_env  # noqa: F401 — loads MAS .env into os.environ

from models import MigrationPlan, ProposedMove

SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".next",
    "dist",
    "build",
    ".cursor",
}

KEY_CONFIG_NAMES = {
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "CLAUDE.md",
    "README.md",
    "docker-compose.yml",
    ".env.example",
}

BLUEPRINT_SUFFIXES = (".blueprint.json", ".json")

HEURISTIC_RULES: list[tuple[str, str, str]] = [
    (r"n8n|workflow|automation|make", "automation_workflows/", "automation"),
    (r"web|frontend|backend|src|app|pages|components", "web_development/", "web"),
    (r"agent|hermes|prompt|core", "ai_agents/", "ai_agents"),
    (r"brief|chat|upwork|scope", "communications_history/briefs/", "communications"),
    (r"monday|pm|task", "communications_history/monday_logs/", "communications"),
    (r"doc|plan|architecture|guide", "docs/", "docs"),
    (r"test|spec", "tests/", "tests"),
    (r"script|util", "scripts/", "scripts"),
]


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def map_tree(root: Path, max_depth: int = 8) -> list[str]:
    lines: list[str] = []
    root = root.resolve()

    def walk(current: Path, prefix: str = "", depth: int = 0) -> None:
        if depth > max_depth or should_skip(current):
            return
        try:
            entries = sorted(current.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except PermissionError:
            lines.append(f"{prefix}[permission denied]")
            return
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            branch = "└── " if is_last else "├── "
            lines.append(f"{prefix}{branch}{entry.name}{'/' if entry.is_dir() else ''}")
            if entry.is_dir() and not should_skip(entry):
                extension = "    " if is_last else "│   "
                walk(entry, prefix + extension, depth + 1)

    lines.append(f"{root.name}/")
    walk(root)
    return lines


def collect_key_files(root: Path, limit: int = 30) -> dict[str, str]:
    collected: dict[str, str] = {}
    for path in root.rglob("*"):
        if should_skip(path) or not path.is_file():
            continue
        rel = str(path.relative_to(root)).replace("\\", "/")
        name = path.name
        is_blueprint = name.endswith(BLUEPRINT_SUFFIXES) and "blueprint" in name.lower()
        if name in KEY_CONFIG_NAMES or is_blueprint:
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
                collected[rel] = content[:4000]
            except OSError:
                continue
        if len(collected) >= limit:
            break
    return collected


def heuristic_classify(rel_path: str) -> tuple[str, str] | None:
    import re

    lower = rel_path.lower().replace("\\", "/")
    for pattern, dest, module in HEURISTIC_RULES:
        if re.search(pattern, lower):
            filename = Path(rel_path).name
            return f"{dest.rstrip('/')}/{filename}", module
    return None


def build_heuristic_plan(root: Path) -> MigrationPlan:
    proposed: list[ProposedMove] = []
    unmapped: list[str] = []
    risks: list[str] = []

    for path in root.rglob("*"):
        if should_skip(path) or not path.is_file():
            continue
        rel = str(path.relative_to(root)).replace("\\", "/")
        if rel.startswith("docs/") and path.name in KEY_CONFIG_NAMES:
            continue
        match = heuristic_classify(rel)
        if match:
            dest, module = match
            proposed.append(
                ProposedMove(
                    source=rel,
                    destination=dest,
                    module=module,
                    reason=f"Heuristic match for module '{module}'",
                )
            )
        else:
            unmapped.append(rel)

    if len(unmapped) > 50:
        risks.append(f"{len(unmapped)} files could not be auto-mapped — manual review required")
    if any("node_modules" in p for p in unmapped):
        risks.append("Some paths may reference dependencies outside scan scope")

    return MigrationPlan(
        source_path=str(root.resolve()),
        analyzed_at=datetime.now(timezone.utc).isoformat(),
        proposed_moves=proposed,
        risks=risks or ["Heuristic analysis may miss edge cases — review before apply"],
        unmapped_files=unmapped[:100],
        approval_required=True,
        analysis_method="heuristic",
    )


def analyze_with_gemini(root: Path, tree: list[str], key_files: dict[str, str]) -> MigrationPlan:
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY or GEMINI_API_KEY not set")

    try:
        import google.generativeai as genai
    except ImportError as e:
        raise RuntimeError("Install google-generativeai: pip install google-generativeai") from e

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""Analyze this legacy client repository and propose migration to MAS standard layout.

Standard modules:
- web_development/ (frontend/backend)
- automation_workflows/n8n_nodes/ and make_scenarios/ (n8n/Make.com)
- ai_agents/ (custom agent code)
- communications_history/briefs/ and monday_logs/
- docs/, scripts/, tests/, config/

Directory tree:
{chr(10).join(tree[:500])}

Key config file excerpts:
{json.dumps(key_files, indent=2)[:12000]}

Return ONLY valid JSON matching this schema:
{{
  "proposed_moves": [{{"source": "path", "destination": "path", "module": "web|automation|ai_agents|communications|docs|scripts|tests", "reason": "why"}}],
  "risks": ["list of risks"],
  "unmapped_files": ["paths that need manual decision"]
}}
"""

    response = model.generate_content(prompt)
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    data = json.loads(text)
    moves = [ProposedMove(**m) for m in data.get("proposed_moves", [])]

    return MigrationPlan(
        source_path=str(root.resolve()),
        analyzed_at=datetime.now(timezone.utc).isoformat(),
        proposed_moves=moves,
        risks=data.get("risks", []),
        unmapped_files=data.get("unmapped_files", []),
        approval_required=True,
        analysis_method="gemini",
    )


def apply_plan(root: Path, plan: MigrationPlan, dry_run: bool) -> None:
    if plan.approval_required:
        print("\nWARNING: Migration requires explicit approval. Use --apply to execute moves.\n")

    for move in plan.proposed_moves:
        src = root / move.source
        dest = root / move.destination
        if not src.exists():
            print(f"  SKIP (missing): {move.source}")
            continue
        if dry_run:
            print(f"  [dry-run] would move: {move.source} -> {move.destination}")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            src.rename(dest)
            print(f"  MOVED: {move.source} -> {move.destination}")


def main() -> int:
    parser = argparse.ArgumentParser(description="MAS legacy repo analyzer")
    parser.add_argument("--path", required=True, type=Path, help="Legacy repo path to analyze")
    parser.add_argument("--output", type=Path, help="Write migration plan JSON here")
    parser.add_argument("--use-gemini", action="store_true", help="Use Gemini API for analysis")
    parser.add_argument("--apply", action="store_true", help="Apply approved migration moves")
    parser.add_argument("--dry-run", action="store_true", help="Print apply actions without moving")
    args = parser.parse_args()

    root = args.path.expanduser().resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        return 1

    print(f"Analyzing: {root}\n")
    tree = map_tree(root)
    key_files = collect_key_files(root)

    try:
        if args.use_gemini:
            plan = analyze_with_gemini(root, tree, key_files)
        else:
            plan = build_heuristic_plan(root)
    except RuntimeError as e:
        print(f"Gemini unavailable ({e}), falling back to heuristic analysis")
        plan = build_heuristic_plan(root)

    output_json = json.dumps(plan.model_dump(), indent=2)
    print(output_json)

    if args.output:
        if args.dry_run:
            print(f"\n[dry-run] would write plan to: {args.output}")
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output_json, encoding="utf-8")
            print(f"\nPlan written to: {args.output}")

    if args.apply:
        if not args.dry_run:
            confirm = input("\nType 'APPROVE' to apply migration moves: ")
            if confirm.strip() != "APPROVE":
                print("Aborted.")
                return 1
        apply_plan(root, plan, dry_run=args.dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())
