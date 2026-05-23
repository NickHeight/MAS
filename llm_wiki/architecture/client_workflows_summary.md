# Client Workflow Architecture — Summary

Rollup of active MAS client bundles. Detail pages live in each client wiki.

**Updated:** 2026-05-22

---

## Turo (Marc Walden / Coastal Lux)

**Canonical doc:** [~/Upwork/llmwiki/Turo/concepts/workflow_architecture.md](file:///C:/Users/Nicol/Upwork/llmwiki/Turo/concepts/workflow_architecture.md)

| Layer | Count | Status |
|-------|-------|--------|
| Core Make scenarios (S1–S4) | 4 | ✅ Active |
| Firecrawl helpers | 4 | 3 active, 1 parked |
| Financial (S6/S7/QBO/Stripe) | 4 | ❌ Built but off — Marc gated |
| Web (site + 2 dashboards) | 3 | ✅ Live on Netlify |
| PM sync | Monday + SMS agent | ⚠️ Monday 4wk stale |

**Top blockers:** TFV/A2P pending, Stripe LIVE + DKIM, QBO prod attestation, Meta BM invite, Bouncie creds, walkthrough call.

**SMS → Monday:** `python scripts/suggest_monday_from_messages.py` + playbook `Turo/playbooks/sms_to_monday_review.md`

---

## OpenClaw (Elijah Booker / HIRO)

**Status:** Architecture review pending (paragon repo synced 2026-05-18; wiki stale 2026-04-18).

**Repos:**
- `NickHeight/openclaw-elijah-workspace` (wrapper)
- `NickHeight/openclaw-hiro-paragon` (agent code)
- `NickHeight/hirobooker-site`

**Next:** Draft `OpenClaw/concepts/workflow_architecture.md` after Turo PM loop proven.

---

## Git freshness (2026-05-22)

| Repo | Local vs GitHub |
|------|-----------------|
| turo-fleet-automation-system | ✅ synced |
| coastal-lux-site | ✅ pushed (`replay-addon-session`) |
| llmwiki | ⚠️ 52 uncommitted local files (archive moves) |
| openclaw-elijah-paragon | ✅ synced |
