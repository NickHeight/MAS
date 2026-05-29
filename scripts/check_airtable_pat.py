#!/usr/bin/env python3
"""Verify Airtable PAT is valid."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_env import load_mas_env

COASTAL_BASE_ID = "appRYppT9D6TUtypr"


def main() -> int:
    load_mas_env()
    pat = os.environ.get("AIRTABLE_PAT")
    if not pat:
        raise SystemExit("AIRTABLE_PAT not set — check Netlify env or MAS .env")

    req = urllib.request.Request(
        "https://api.airtable.com/v0/meta/bases",
        headers={"Authorization": f"Bearer {pat}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        print(f"FAIL — HTTP {exc.code}: {exc.read().decode()[:200]}")
        return 1

    bases = data.get("bases", [])
    coastal = [b for b in bases if b.get("id") == COASTAL_BASE_ID]
    print(f"OK — {len(bases)} bases visible")
    print(f"Coastal Lux base present: {bool(coastal)}")
    if not coastal:
        print("WARN: appRYppT9D6TUtypr not in token scope")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
