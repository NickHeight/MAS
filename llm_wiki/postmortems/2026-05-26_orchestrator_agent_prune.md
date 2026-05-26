# Postmortem — Orchestrator agent prune (2026-05-26)

## What changed

Removed MAS orchestrator subagents not built on **2026-05-25** or **2026-05-26**:

- `orchestrator/agents/client-lead.md` (2026-05-22)
- `orchestrator/agents/content-lead.md` (2026-05-22)
- `orchestrator/agents/sms-monday-reviewer.md` (2026-05-22)

## Kept (2026-05-26)

- `monday-hermes-pm-lead.md`
- `monday-board-builder.md`
- `monday-hermes-sync-worker.md`

## Routing updates

- `orchestrator/domains.yaml` — `team_leads` section lists only the Monday trio; `client-lead` / `content-lead` paths removed.
- SMS → Monday flow: `scripts/suggest_monday_from_messages.py` (no dedicated subagent).
- `coding` / `automation` still name `architect-lead` / `backend-lead` as **Cursor built-ins** (`team_lead_source: cursor_builtin`), not MAS files.

## Not removed (outside MAS scope)

- `C:/Users/Nicol/agentic/system/agents/*` and `team-of-teams` skill (2026-04-23) — separate repo; reinstall via `agentic/system/install.sh` when needed.

## Follow-up

Re-scaffold domain leads (client, content, SMS reviewer) only when rebuilt with pi-team-architect or new templates.
