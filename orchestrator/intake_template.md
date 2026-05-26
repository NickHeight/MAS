# MAS Project Intake Template

Used by `orchestrator/agents/orchestrator.md` at the start of every new project. Fill into `llm_wiki/intakes/YYYY-MM-DD_<slug>.md` before any Team Lead dispatch.

Keep prose tight; tables and YAML over paragraphs.

---

## 0. Verbatim prompt

> Paste Nick's exact opening message. Do not paraphrase.

## 1. Goal (one sentence)

`<who> gets <what> by <when>, measured by <metric>.`

## 2. Auxiliary points

- Constraints (budget, latency, integrations, compliance):
- Non-goals (explicit out-of-scope):
- Prior decisions to honor (link past postmortems, wiki pages):
- Voice / channel rules (e.g. Katya in-platform only, HITL approve gates):
- Deadlines / external dependencies:

## 3. Definition of done

One or two lines naming the artifact or behavior that closes the project.

## 4. Full path map

| # | Step | Owner (Team Lead) | Output artifact | Fallback rung |
|---|------|-------------------|-----------------|---------------|
| 1 |      |                   |                 |               |
| 2 |      |                   |                 |               |

Mark unknowns explicitly. If any row has unknown owner or output, schedule a research-only spike first.

## 5. Credential / access inventory (ask once)

```yaml
credentials:
  - service: <name>
    env_vars: []
    scope: <read | write | full>
    hitl: false
    fallback: <api | mcp | browser | partial | hitl>
    source_doc: <path>
```

Mark anything Nick still needs to provide before dispatch can start.

## 6. Wiki preloads

- Global KB pages: 
- Upwork wiki pages: 
- Reference matrices (e.g. `~/.claude/kb/_reference/frontier-model-research/model-routing-matrix.md`):

## 7. Risk register

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
|      |           |           |

## 8. Dispatch plan

Order of Team Lead calls (parallel where independent):

1. 
2. 
3. 

## 9. Closeout (filled at end)

- Final artifacts:
- Postmortem path:
- Model routing changes (if any):
- New agent teams spun up (pi-team-architect):
