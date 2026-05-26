# MAS Task Board

Single source of truth for the Tier-1 Orchestrator. Unchecked items block session stop.

## Foundation (active)

- [x] Scaffold MAS workspace structure
- [x] Create domain registry and routing docs
- [x] Build client template scaffolder
- [x] Build repo analyzer
- [x] Document Cursor and Obsidian setup
- [x] Run verification dry-runs on test client
- [x] Upwork root audit (`upwork_audit.py`) — inventory + gap report
- [x] Cross-links applied for Turo + OpenClaw bundles

## Active — Client architecture + SMS → Monday

- [x] Hermes / HIRO wiki rename — Hiro agent → Hermes production runtime (2026-05-25)
- [x] Turo `concepts/workflow_architecture.md` — per-workflow done vs needed
- [x] `scripts/suggest_monday_from_messages.py` — SMS/MMS → Monday suggestions
- [~] Monday reconciliation sweep for Marc (board `18408242353` vs wiki) — paused: awaiting Nick APPROVE before any Monday write (HITL gate per `Turo/playbooks/sms_to_monday_review.md`)
- [x] Marc Monday board redesign — client board `18408242353` polished (views, hygiene sweep, 5-item action queue). Daily: `python scripts/monday_board_hygiene.py`. Manual: add Done→Completed automation in Monday UI (MCP automations 403).
- [x] HIRO Monday command center — board `18414790992` updated, monday-sync skill shipped, ai-agent template written (2026-05-26). Pending: HIRO guest invite acceptance + Mini git pull.
- [x] Commit/push pending `llmwiki` archive changes — 56 files, commit `2d43b0a`, pushed to `NickHeight/llmwiki` master
- [x] Rebuild MAS Tier-1 orchestrator persona — `orchestrator/agents/orchestrator.md` + `orchestrator/intake_template.md` (workspace-only, 2026-05-26). CLAUDE.md, domains.yaml, mas-orchestrator.mdc wired.

## Periodic maintenance

```powershell
python scripts/upwork_audit.py --root ~/Upwork --dry-run
```

Run monthly or after onboarding a new client.

## Client architecture review (2026-05-22)

- [x] GitHub pre-flight + repo_analyzer for Turo and OpenClaw
- [x] Turo `concepts/workflow_architecture.md`
- [x] OpenClaw `concepts/workflow_architecture.md` + `index.md`
- [x] MAS rollup + post-mortem
- [~] Reconcile Turo scenario entity status vs overview (follow-up) — deferred 2026-05-25, unrelated to HIRO/Bentley work
- [~] Monday board sync sweep for Marc (follow-up) — deferred 2026-05-25, HITL gate noted under Active section

## Deferred — Pipeline 2: Upwork Delivery

> Marker `[~]` = explicitly deferred (Phase 2). Not blocking session stop.

- [~] Wire `upwork-ops` domain to existing Upwork skills
- [~] Implement Monday.com API worker
- [~] Connect scope parser to Gemini ingestion

## Deferred — Pipeline 1: Social Media Clipping

- [~] Transcript ingestion worker (Whisper/Gemini)
- [~] Platform compliance scoring
- [~] Remotion animated caption renderer
- [~] HITL approval gate + multi-platform publisher
