# Required environment variables

These need to be set in the n8n host environment (or in n8n credential records, where noted). Values are placeholders — fill at deploy time.

## Business identity

| Var | Example | Notes |
|-----|---------|-------|
| `BUSINESS_UNIT` | `paragon_tax` | One of: `paragon_tax`, `hh_insurance`, `hh_consulting`. Used by lib workflows for env-var routing. |
| `BRAND_NAME` | `Paragon Tax` | Human-facing brand for fallback copy. |
| `BRAND_VOICE` | `trusted-advisor` | Maps to copy library voice profile. |

## Twilio (per-business from-numbers)

| Var | Notes |
|-----|-------|
| `TWILIO_FROM_NUMBER` | Default sender number, E.164. |
| `TWILIO_FROM_NUMBER_PARAGON_TAX` | Per-business override. |
| `TWILIO_FROM_NUMBER_HH_INSURANCE` | Per-business override. |
| `TWILIO_FROM_NUMBER_HH_CONSULTING` | Per-business override. |
| `TWILIO_STATUS_CALLBACK_URL` | Webhook URL n8n exposes for delivery status. |

**Credentials in n8n** (not env vars): create a `twilioApi` credential named `Twilio HIRO` with the Account SID + Auth Token. The lib workflows reference it by ID — replace `REPLACE_WITH_TWILIO_CRED_ID` in each lib JSON on import.

## Gmail (per-business aliases)

| Var | Notes |
|-----|-------|
| `GMAIL_FROM_ALIAS` | Default from-alias. |
| `GMAIL_FROM_ALIAS_PARAGON_TAX` | e.g. `hiro@paragonpartnerllc.com`. |
| `GMAIL_FROM_ALIAS_HH_INSURANCE` | e.g. `hiro@hhinsurance.info`. |
| `GMAIL_FROM_ALIAS_HH_CONSULTING` | e.g. `hiro@hhconsulting.group`. |

**Credentials in n8n**: separate `gmailOAuth2` credential per business inbox. Lib workflow currently references one — branch by `business_unit` if multiple inboxes go live.

## HubSpot

| Var | Notes |
|-----|-------|
| `HUBSPOT_PIPELINE_ID` | Default deal pipeline ID. |
| `HUBSPOT_DEAL_STAGE_WON` | Stage ID used to enroll into post-close sequences. |
| `HUBSPOT_LIFECYCLE_DEFAULT` | Lifecycle stage for newly-created contacts (default `lead`). |

**Credentials in n8n**: `hubspotAppToken` Private App named `HubSpot HIRO Private App`. Required scopes: `crm.objects.contacts.read`, `crm.objects.contacts.write`, `crm.schemas.contacts.read`, `crm.objects.deals.read`, `crm.objects.deals.write`.

## Calendly

| Var | Notes |
|-----|-------|
| `CALENDLY_WEBHOOK_SECRET` | Verifies inbound webhook signatures. |
| `CALENDLY_TUNNEL_URL` | Public URL where Calendly POSTs (Cloudflare Tunnel). |

## Bentley HTTP (AI call-out)

| Var | Notes |
|-----|-------|
| `BENTLEY_HTTP_URL` | Bentley's chat endpoint, e.g. `http://localhost:8081/v1/chat`. |
| `BENTLEY_HTTP_TOKEN` | Shared secret for n8n to authenticate to Bentley. |

## Monday board

| Var | Notes |
|-----|-------|
| `MONDAY_BOARD_ID` | `18414790992` for HIRO internal board. |
| `MONDAY_API_TOKEN` | Set as n8n credential, not env var, for security. Lib `log-to-monday-update.json` (not yet built) references it. |

## Telegram (optional)

Only needed if n8n triggers Bentley DMs directly. Default: Bentley owns Telegram, n8n logs to Monday and Bentley reads Monday.

| Var | Notes |
|-----|-------|
| `TELEGRAM_BOT_TOKEN` | Same token Bentley uses. |
| `TELEGRAM_HIRO_CHAT_ID` | Hiro's Telegram chat ID for direct DMs. |

## Sequence pacing

In days. Used by cron-tick workflows to decide when a contact is ripe for the next step.

| Var | Default | Notes |
|-----|---------|-------|
| `PARAGON_REFERRAL_STEP_INTERVAL_DAYS` | 3 | Days between consecutive steps in paragon-tax referral-request. |
| `HH_INSURANCE_QUAL_STEP_INTERVAL_DAYS` | 2 | Days between qualification-router probes. |
| `HH_CONSULTING_INVESTOR_STEP_INTERVAL_DAYS` | 4 | Days between investor-outreach touches. |

## Deployment-target switch

| Var | Example | Notes |
|-----|---------|-------|
| `DEPLOY_TARGET` | `nick-test` or `hiro-prod` | Read by workflows that want to behave differently in test (synthetic leads) vs prod (real). Used by `cron/sequence-tick.json` to skip cron firing on test except when manually triggered. |
