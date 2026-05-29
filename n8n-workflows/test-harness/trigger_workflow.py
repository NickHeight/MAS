"""Trigger an n8n workflow execution via REST.

Two modes:
  webhook: POST to /webhook/<path> (workflow must have a Webhook trigger)
  manual:  POST to /api/v1/workflows/{id}/execute (works for any workflow)

Usage:
    python trigger_workflow.py --workflow-id paragon-tax--referral-request --payload payload.json
    python trigger_workflow.py --webhook-path twilio-inbound --payload payload.json --mode webhook
Prints execution result JSON.
"""
import argparse
import json
import os
import sys
import urllib.request


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow-id", default=None, help="n8n internal workflow id OR our `id` field")
    ap.add_argument("--webhook-path", default=None)
    ap.add_argument("--mode", default="manual", choices=["manual", "webhook"])
    ap.add_argument("--payload", required=True, help="Path to JSON file with the trigger payload")
    args = ap.parse_args()

    base = os.environ.get("N8N_BASE_URL")
    if not base:
        print(json.dumps({"error": "missing_env", "details": "N8N_BASE_URL required"}), file=sys.stderr)
        sys.exit(2)

    with open(args.payload) as f:
        body = json.load(f)

    if args.mode == "webhook":
        if not args.webhook_path:
            print(json.dumps({"error": "bad_args", "details": "--webhook-path required for webhook mode"}), file=sys.stderr)
            sys.exit(2)
        url = base.rstrip("/") + "/webhook/" + args.webhook_path.lstrip("/")
        headers = {"Content-Type": "application/json"}
    else:
        if not args.workflow_id:
            print(json.dumps({"error": "bad_args", "details": "--workflow-id required for manual mode"}), file=sys.stderr)
            sys.exit(2)
        api_key = os.environ.get("N8N_API_KEY")
        if not api_key:
            print(json.dumps({"error": "missing_env", "details": "N8N_API_KEY required for manual mode"}), file=sys.stderr)
            sys.exit(2)
        url = base.rstrip("/") + "/api/v1/workflows/" + args.workflow_id + "/execute"
        headers = {"Content-Type": "application/json", "X-N8N-API-KEY": api_key}

    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = resp.read().decode("utf-8")
    except Exception as exc:
        print(json.dumps({"error": "trigger_failed", "details": str(exc), "url": url}), file=sys.stderr)
        sys.exit(3)

    try:
        result = json.loads(payload)
    except json.JSONDecodeError:
        result = {"raw": payload}

    print(json.dumps({"triggered": True, "url": url, "result": result}, indent=2))


if __name__ == "__main__":
    main()
