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

- [ ] OpenClaw `concepts/workflow_architecture.md` (after Turo PM loop validated)
- [x] Turo `concepts/workflow_architecture.md` — per-workflow done vs needed
- [x] `scripts/suggest_monday_from_messages.py` — SMS/MMS → Monday suggestions
- [ ] Monday reconciliation sweep for Marc (board `18408242353` vs wiki) — human APPROVE before post
- [ ] Commit/push pending `llmwiki` archive changes (52 files)

## Periodic maintenance

```powershell
python scripts/upwork_audit.py --root ~/Upwork --dry-run
```

Run monthly or after onboarding a new client.

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
