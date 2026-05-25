# System Prompt 5: Client Workflow Architecture Review

**Workspace:** `c:/Users/Nicol/MAS/`  
**Scope:** Active client bundles from `llm_wiki/audits/upwork_inventory.json`

## Objective

Produce one **`concepts/workflow_architecture.md`** per active client with:
workflow catalog, tools matrix, mermaid dependency graph, cross-workflow contracts,
operational dependencies, gaps/drift, and MAS routing hints.

## Orchestrator phases

| Phase | Domain | Lead | Action |
|-------|--------|------|--------|
| 0 | client-bootstrap | client-lead | GitHub pre-flight, audit, repo_analyzer |
| 1 | automation + coding | backend-lead + architect-lead | Parallel per-client review (read-only) |
| 2 | coding | architect-lead | Merge rollup + Global KB + post-mortem |

## Reconciliation rules

- Wiki wins for **client-facing status**
- Repo wins for **paths and code structure**
- Flag Make scenario IDs, Airtable tables, connection ID mismatches
- **Read-only** — no Make/production changes during review

## Output paths

- `~/Upwork/llmwiki/{Client}/concepts/workflow_architecture.md`
- `c:/Users/Nicol/MAS/llm_wiki/architecture/client_workflows_summary.md`
- Template: `templates/client-workspace/wiki/workflow_architecture.md.template`
