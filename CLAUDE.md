# MAS — Multi-Agent System Orchestrator

Unified routing shell for domain-specific agent teams. Extends the existing team-of-teams pattern; does not replace it.

## Session startup

At the start of EVERY session in this workspace, read in order:

1. `orchestrator/agents/orchestrator.md` — Tier-1 persona, intake + dispatch contract
2. `TASKS.md` — current backlog and blockers
3. `orchestrator/domains.yaml` — domain → Team Lead mapping
4. `orchestrator/router.md` — routing decision tree
5. `orchestrator/intake_template.md` — used on every new project
6. `~/.claude/kb/index.md` — Global KB catalog (sync relevant pages)
7. `~/Upwork/llmwiki/index.md` — per-client wiki catalog (if client work)

**Mobile / away from desk:** use Claude Code Remote Control — `docs/CLAUDE_CODE_SETUP.md`. Start with `claude --remote-control "MAS Orchestrator"` from this directory. Requires Max `/login` (full scope), not `setup-token`.

## Orchestrator duties

The full persona lives in [`orchestrator/agents/orchestrator.md`](orchestrator/agents/orchestrator.md). Short form:

1. **Intake** — capture prompt verbatim; fill `orchestrator/intake_template.md` into `llm_wiki/intakes/`
2. **Goal definition** — one-sentence goal + auxiliary points + definition of done (confirm with Nick)
3. **Path mapping** — map the full path to done before dispatch (blocked-step ladder)
4. **Credential inventory** — single batched ask at intake; delta inventory when new components appear
5. **Dispatch** — Team Leads via `Task` tool using the 9-section handoff contract
6. **Monitor + self-heal** — try fallback rungs; cap retries at 3 per node; ship partial deliverables over stalls
7. **Close + learn** — never silently stop; postmortem on surprises; promote patterns after 3 recurrences

## Domain routing (quick reference)

| Domain | Team Lead | When to use |
|--------|-----------|---------------|
| `coding` | `architect-lead` | Code structure, refactors, multi-file edits |
| `client-bootstrap` | `monday-hermes-pm-lead` | Audit/scaffold scripts + Monday/wiki PM |
| `upwork-ops` | `monday-hermes-pm-lead` | Upwork delivery, Monday.com PM (Phase 2) |
| `monday-clients` | `monday-hermes-pm-lead` | Hermes/AI-agent Monday command centers |
| `automation` | `backend-lead` (Cursor builtin) | Make.com/n8n workflows (Phase 2) |
| `content` | — | Social clipping (Phase 2; content-lead removed until rebuilt) |

Full routing logic: `orchestrator/router.md`

## Key paths

| Asset | Location |
|-------|----------|
| Client scaffolder | `scripts/scaffold_client.py` |
| Repo analyzer | `scripts/repo_analyzer.py` |
| Client template | `templates/client-workspace/` |
| Cursor prompts | `prompts/` |
| MAS postmortems | `llm_wiki/postmortems/` |
| Global KB | `~/.claude/kb/` |
| Upwork wiki | `~/Upwork/llmwiki/` |
| Team-of-teams plan | `C:/Users/Nicol/agentic/TEAM-OF-TEAMS-PLAN.md` |

## Guardrails

- Use strict Pydantic schemas for inter-agent JSON handoffs
- Hard cap recursion at 3 attempts per worker task
- Never auto-post to social platforms — HITL approval required
- Defer LangGraph service until always-on n8n pipelines are needed
- Hermes remains eval-only until CC-native MAS routing is proven

## Self-improvement

After every run with a failure or non-obvious judgment:
1. Append postmortem to `llm_wiki/postmortems/`
2. If same pattern appears 3+ times, promote to `~/.claude/kb/_reference/`
