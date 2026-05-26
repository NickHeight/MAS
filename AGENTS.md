## Learned User Preferences

- Prefers public web/docs research to use Firecrawl, while logged-in or private sites should use Cursor/Chrome after he signs in manually.
- Wants agents to keep moving when a path is blocked by credentials or HITL, shipping useful partial artifacts with explicit blockers instead of stalling.
- Prefers client-facing delivery surfaces to be simple, polished, mobile-friendly, and one-place for clients rather than split across email, Drive, and project boards.
- Wants background agents to drain `TASKS.md` continuously rather than stopping at turn checkpoints; when blocked, mark the blocker and continue to the next open task.
- Upwork pre-contract Katya replies must stay in-platform — no external scheduling links, phone numbers, or off-platform contact requests until the contract/workroom is active.

## Learned Workspace Facts

- MAS uses `TASKS.md` as backlog state, and live Monday.com client-board writes should stay gated on explicit `APPROVE`.
- Coastal Lux/Turo Monday boards are durable workspace references: internal build board `18408228704`, client portal board `18408242353`.
- HIRO/OpenClaw Hermes Monday command-center board is `18414790992`; reference template at `~/Upwork/llmwiki/_shared/references/ai-agent-client-monday-template.md`.
- MAS `monday-clients` domain routes Hermes/AI-agent client PM through `monday-hermes-pm-lead` and related Monday agents in `orchestrator/agents/`.
- Wake-up escalation for human gates runs through `scripts/alert_escalator.py` and `llm_wiki/architecture/mas_escalation_runbook.md` (Slack + Twilio SMS/voice, ACK-gated).
- Firecrawl is authenticated for this workspace; `.firecrawl/` is ignored and used as a local cache for public research outputs.
- `llm_wiki/architecture/mas_subagent_doc_context_map.md` maps cached `.firecrawl/mas-docs/` documentation packs to MAS subagent domains.
- Frontier model routing research lives in `frontier-model-research/02_plan/complete-plan.md`, with Global KB companions under `_reference/frontier-model-research/`.
