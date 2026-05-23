# System Prompt 1: Core Orchestrator Engine

**Project:** MAS — Unified Multi-Agent Domain Router  
**Workspace:** `c:/Users/Nicol/MAS/`  
**Framework:** Extends existing team-of-teams (Claude Code Agent Teams)  
**Do NOT build:** Standalone LangGraph service (deferred to Phase 2)

---

## 1. Context

You are building the central routing shell for a multi-pipeline agent framework. MAS extends the existing 4-tier team-of-teams pattern at `C:/Users/Nicol/agentic/` — it does **not** replace it.

MAS routes user intent to domain-specific Team Leads:

| Domain | Team Lead | Status |
|--------|-----------|--------|
| `coding` | `architect-lead` | Active |
| `client-bootstrap` | `client-lead` | Active |
| `upwork-ops` | `client-lead` | Stub |
| `automation` | `backend-lead` | Stub |
| `content` | `content-lead` | Stub |

Both Upwork delivery and social media clipping pipelines get architectural hooks only — full implementation is deferred.

## 2. Existing infrastructure to reuse

- Team-of-teams plan: `C:/Users/Nicol/agentic/TEAM-OF-TEAMS-PLAN.md`
- Standing subagents: `~/.claude/agents/` (orchestrator, architect-lead, backend-lead, etc.)
- Global KB: `~/.claude/kb/`
- Upwork LLM Wiki: `~/Upwork/llmwiki/`
- Client bootstrap spec: `~/.claude/kb/_reference/new-client-project-bootstrap.md`
- Upwork skills: `process-upwork-queue`, `upwork-proposal`, `upwork-monitor`
- Make.com skill: `make-scenario-builder`

## 3. Directory structure (verify or create)

```text
MAS/
├── TASKS.md
├── CLAUDE.md
├── orchestrator/
│   ├── domains.yaml
│   └── router.md
├── scripts/
│   ├── models.py
│   ├── scaffold_client.py
│   └── repo_analyzer.py
├── templates/client-workspace/
├── prompts/
├── llm_wiki/postmortems/
└── docs/
```

## 4. Shared state schema (Pydantic stub)

In `scripts/models.py`, define schemas for inter-agent handoffs:

```python
class GlobalState(BaseModel):
    trigger_source: str  # "cursor", "upwork", "monday", "livestream_feed"
    domains: list[str]
    metadata: dict
    shared_context: dict
    active_blueprints: dict
    execution_status: str
    error_logs: list[str]
```

This is a **stub** for future LangGraph integration. For now, TASKS.md + wiki pages serve as the live shared state.

## 5. Orchestrator execution flow

1. Read `CLAUDE.md` and `orchestrator/router.md`
2. Classify user intent → domain(s)
3. Sync relevant wiki pages from `domains.yaml`
4. Update `TASKS.md` with domain-tagged tasks
5. Dispatch Team Lead(s) via Agent Teams
6. On completion → write postmortem to `llm_wiki/postmortems/`

## 6. Post-mortem template

Save to `llm_wiki/postmortems/YYYY-MM-DD_<topic>.md`:

```markdown
---
date: YYYY-MM-DD
domains: [client-bootstrap]
status: completed|failed
---

# Post-mortem: <topic>

## What happened
## What worked
## What failed
## Promotion candidate (if 3+ recurrence)
```

## 7. Execution instructions

1. Verify the MAS directory structure matches Section 3
2. Ensure `orchestrator/domains.yaml` and `router.md` are complete
3. Ensure `scripts/models.py` has the Pydantic stub
4. Stop and ask the user to review the state schema before building worker scripts
