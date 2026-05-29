# Client Workflow Architecture — Summary

**Generated:** 2026-05-22  
**MAS orchestrator:** client architecture review (Phase 1–2)

## Active bundles

| Client | Slug | Architecture doc | Primary runtime |
|--------|------|------------------|-----------------|
| Coastal Lux / Turo | `turo` | [Turo/concepts/workflow_architecture.md](file:///C:/Users/Nicol/Upwork/llmwiki/Turo/concepts/workflow_architecture.md) | Make.com + Airtable + Netlify |
| Hermes / HIRO | `openclaw` | [OpenClaw/concepts/workflow_architecture.md](file:///C:/Users/Nicol/Upwork/llmwiki/OpenClaw/concepts/workflow_architecture.md) | Hermes Agent (Bentley, Telegram + GHL) |

## GitHub repos verified (2026-05-22)

### Turo

- `NickHeight/turo-fleet-automation-system` — main automation repo
- `NickHeight/coastal-lux-site` — nested marketing site
- `NickHeight/llmwiki` — shared wiki (`Turo/` section)

### OpenClaw

- `NickHeight/openclaw-elijah-workspace` — workspace wrapper
- `NickHeight/openclaw-hiro-paragon` — agent code (Hermes active)
- `NickHeight/hirobooker-site` — client website

## Cross-client patterns

| Pattern | Turo | Hermes / HIRO |
|---------|------|---------------|
| Agent-readable PM | Monday (stale) + Asana MCP | None standardized |
| Wiki as long-form truth | llmwiki/Turo/ rich | llmwiki/OpenClaw/ expanded 2026-05-22 |
| Blocked comms channel | Twilio A2P | Twilio A2P |
| Primary automation | Make scenarios | Hermes skills + cron |
| MAS domain for workflows | `automation` | `coding` + `upwork-ops` |

## Top drift items to reconcile

1. **Turo:** Wiki overview "Active" vs scenario entity "stopped-global-freeze" — pick one source of truth per scenario.
2. **Turo:** Monday client board 4 weeks behind wiki — run reconciliation sweep.
3. **Hermes / HIRO:** `cron-setup.sh` references missing `crm-sync/` path (legacy OpenClaw cron).

## Repo analyzer outputs

- `llm_wiki/architecture/turo_scan.json`
- `llm_wiki/architecture/openclaw_scan.json`

## Next actions

- [ ] Wire Monday MCP + weekly sync job (Turo) OR migrate to Asana-only with Marc guest access
- [ ] Expand OpenClaw wiki entities/ (mirror Turo pattern)
- [ ] Phase 2: `upwork-ops` worker reads workflow_architecture.md for routing
