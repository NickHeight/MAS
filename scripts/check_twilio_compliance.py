#!/usr/bin/env python3
"""Print live Twilio TFV + A2P status for Coastal Lux Turo account."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_env import load_mas_env

TFV_SID = "HHf8191e7eac9b52f82dfe45a3d3eb8c13"
A2P_SID = "QE2c6890da8086d771620e9b13fadeba0b"
MS_SID = "MGc86b818348ae867b12c400ea7dac7f0d"
BRAND_SID = "BN43bc7501bde12f37d54f702692943e4b"


def _auth_header() -> str:
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    if not sid or not token:
        raise SystemExit("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN required (MAS .env)")
    return "Basic " + base64.b64encode(f"{sid}:{token}".encode()).decode()


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"Authorization": _auth_header()})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    load_mas_env()

    report: dict = {}
    try:
        report["tfv"] = _get(
            f"https://messaging.twilio.com/v1/Tollfree/Verifications/{TFV_SID}"
        )
    except urllib.error.HTTPError as exc:
        report["tfv_error"] = f"HTTP {exc.code}: {exc.read().decode()[:200]}"

    try:
        report["a2p"] = _get(
            f"https://messaging.twilio.com/v1/Services/{MS_SID}/Compliance/Usa2p/{A2P_SID}"
        )
    except urllib.error.HTTPError as exc:
        report["a2p_error"] = f"HTTP {exc.code}: {exc.read().decode()[:200]}"

    try:
        report["brand"] = _get(
            f"https://messaging.twilio.com/v1/a2p/BrandRegistrations/{BRAND_SID}"
        )
    except urllib.error.HTTPError as exc:
        report["brand_error"] = f"HTTP {exc.code}: {exc.read().decode()[:200]}"

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        tfv = report.get("tfv", {})
        a2p = report.get("a2p", {})
        print("=== Twilio Compliance Status ===")
        print(f"TFV status:     {tfv.get('status', report.get('tfv_error', 'unknown'))}")
        print(f"A2P status:     {a2p.get('campaign_status', report.get('a2p_error', 'unknown'))}")
        brand = report.get("brand", {})
        print(f"Brand status:   {brand.get('status', report.get('brand_error', 'unknown'))}")
        tfv_status = (tfv.get("status") or "").upper()
        if tfv_status in {"TWILIO_APPROVED", "APPROVED"}:
            print("ACTION: Enable S8 sms channel for Marc-only alerts")
        elif tfv_status in {"PENDING_REVIEW", "IN_REVIEW"}:
            print("ACTION: Still waiting — use email alerts today")
        elif "REJECT" in tfv_status:
            print("ACTION: Read rejection_reasons in --json output; resubmit per decision doc")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
