# n8n Workflows — Three-Business Outreach Automation

Pulled out of the Hermes/Bentley runtime, rebuilt as a portable n8n workflow set.

## Why this exists

Two reasons:

1. **Operational resilience for HIRO.** Bentley dying right now means every outreach sequence stops. With n8n owning orchestration, Bentley becomes a monitor instead of a single point of failure.
2. **Productization.** This is also Nick's internal template. Built generically with env-var-driven business config — drop a new `.env`, drop in a new copy library, get a working three-business outreach engine for any client.

## Architecture (Path A — n8n owns orchestration, Bentley owns AI)

```
┌─────────────┐         ┌─────────────────┐         ┌──────────┐
│  Triggers   │  ────▶  │  n8n workflows  │  ────▶  │ Channels │
│  (cron,     │         │  (orchestration)│         │ (Twilio, │
│   webhook,  │         │                 │         │  Gmail,  │
│   webhook)  │         │                 │         │  Social) │
└─────────────┘         └────────┬────────┘         └──────────┘
                                 │
                                 │ HTTP call for AI bits only
                                 ▼
                        ┌─────────────────┐
                        │  Bentley HTTP   │
                        │  (copy gen,     │
                        │   qualification │
                        │   brand voice)  │
                        └─────────────────┘
```

n8n handles deterministic logic: scheduling, state transitions, send/receive, retries. Bentley handles agentic logic: generating copy in the right brand voice, ambiguous lead qualification, conversational walkthroughs (HubSpot onboarding etc.).

Each n8n workflow can call Bentley via HTTP at any step. Bentley's response comes back as data in the n8n execution context.

## Directory layout

| Path | Purpose |
|------|---------|
| `lib/` | Reusable sub-workflows. Called via `Execute Workflow` node from sequence workflows. |
| `paragon-tax/` | Six sequence workflows for Paragon Tax (CPA services). |
| `hh-insurance/` | Seven sequence workflows for HH Insurance (life insurance / IUL). |
| `hh-consulting/` | Six sequence workflows for HH Consulting (real estate investor ops). |
| `inbound/` | Webhook receivers — Calendly, Twilio SMS inbound, HubSpot CRM events. |
| `cron/` | Daily/hourly scheduled triggers — morning briefing, social monitor, sequence-step advancer. |

## Sequence state model

n8n workflows are stateless between executions. We persist state on the **HubSpot contact record**, not in n8n.

For each sequence type, the contact carries:

| Property | Type | Example |
|----------|------|---------|
| `<sequence>_enrolled_at` | datetime | `2026-05-26T14:30:00Z` |
| `<sequence>_step` | integer | `0` (just enrolled) → `N` (complete) |
| `<sequence>_last_action_at` | datetime | last touch |
| `<sequence>_state` | enum | `active`, `paused`, `completed`, `opted_out` |

Each sequence has a daily **tick cron** (in `cron/<sequence>-tick.json`) that:
1. Queries HubSpot for contacts where `state=active` AND `now - last_action_at >= step_interval`
2. For each ripe contact, calls the sequence workflow with the current step
3. Sequence workflow executes the step (send SMS/email, update tags), increments step, updates `last_action_at`

This is simpler than n8n's wait nodes (which keep executions open for days, can't survive restarts cleanly).

## Templating model (for cross-client reuse)

All business-specific config lives in `.env`:

```bash
# Business identity
BUSINESS_UNIT=paragon_tax            # paragon_tax | hh_insurance | hh_consulting | <new>
BRAND_NAME="Paragon Tax"
BRAND_VOICE=trusted-advisor          # trusted-advisor | wealth-partner | investor-ops | <new>

# Channels
TWILIO_FROM_NUMBER=+18329812132
GMAIL_FROM_ALIAS=hiro@hhinsurance.info

# CRM
HUBSPOT_PIPELINE_ID=...
HUBSPOT_DEAL_STAGE_WON=...

# AI handler
BENTLEY_HTTP_URL=http://localhost:8081/v1/chat
BENTLEY_HTTP_TOKEN=...

# Compliance
A2P_BRAND_ID=...
A2P_CAMPAIGN_ID=...
```

Sequence workflows reference env vars exclusively. Copy libraries are passed in as separate JSON blobs per business (in `lib/copy-library/<business>.json`) so the n8n nodes themselves are identical across clients.

## Deployment

Two target environments:

- **`nick-test/`** — Nick's own n8n instance for testing. Synthetic leads only.
- **`hiro-prod/`** — Hiro's Mac Mini n8n instance. Real production.

Same workflow JSONs deploy to both — just different `.env`.

## Status / progress

See Monday board **HIRO / Bentley — Internal Build & Ops** (`18414790992`), group `⚙️ n8n Migration — Build & Template`. Six weekly milestones.

## Next session pickup

If picking this up cold:
1. Read this README.
2. Check Monday board for current week status.
3. Look at `lib/` first — sub-workflows are the foundation, sequences just compose them.
4. Look at `paragon-tax/referral-request.json` as the simplest reference sequence end-to-end.
5. Look at `cron/sequence-tick.json` as the reference for how sequences get advanced.
