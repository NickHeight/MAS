# MAS Routing Decision Tree

Tier-1 Orchestrator uses this tree to classify intent and dispatch Team Leads.

## Step 1: Classify domain

```
User request
    |
    +-- mentions new client / bootstrap / scaffold / template?
    |       --> client-bootstrap
    |
    +-- mentions Upwork / Monday.com / client delivery / scope?
    |       --> upwork-ops (stub — route to client-lead with Phase 2 note)
    |
    +-- mentions Hermes / Bentley / AI agent client / Monday PM for agent clients?
    |       --> monday-clients (monday-hermes-pm-lead)
    |
    +-- mentions Make.com / n8n / workflow / blueprint?
    |       --> automation (stub — route to backend-lead)
    |
    +-- mentions video / clip / caption / social / livestream?
    |       --> content (stub — route to content-lead)
    |
    +-- mentions proposal website / premium demo / portfolio site for Upwork?
    |       --> proposal-websites (PremiumWebDesign framework + ~/Upwork/websites)
    |
    +-- mentions code / refactor / structure / types / config?
    |       --> coding
    |
    +-- spans multiple domains?
            --> dispatch multiple Team Leads in parallel via Agent Teams
```

## Step 2: Sync wikis

For each matched domain, read the `wiki_sync` paths listed in `domains.yaml`:

1. Read `index.md` at each wiki root first
2. Pull only pages relevant to the current task (do not grep entire vault)
3. Inject wiki pointers into Team Lead dispatch prompt

## Step 3: Update TASKS.md

- Add or update task entries with domain tag: `[domain:client-bootstrap]`
- Unchecked items block session stop (Stop hook enforces this globally)

## Step 4: Dispatch Team Lead

Use Agent Teams with standing subagent definitions from `~/.claude/agents/`.

Dispatch prompt must include:
- Task text from TASKS.md
- Domain classification
- Wiki page list (paths, not full content)
- File ownership scope
- Success criterion

## Step 5: Post-mortem

On completion or failure:

1. Write `llm_wiki/postmortems/YYYY-MM-DD_<topic>.md`
2. If client work: append to `~/Upwork/llmwiki/{ClientName}/log.md`
3. If cross-cutting lesson: consider promotion to `~/.claude/kb/_reference/`

## Multi-domain example

Request: *"Set up a new client for n8n workflows and scaffold their repo"*

```
Domains: client-bootstrap + automation
Team Leads: client-lead (scaffold) + backend-lead (n8n module guidance)
Order: client-lead first (creates repo), then backend-lead (populates automation module)
```

## Error handling

| Situation | Action |
|-----------|--------|
| Worker fails 3 times | Supervisor reports `failed` to Team Lead |
| Team Lead fails twice | Orchestrator escalates to user |
| Unknown domain | Default to `coding` via architect-lead |
| Stub domain requested | Dispatch lead with Phase 2 deferral note in TASKS.md |
