# MAS — Multi-Agent System Orchestrator

Unified routing shell for domain-specific agent teams. Extends the existing team-of-teams pattern; does not replace it.

## Session startup

At the start of EVERY session in this workspace, read in order:

1. `TASKS.md` — current backlog and blockers
2. `orchestrator/domains.yaml` — domain → Team Lead mapping
3. `orchestrator/router.md` — routing decision tree
4. `~/.claude/kb/index.md` — Global KB catalog (sync relevant pages)
5. `~/Upwork/llmwiki/index.md` — per-client wiki catalog (if client work)

**Mobile / away from desk:** use Claude Code Remote Control — `docs/CLAUDE_CODE_SETUP.md`. Start with `claude --remote-control "MAS Orchestrator"` from this directory. Requires Max `/login` (full scope), not `setup-token`.

## Orchestrator duties

1. **Classify intent** — map user request to one or more domains (`coding`, `client-bootstrap`, `upwork-ops`, `automation`, `content`)
2. **Sync wikis** — pull relevant Global KB and Upwork wiki pages before dispatch
3. **Update TASKS.md** — tag tasks with domain; never mark done without verification
4. **Dispatch Team Leads** — use Agent Teams with standing subagents from `~/.claude/agents/`
5. **Post-mortem** — on completion or failure, write to `llm_wiki/postmortems/YYYY-MM-DD_<topic>.md`

## Domain routing (quick reference)

| Domain | Team Lead | When to use |
|--------|-----------|---------------|
| `coding` | `architect-lead` | Code structure, refactors, multi-file edits |
| `client-bootstrap` | `client-lead` | New client setup, repo analysis, template scaffold |
| `upwork-ops` | `client-lead` | Upwork delivery, Monday.com PM (Phase 2) |
| `automation` | `backend-lead` | Make.com/n8n workflows (Phase 2) |
| `content` | `content-lead` | Social media clipping pipeline (Phase 2) |

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
