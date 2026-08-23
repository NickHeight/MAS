# MAS LLM Wiki Index

MAS `llm_wiki` is an audit/postmortem cache for the MAS orchestrator. It is not the primary Global KB and not the live Upwork client state wiki.

## Read order

1. `../AGENTS.md` — MAS workspace rules and learned preferences.
2. This `index.md`.
3. `architecture/` for runbooks, maps, and operating architecture.
4. `audits/` for point-in-time reviews.
5. `postmortems/` for append-only run history.

## Folders

- `architecture/` — MAS orchestration architecture, escalation runbooks, subagent/document context maps.
- `audits/` — audits and reviews from MAS runs.
- `postmortems/` — append-only run history. Promote recurring patterns to `C:/Users/Nicol/.claude/kb/_reference/` after 3+ occurrences.

## Routing

- Active Upwork/client state belongs in `C:/Users/Nicol/Upwork/llmwiki`.
- Cross-project durable patterns belong in `C:/Users/Nicol/.claude/kb`.
- MAS-local execution evidence and postmortems belong here.
