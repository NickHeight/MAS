# n8n-workflows test harness

Synthetic-lead test harness for validating the three-business outreach engine
without touching real leads. Use against `nick-test` deployment target only.

## What it does

End-to-end loop for each sequence:

1. Inject a synthetic contact into HubSpot (test environment) with the
   property shape the sequence expects.
2. Trigger the n8n sequence workflow via its webhook URL (or via
   `executeWorkflow` REST call) with a fixture payload.
3. Wait for the execution to finish.
4. Fetch the contact's properties back from HubSpot and assert that the
   expected state transition happened (e.g. `paragon_referral_step` went
   from 0 to 1, `paragon_referral_state = "active"`, etc.).
5. Print pass/fail with a diff if assertion failed.

## Files

| Path | Purpose |
|---|---|
| `fixtures/*.json` | Synthetic lead payloads, one per sequence type |
| `inject_synthetic_lead.py` | Upsert a contact into HubSpot (test mode tagging) |
| `trigger_workflow.py` | POST to an n8n workflow webhook or call its executeWorkflow ID |
| `assert_state.py` | Fetch HubSpot contact + diff against expected state |
| `run_e2e.sh` | Orchestrator: inject -> trigger -> wait -> assert |
| `cleanup_test_contacts.py` | Delete contacts tagged `test_harness=true` |

## Required env

| Var | Purpose |
|---|---|
| `HUBSPOT_PRIVATE_APP_TOKEN` | Test-environment HubSpot Private App token |
| `N8N_BASE_URL` | e.g. `http://localhost:5678` |
| `N8N_API_KEY` | n8n PAT |
| `DEPLOY_TARGET` | Must be `nick-test` (asserts environment to prevent prod hits) |

## Safety guards

- All synthetic contacts get tagged `test_harness=true` + `test_run_id=<uuid>`
  on creation. `cleanup_test_contacts.py` only deletes contacts matching
  this tag — never touches real records.
- `inject_synthetic_lead.py` refuses to run if `DEPLOY_TARGET != "nick-test"`.
- Fixtures use email pattern `test-<uuid>@n8n-harness.invalid` so production
  email sends to test contacts would bounce. Use a non-routable domain in
  your test creds for extra safety.

## Run

```bash
export DEPLOY_TARGET=nick-test
export HUBSPOT_PRIVATE_APP_TOKEN=...
export N8N_BASE_URL=http://localhost:5678
export N8N_API_KEY=...

bash run_e2e.sh paragon-tax--referral-request
bash run_e2e.sh hh-insurance--qualification-router
```

## Next iterations (not in v0.1)

- Parallel runner that exercises all 19 sequences at once
- Capture-and-replay: dump real anonymized leads as fixtures for regression tests
- Latency budget assertions (sequence step end-to-end < N seconds)
- Bentley HTTP mock so qualification-router can be tested without Bentley running
