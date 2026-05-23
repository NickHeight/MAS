#!/usr/bin/env python3
"""Review SMS Backup & Restore XML for client contacts; suggest Monday.com items."""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scan_message_backups import CONTACT_TO_SLUG, DEFAULT_BACKUP_ROOT

MAS_ROOT = Path(__file__).resolve().parent.parent
AUDITS_DIR = MAS_ROOT / "llm_wiki" / "audits"

KEYWORD_RULES: list[tuple[str, str, str]] = [
    (r"stripe|payment|payout|invoice|refund|\$\d+", "Financials", "S7 / Stripe / QBO"),
    (r"twilio|sms|text message|a2p|tfv|toll.?free", "Infra", "Twilio compliance"),
    (r"quickbooks|qbo|intuit|chart of accounts|coa", "Financials", "QuickBooks"),
    (r"bouncie|gps|telemetry|odometer", "Infra", "Bouncie GPS"),
    (r"meta|facebook|instagram|ad campaign|gbp|google business", "MEO", "Meta / MEO"),
    (r"monday|asana|board|update", "Documentation", "PM sync"),
    (r"walkthrough|call|meeting|schedule", "Question", "Marc walkthrough"),
    (r"jet\s*ski|qr code|upsell|beach gear", "Decision", "Upsell catalog"),
    (r"stripe.*cancel|not getting paid|losing money", "Blocker", "Trust / payout loop"),
    (r"claude|ai|mcp", "Documentation", "Marc Claude + Monday onboarding"),
]

MONDAY_BOARD = {
    "turo": {
        "client_board_id": "18408242353",
        "client_board_name": "Coastal Lux — Development Portal",
        "cover_item_id": "11805693950",
    },
}


def _extract_body(el: ET.Element) -> str:
    body = (el.get("body") or "").strip()
    if body:
        return body
    for part in el.findall("parts/part"):
        text = (part.get("text") or "").strip()
        if text:
            return text.replace("&#10;", "\n")
    return ""


def parse_sms_messages(xml_path: Path, contact: str, since_ms: int | None = None) -> list[dict]:
    rows: list[dict] = []
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError:
        return rows

    for tag in ("sms", "mms"):
        for el in root.iter(tag):
            name = el.get("contact_name") or ""
            if name != contact:
                continue
            date_ms = int(el.get("date") or "0")
            if since_ms and date_ms < since_ms:
                continue
            body = _extract_body(el)
            msg_box = el.get("msg_box") or el.get("type") or "1"
            rows.append(
                {
                    "date_ms": date_ms,
                    "date_iso": datetime.fromtimestamp(date_ms / 1000, tz=timezone.utc).isoformat(),
                    "direction": "received" if msg_box == "1" else "sent",
                    "body": body,
                    "has_body": bool(body),
                    "kind": tag,
                    "source_file": xml_path.name,
                }
            )
    return rows


def classify_message(body: str) -> tuple[str, str] | None:
    if not body or len(body) < 8:
        return None
    lower = body.lower()
    for pattern, category, workflow in KEYWORD_RULES:
        if re.search(pattern, lower, re.I):
            return category, workflow
    if len(body) > 40:
        return "Question", "General client ask"
    return None


def suggest_items(messages: list[dict], slug: str) -> list[dict]:
    by_area: dict[str, dict] = {}
    for msg in sorted(messages, key=lambda m: m["date_ms"], reverse=True):
        if msg["direction"] != "received":
            continue
        hit = classify_message(msg["body"])
        if not hit:
            continue
        category, workflow = hit
        preview = msg["body"][:200].replace("\n", " ")
        if workflow not in by_area:
            by_area[workflow] = {
                "slug": slug,
                "suggested_title": f"[SMS] {workflow} — review Marc message",
                "category": category,
                "workflow_area": workflow,
                "suggested_status": "Pending Marc" if category in ("Decision", "Question", "Blocker") else "Pending Nick",
                "latest_message_date": msg["date_iso"],
                "message_preview": preview,
                "action": "Create new Monday item OR post update on cover item 11805693950",
                "monday_board_id": MONDAY_BOARD.get(slug, {}).get("client_board_id"),
            }
    return list(by_area.values())


def render_markdown_report(result: dict) -> str:
    lines = [
        "# SMS → Monday Suggestions",
        "",
        f"**Generated:** {result['generated_at']}",
        f"**Backup root:** `{result['backup_root']}`",
        f"**Window:** last {result['days']} days",
        "",
    ]
    for slug, block in result["by_client"].items():
        lines.append(f"## {slug}")
        lines.append("")
        lines.append(f"- Messages with body text: {block['messages_with_body']} / {block['messages_total']}")
        lines.append(f"- Board: `{block.get('client_board_name', block.get('monday_board_name', 'n/a'))}` (`{block.get('client_board_id', block.get('monday_board_id', ''))}`)")
        lines.append("")
        if not block["suggestions"]:
            lines.append("_No keyword-matched suggestions (MMS bodies often empty in exports)._")
            lines.append("")
            continue
        lines.append("| Workflow | Category | Status | Latest | Preview |")
        lines.append("|----------|----------|--------|--------|---------|")
        for s in block["suggestions"]:
            prev = s["message_preview"][:80].replace("|", "/")
            lines.append(
                f"| {s['workflow_area']} | {s['category']} | {s['suggested_status']} | {s['latest_message_date'][:10]} | {prev} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Agent next steps",
            "",
            "1. Cross-check each suggestion against `Turo/log.md` and `decisions/2026-05-22_monday_wiki_reconciliation.md`",
            "2. Post plain-text Monday updates (no HTML) on the matching item or create new items",
            "3. Append ingest note to `Turo/sources/marc_messages/index.md`",
            "",
        ]
    )
    return "\n".join(lines)


def run_review(backup_root: Path, days: int = 30, contacts: list[str] | None = None) -> dict:
    contacts = contacts or list(CONTACT_TO_SLUG.keys())
    since_ms = int((datetime.now(timezone.utc).timestamp() - days * 86400) * 1000)

    xml_files = sorted(backup_root.glob("*.xml"), key=lambda p: p.stat().st_mtime, reverse=True)
    # Full folder has 286+ large XMLs — scan latest 40 for body extraction
    xml_files = xml_files[:40]
    by_client: dict[str, dict] = {}

    for contact in contacts:
        slug = CONTACT_TO_SLUG.get(contact, "unknown")
        all_msgs: list[dict] = []
        seen: set[tuple] = set()
        for f in xml_files:
            for row in parse_sms_messages(f, contact, since_ms=since_ms):
                key = (row["date_ms"], row["body"][:80], row["direction"])
                if key in seen:
                    continue
                seen.add(key)
                all_msgs.append(row)

        with_body = [m for m in all_msgs if m["has_body"]]
        suggestions = suggest_items(with_body, slug) if slug != "unknown" else []
        board = MONDAY_BOARD.get(slug, {})
        by_client[slug] = {
            "contact": contact,
            "messages_total": len(all_msgs),
            "messages_with_body": len(with_body),
            "recent_with_body": with_body[:20],
            "suggestions": suggestions,
            **board,
        }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "backup_root": str(backup_root),
        "days": days,
        "by_client": by_client,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Suggest Monday items from SMS backups")
    parser.add_argument("--root", type=Path, default=DEFAULT_BACKUP_ROOT)
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--output-json", type=Path, default=AUDITS_DIR / "monday_suggestions_from_sms.json")
    parser.add_argument("--output-md", type=Path, default=AUDITS_DIR / "monday_suggestions_from_sms.md")
    parser.add_argument("--wiki-copy", type=Path, help="Also write markdown to wiki path")
    args = parser.parse_args()

    result = run_review(args.root, days=args.days)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    md = render_markdown_report(result)
    args.output_md.write_text(md, encoding="utf-8")
    if args.wiki_copy:
        args.wiki_copy.parent.mkdir(parents=True, exist_ok=True)
        args.wiki_copy.write_text(
            "---\ntags: [turo, monday, sms, suggestions]\nupdated: "
            + datetime.now(timezone.utc).strftime("%Y-%m-%d")
            + "\n---\n\n"
            + md,
            encoding="utf-8",
        )

    print(json.dumps({k: v for k, v in result.items() if k != "by_client"}, indent=2))
    for slug, block in result["by_client"].items():
        print(f"  {slug}: {block['messages_with_body']} bodies, {len(block['suggestions'])} suggestions")
    print(f"Wrote {args.output_json}")
    print(f"Wrote {args.output_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
