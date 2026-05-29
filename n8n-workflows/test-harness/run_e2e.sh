#!/usr/bin/env bash
# Orchestrator: inject -> trigger -> wait -> assert -> report.
# Usage: bash run_e2e.sh paragon-tax--referral-request

set -euo pipefail

WORKFLOW_ID="${1:-}"
if [ -z "$WORKFLOW_ID" ]; then
  echo "usage: $0 <workflow_id>" >&2
  exit 2
fi

if [ "${DEPLOY_TARGET:-}" != "nick-test" ]; then
  echo "ERROR: DEPLOY_TARGET must be nick-test (got: ${DEPLOY_TARGET:-unset})" >&2
  exit 2
fi

cd "$(dirname "$0")"

# Map workflow_id -> fixture
case "$WORKFLOW_ID" in
  paragon-tax--referral-request)      FIXTURE=fixtures/paragon-referral.json ;;
  paragon-tax--new-lead-outreach)     FIXTURE=fixtures/paragon-new-lead.json ;;
  hh-insurance--qualification-router) FIXTURE=fixtures/hh-insurance-qualification.json ;;
  hh-consulting--referral-request)    FIXTURE=fixtures/hh-consulting-investor.json ;;
  *) echo "ERROR: no fixture mapped for $WORKFLOW_ID" >&2; exit 2 ;;
esac

echo "==> Injecting synthetic contact (fixture=$FIXTURE)"
INJECT_OUT=$(python inject_synthetic_lead.py --fixture "$FIXTURE")
echo "$INJECT_OUT"
CONTACT_ID=$(echo "$INJECT_OUT" | python -c "import sys,json; print(json.load(sys.stdin)['contact_id'])")
CONTACT_EMAIL=$(echo "$INJECT_OUT" | python -c "import sys,json; print(json.load(sys.stdin)['contact_email'])")
RUN_ID=$(echo "$INJECT_OUT" | python -c "import sys,json; print(json.load(sys.stdin)['run_id'])")

# Build trigger payload from fixture, substituting contact_id and run_id
TRIGGER_PAYLOAD=$(mktemp)
python -c "
import json, sys
fixture = json.load(open('$FIXTURE'))
payload = fixture.get('trigger_input', {})
def sub(v):
    if isinstance(v, str):
        v = v.replace('{hubspot_contact_id}', '$CONTACT_ID').replace('{run_id}', '$RUN_ID')
    return v
def walk(o):
    if isinstance(o, dict): return {k: walk(sub(v)) for k, v in o.items()}
    if isinstance(o, list): return [walk(sub(v)) for v in o]
    return sub(o)
json.dump(walk(payload), open('$TRIGGER_PAYLOAD', 'w'))
"
echo "==> Trigger payload:"
cat "$TRIGGER_PAYLOAD"
echo

echo "==> Triggering workflow $WORKFLOW_ID"
python trigger_workflow.py --workflow-id "$WORKFLOW_ID" --payload "$TRIGGER_PAYLOAD" || {
  echo "TRIGGER FAILED" >&2
  exit 4
}

echo "==> Waiting 5s for execution to complete and HubSpot to settle..."
sleep 5

echo "==> Asserting state on contact $CONTACT_ID"
if python assert_state.py --contact-id "$CONTACT_ID" --fixture "$FIXTURE"; then
  echo "==> PASS"
  rm -f "$TRIGGER_PAYLOAD"
  exit 0
else
  echo "==> FAIL (contact $CONTACT_ID retained for inspection)" >&2
  echo "==> Cleanup with: DEPLOY_TARGET=nick-test python cleanup_test_contacts.py" >&2
  rm -f "$TRIGGER_PAYLOAD"
  exit 1
fi
