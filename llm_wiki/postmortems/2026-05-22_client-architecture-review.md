# Post-mortem: Client Architecture Review (2026-05-22)

## Outcome

**Success (partial)** — Both active clients now have `concepts/workflow_architecture.md` in the Upwork wiki plus MAS rollup. Execution interrupted once by plan-mode; completed on retry.

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| Turo architecture | `~/Upwork/llmwiki/Turo/concepts/workflow_architecture.md` | Done |
| OpenClaw architecture | `~/Upwork/llmwiki/OpenClaw/concepts/workflow_architecture.md` | Done |
| OpenClaw index | `~/Upwork/llmwiki/OpenClaw/index.md` | Done |
| MAS rollup | `llm_wiki/architecture/client_workflows_summary.md` | Done |
| Repo scans | `llm_wiki/architecture/turo_scan.json`, `openclaw_scan.json` | Done |
| Prompt spec | `prompts/5-client-architecture-review.md` | Done |
| Wiki template | `templates/client-workspace/wiki/workflow_architecture.md.template` | Blocked by plan-mode once |

## Method

- Phase 0: `git fetch` on 5 client-related repos; `repo_analyzer.py` on both project roots
- Phase 1: Parallel `explore` sub-agents (Turo + OpenClaw) — structured workflow/tool/drift reports
- Phase 2: Orchestrator synthesized wiki pages + rollup

## Key findings

### Turo

- S3/S4/FC → S2 dependency chain is the critical pricing path; DS 87382 and FlightCache are shared contracts
- Status drift between wiki overview and scenario entity pages is the #1 maintenance risk
- Monday board stale since 2026-04-28; wiki is ahead of client-visible PM

### OpenClaw

- **Hermes is active runtime**; OpenClaw skills/sequences are legacy reference only
- Wiki was severely under-scaffolded (2 files) — index + architecture added
- Cron script path bug: `crm-sync` vs `paragon-crm-sync`

## Learnings

- **LEARNED:** Always run GitHub pre-flight (`git fetch` + inventory cross-check) before architecture review
- **LEARNED:** Parallel `explore` sub-agents produce better drift reports than single-pass reads
- **LEARNED:** Cursor plan-mode blocks non-markdown writes — execute architecture reviews in agent mode or Claude Code

## Follow-ups

1. Update Turo `index.md` to link workflow_architecture
2. Append client wiki log.md entries
3. Global KB entity architecture pointers (short paragraph each)
4. Reconcile Turo scenario status fields in entity frontmatter
