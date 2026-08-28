#!/usr/bin/env python3
"""Scan SMS Backup & Restore XML exports for Upwork client contacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

DEFAULT_BACKUP_ROOT = Path("~/OneDrive - Height Consulting/Apps/SMS Backup and Restore/UpworkMsgs").expanduser()

# Map SMS contact_name → client bundle slug
CONTACT_TO_SLUG: dict[str, str] = {
    "Marc Walden": "turo",
    "HIRO": "openclaw",
    "Elijah Booker": "openclaw",
}


def scan_backup_root(root: Path, max_files: int | None = 20) -> dict:
    if not root.is_dir():
        return {"error": f"Path not found: {root}", "file_count": 0}

    xml_files = sorted(root.glob("*.xml"), key=lambda p: p.stat().st_mtime, reverse=True)
    file_count = len(xml_files)
    to_scan = xml_files if max_files is None else xml_files[:max_files]

    contacts: Counter[str] = Counter()
    addresses: Counter[str] = Counter()
    by_slug: Counter[str] = Counter()

    for f in to_scan:
        text = f.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r'contact_name="([^"]+)"', text):
            name = m.group(1)
            contacts[name] += 1
            slug = CONTACT_TO_SLUG.get(name)
            if slug:
                by_slug[slug] += 1
        for m in re.finditer(r'address="(\+?[0-9]+)"', text):
            addresses[m.group(1)] += 1

    latest = xml_files[0].stat().st_mtime if xml_files else 0
    from datetime import datetime, timezone

    return {
        "backup_root": str(root),
        "file_count": file_count,
        "files_scanned": len(to_scan),
        "latest_backup_mtime": datetime.fromtimestamp(latest, tz=timezone.utc).isoformat() if latest else None,
        "contacts": dict(contacts.most_common()),
        "addresses": dict(addresses.most_common(10)),
        "messages_by_client_slug": dict(by_slug),
        "contact_to_slug": CONTACT_TO_SLUG,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan Upwork SMS/XML message backups")
    parser.add_argument("--root", type=Path, default=DEFAULT_BACKUP_ROOT)
    parser.add_argument("--output", type=Path, help="Write JSON summary")
    args = parser.parse_args()

    result = scan_backup_root(args.root)
    print(json.dumps(result, indent=2))

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Wrote {args.output}")

    return 0 if "error" not in result else 1


if __name__ == "__main__":
    sys.exit(main())
