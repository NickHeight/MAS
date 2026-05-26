"""Delete all HubSpot contacts with test_harness=true.

Safety guard: refuses unless DEPLOY_TARGET=nick-test.
"""
import json
import os
import sys
import urllib.request


def main():
    if os.environ.get("DEPLOY_TARGET") != "nick-test":
        print(json.dumps({"error": "wrong_deploy_target", "details": "DEPLOY_TARGET must be nick-test"}), file=sys.stderr)
        sys.exit(2)

    token = os.environ.get("HUBSPOT_PRIVATE_APP_TOKEN")
    if not token:
        print(json.dumps({"error": "missing_env", "details": "HUBSPOT_PRIVATE_APP_TOKEN required"}), file=sys.stderr)
        sys.exit(2)

    search_body = {
        "filterGroups": [{"filters": [{"propertyName": "test_harness", "operator": "EQ", "value": "true"}]}],
        "properties": ["email", "test_run_id"],
        "limit": 100,
    }
    sreq = urllib.request.Request(
        "https://api.hubapi.com/crm/v3/objects/contacts/search",
        data=json.dumps(search_body).encode("utf-8"),
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(sreq, timeout=15) as resp:
            results = json.loads(resp.read().decode("utf-8")).get("results", [])
    except Exception as exc:
        print(json.dumps({"error": "hubspot_search_failed", "details": str(exc)}), file=sys.stderr)
        sys.exit(3)

    deleted = []
    for c in results:
        cid = c["id"]
        dreq = urllib.request.Request(
            "https://api.hubapi.com/crm/v3/objects/contacts/" + cid,
            headers={"Authorization": "Bearer " + token},
            method="DELETE",
        )
        try:
            with urllib.request.urlopen(dreq, timeout=15) as resp:
                if 200 <= resp.status < 300:
                    deleted.append({"id": cid, "email": c.get("properties", {}).get("email")})
        except Exception as exc:
            print(json.dumps({"warning": "delete_failed", "id": cid, "details": str(exc)}), file=sys.stderr)

    print(json.dumps({"deleted": len(deleted), "contacts": deleted}, indent=2))


if __name__ == "__main__":
    main()
