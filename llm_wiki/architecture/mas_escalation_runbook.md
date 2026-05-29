# MAS Escalation Runbook

Updated: 2026-05-26

## Purpose

MAS needs a reliable way to wake Nick when an agent hits a true human gate: credentials, OAuth, billing, destructive actions, client-facing pushes, or production incidents. The escalation layer is intentionally local-first and env-driven so it can be called from Claude Code loops, hooks, n8n, or Katya without putting secrets in git.

## Files

| Path | Purpose |
|---|---|
| `scripts/alert_escalator.py` | CLI for Slack, Twilio SMS, and Twilio Voice escalation. |
| `scripts/alert_ack_server.py` | Optional local ACK webhook for `ACK`, `DONE`, or `STOP` replies. |
| `config/alert_profiles.example.json` | Reusable project profiles and call cadence policies. |
| `templates/katya/upwork_pre_contract.md` | Upwork-safe pre-contract Katya reply. |
| `templates/katya/upwork_post_contract.md` | Post-contract Katya reply with scheduling/callback options. |

## Secret Handling

Never commit secret values. Set these in the shell, service manager, n8n host, or OS secret store:

| Env var | Required for | Notes |
|---|---|---|
| `SLACK_WEBHOOK_URL` | Slack webhook alerts | Easiest Slack path. |
| `SLACK_BOT_TOKEN` + `SLACK_CHANNEL` | Slack API alerts | Alternative to webhook. |
| `TWILIO_ACCOUNT_SID` | SMS and voice | Height/Katya scope only for Nick-side workflows. |
| `TWILIO_AUTH_TOKEN` | SMS and voice | Do not share with Bentley/HIRO scope. |
| `TWILIO_FROM_NUMBER` | SMS and voice | E.164 format. |
| `ALERT_NICK_PHONE` | SMS and voice | E.164 format. |

## Alert Profiles

Profiles live in `config/alert_profiles.example.json`.

| Profile | Channels | Call behavior |
|---|---|---|
| `mas-default` | Slack + SMS | No calls. |
| `upwork-p0` | Slack + SMS + voice | 5 attempts, every 2 minutes. |
| `client-prod` | Slack + SMS + voice | 10 attempts, every 90 seconds. |
| `personal-critical` | Slack + SMS + voice | 15 attempts, every 60 seconds. |

The profile is selected at runtime. Do not hardcode one cadence globally; the right level of aggression depends on project risk.

## Dry Run

Use dry-run first:

```powershell
python scripts/alert_escalator.py --profile mas-default trigger `
  --project MAS `
  --severity p0 `
  --title "Agent blocked" `
  --body "Claude session hit an OAuth gate and needs Nick." `
  --agent "orchestrator" `
  --incident-id "mas-test-001" `
  --dry-run
```

## Real Alert

After env vars are set:

```powershell
python scripts/alert_escalator.py --profile upwork-p0 trigger `
  --project Upwork `
  --severity p0 `
  --title "New client message needs Nick" `
  --body "Katya received a client message that needs human review." `
  --agent "katya" `
  --incident-id "upwork-20260526-001"
```

## Manual ACK

Any operator can stop a repeated voice loop from the same machine:

```powershell
python scripts/alert_escalator.py --profile upwork-p0 ack upwork-20260526-001 --source manual
```

The ACK state file defaults to `.mas/alerts/acks.json`. That path should remain local runtime state, not a committed artifact.

## SMS / Webhook ACK

Start the local ACK server:

```powershell
python scripts/alert_ack_server.py --host 127.0.0.1 --port 8765
```

Then expose it with a tunnel if needed and point Twilio inbound SMS to it. Supported bodies:

```text
ACK upwork-20260526-001
DONE upwork-20260526-001
STOP upwork-20260526-001
```

If a single incident is active, the server can be started with:

```powershell
python scripts/alert_ack_server.py --default-incident-id upwork-20260526-001
```

Then a plain `ACK` body will stop that incident.

## Cost Notes

As of the 2026-05-26 check, Twilio US outbound Programmable Voice is roughly $0.014/minute, with some destinations higher. SMS cost depends on number type, registration, and destination. The expensive part is not the wake-up calls themselves; it is accidentally creating an infinite loop. Always use capped profiles and ACK state.

## Upwork / Katya Rules

Pre-contract Upwork communication must stay inside Upwork. Katya must not send or request:

- Phone numbers
- Email addresses
- Calendly links
- Slack, Telegram, Zoom, Google Meet, or other external contact details
- Any instruction to communicate outside Upwork

Use `templates/katya/upwork_pre_contract.md` before a contract starts.

After a contract/workroom is active, use `templates/katya/upwork_post_contract.md` when scheduling/callback options are appropriate.

## MAS Loop Integration

When an agent loop detects a true blocker:

1. Mark the task as blocked in `TASKS.md` or the relevant Monday item.
2. Trigger `alert_escalator.py` with the appropriate profile.
3. Continue to the next runnable offline task.
4. Do not sit idle waiting for Nick unless no runnable work remains.

Example:

```powershell
python scripts/alert_escalator.py --profile client-prod trigger `
  --project Turo `
  --severity p0 `
  --title "Stripe webhook blocked by credential gate" `
  --body "Agent needs Nick to complete OAuth before it can register the webhook." `
  --agent "backend-lead" `
  --incident-id "turo-stripe-oauth-20260526"
```

## Failure Modes

| Failure | Response |
|---|---|
| Missing Slack env vars | CLI returns an error for Slack but still attempts other configured channels. |
| Missing Twilio env vars | CLI returns an error for SMS/voice. Use dry-run to validate shape first. |
| ACK state corrupted | CLI treats it as empty state and rewrites a valid JSON file on next ACK. |
| Infinite call risk | Avoid profiles without `max_attempts`; this implementation requires a cap. |
| Upwork pre-contract external contact temptation | Use the pre-contract template only; save the stronger message for post-contract. |

