"""Fetch a HubSpot contact + assert its properties match expected state.

Expected-state DSL:
  literal value: must match exactly
  string '{any_iso_within_60s}': value must be ISO8601 within 60s of now
  string '{not_null}': value must be present and non-empty
  list under key 'expected_state_after_any_of': contact must satisfy at least one variant

Usage:
    python assert_state.py --contact-id 12345 --fixture fixtures/paragon-referral.json
Exits 0 on pass, 1 on assertion fail, 2 on env/setup error.
"""
import argparse
import datetime
import json
import os
import sys
import urllib.request


def fetch_contact(token, contact_id, properties):
    qs = "?properties=" + ",".join(properties)
    url = "https://api.hubapi.com/crm/v3/objects/contacts/" + str(contact_id) + qs
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def assert_one_state(actual_props, expected):
    diffs = []
    now = datetime.datetime.now(datetime.timezone.utc)
    for k, want in expected.items():
        got = actual_props.get(k)
        if want == "{not_null}":
            if not got:
                diffs.append({"key": k, "expected": "non-empty", "got": got})
            continue
        if want == "{any_iso_within_60s}":
            try:
                got_dt = datetime.datetime.fromisoformat(got.replace("Z", "+00:00"))
                delta = abs((now - got_dt).total_seconds())
                if delta > 60:
                    diffs.append({"key": k, "expected": "iso within 60s", "got": got, "delta_seconds": delta})
            except (AttributeError, ValueError):
                diffs.append({"key": k, "expected": "iso within 60s", "got": got, "details": "unparseable"})
            continue
        if str(got) != str(want):
            diffs.append({"key": k, "expected": want, "got": got})
    return diffs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contact-id", required=True)
    ap.add_argument("--fixture", required=True)
    args = ap.parse_args()

    token = os.environ.get("HUBSPOT_PRIVATE_APP_TOKEN")
    if not token:
        print(json.dumps({"error": "missing_env", "details": "HUBSPOT_PRIVATE_APP_TOKEN required"}), file=sys.stderr)
        sys.exit(2)

    with open(args.fixture) as f:
        fixture = json.load(f)

    variants = []
    if "expected_state_after_any_of" in fixture:
        variants = fixture["expected_state_after_any_of"]
    elif "expected_state_after" in fixture:
        variants = [fixture["expected_state_after"]]
    else:
        print(json.dumps({"error": "bad_fixture", "details": "missing expected_state_after or expected_state_after_any_of"}), file=sys.stderr)
        sys.exit(2)

    all_keys = sorted({k for v in variants for k in v.keys()})
    try:
        contact = fetch_contact(token, args.contact_id, all_keys)
    except Exception as exc:
        print(json.dumps({"error": "hubspot_fetch_failed", "details": str(exc)}), file=sys.stderr)
        sys.exit(3)

    props = contact.get("properties", {})

    best = None
    for v in variants:
        diffs = assert_one_state(props, v)
        if not diffs:
            best = {"matched": v, "diffs": []}
            break
        if best is None or len(diffs) < len(best["diffs"]):
            best = {"matched_partially": v, "diffs": diffs}

    if not best["diffs"]:
        print(json.dumps({"status": "PASS", "contact_id": args.contact_id, "matched": best.get("matched")}, indent=2))
        sys.exit(0)
    else:
        print(json.dumps({"status": "FAIL", "contact_id": args.contact_id, "best_match": best, "actual_properties": props}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
