# System Prompt 3: Upwork Delivery Pipeline (Stub)

**Project:** Upwork Delivery & Monday.com Autonomous PM  
**Status:** DEFERRED — Phase 2  
**Workspace:** `c:/Users/Nicol/MAS/`

---

## 1. Context

This pipeline automates Upwork client onboarding, scope generation, Monday.com task mapping, development blueprints, and client communications.

**Do NOT implement now.** This prompt documents the architecture for future wiring.

## 2. Existing assets to delegate to (do not rewrite)

| Asset | Path / Skill |
|-------|-------------|
| Job intake | `~/Upwork/proposal-system/intake-monitor/monitor.py` |
| Proposal queue | `process-upwork-queue` skill |
| Proposal generation | `upwork-proposal` skill |
| Active client monitoring | `upwork-monitor` skill |
| Client bootstrap | `scripts/scaffold_client.py` |
| Make.com deploy | `make-scenario-builder` skill |
| Wiki schema | `~/Upwork/llmwiki/CLAUDE.md` |
| Monday template | `~/.claude/kb/_reference/monday-board-template.md` |

## 3. Target architecture (Phase 2)

```
Orchestrator [domain: upwork-ops]
    └── client-lead
        ├── Project Supervisor (GPT reasoning model)
        │   ├── Scope Parser Worker (Gemini — large context ingestion)
        │   └── Monday.com PM Worker (GraphQL API — NEW)
        └── Delivery Supervisor (GPT reasoning model)
            ├── Dev Architect Worker (Claude — code/workflow blueprints)
            └── Client Relations Worker (Claude — status updates)
```

## 4. Integration points in MAS

When Phase 2 begins:

1. Add workers under `scripts/workers/upwork/`
2. Wire `upwork-ops` domain in `orchestrator/domains.yaml` from `stub` to `active`
3. Monday.com worker reads `technical_scope` Pydantic model, writes board tasks
4. Post-mortem archiver copies successful blueprints to `~/Upwork/llmwiki/{Client}/playbooks/`

## 5. Pydantic handoff schema (future)

```python
class TechnicalScope(BaseModel):
    client_name: str
    deliverables: list[str]
    tech_stack: list[str]
    timeline: str
    constraints: list[str]
    platform: str  # "n8n" | "make" | "web" | "ai_agent"
```

## 6. Execution instructions (when activated)

1. Read existing Upwork skills — extend, do not duplicate
2. Implement Monday.com GraphQL worker as standalone script first
3. Test with a past client brief before live API connection
4. Update TASKS.md deferred section to track progress

**For now:** No code changes. Reference this prompt when Phase 2 starts.
