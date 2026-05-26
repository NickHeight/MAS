"""Inject a synthetic test contact into HubSpot.

Refuses to run unless DEPLOY_TARGET=nick-test. Tags every contact with
test_harness=true and test_run_id=<uuid> for later cleanup.

Usage:
    python inject_synthetic_lead.py --fixture fixtures/paragon-referral.json [--run-id UUID]
Prints JSON: {contact_id, contact_email, run_id} on success.
"""
import argparse
import json
import os
import sys
import uuid
import urllib.request


def assert_test_env():
    target = os.environ.get("DEPLOY_TARGET")
    if target != "nick-test":
        print(json.dumps({"error": "wrong_deploy_target", "details": "DEPLOY_TARGET must be nick-test, got " + repr(target)}), file=sys.stderr)
        sys.exit(2)


def hubspot_upsert(token, properties):
    payload = {
        "properties": properties,
        "idProperty": "email",
    }
    req = urllib.request.Request(
        "https://api.hubapi.com/crm/v3/objects/contacts",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 409:
            # Already exists - search by email and return the existing record
            search_body = {
                "filterGroups": [{"filters": [{"propertyName": "email", "operator": "EQ", "value": properties["email"]}]}],
                "properties": list(properties.keys()),
                "limit": 1,
            }
            sreq = urllib.request.Request(
                "https://api.hubapi.com/crm/v3/objects/contacts/search",
                data=json.dumps(search_body).encode("utf-8"),
                headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(sreq, timeout=15) as resp:
                results = json.loads(resp.read().decode("utf-8")).get("results", [])
                if results:
                    return results[0]
        raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--run-id", default=None)
    args = ap.parse_args()

    assert_test_env()

    token = os.environ.get("HUBSPOT_PRIVATE_APP_TOKEN")
    if not token:
        print(json.dumps({"error": "missing_env", "details": "HUBSPOT_PRIVATE_APP_TOKEN required"}), file=sys.stderr)
        sys.exit(2)

    run_id = args.run_id or str(uuid.uuid4())[:8]

    with open(args.fixture) as f:
        fixture = json.load(f)

    raw_lead = fixture["lead"]
    properties = {}
    for k, v in raw_lead.items():
        if isinstance(v, str):
            v = v.replace("{run_id}", run_id)
        properties[k] = v

    properties.setdefault("test_harness", "true")
    properties.setdefault("test_run_id", run_id)

    try:
        result = hubspot_upsert(token, properties)
    except Exception as exc:
        print(json.dumps({"error": "hubspot_upsert_failed", "details": str(exc)}), file=sys.stderr)
        sys.exit(3)

    out = {
        "contact_id": result.get("id"),
        "contact_email": properties["email"],
        "run_id": run_id,
        "fixture": args.fixture,
    }
    print(json.dumps(out))


if __name__ == "__main__":
    main()
