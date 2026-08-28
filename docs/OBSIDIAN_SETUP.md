# Obsidian Setup — Read-Only Wiki Dashboard

Obsidian is your **human dashboard** over the wikis that agents maintain. You do not manually write notes — agents append per wiki schema rules.

## Primary vault: Upwork LLM Wiki

1. Open Obsidian
2. **Open folder as vault** → `~/Upwork/llmwiki`
3. Enable **Graph view** (core plugin) to see cross-client playbook links
4. Enable **Search** for quick client lookup

This vault contains per-client folders (Turo, OpenClaw, Hermes, etc.) plus `_shared/playbooks/`.

## Optional second vault: Global KB

1. **Open folder as vault** → `~/.claude/kb`
2. Use for cross-project concepts, entity pages, and reference docs

Or use Obsidian's multi-root vault feature if available in your version.

## Recommended settings

| Setting | Value | Why |
|---------|-------|-----|
| New link format | Relative path | Matches wiki `[[links]]` |
| Default location for new notes | Disabled / warn | Agents create notes, not you |
| Auto-update links | On | Keeps graph accurate after agent renames |
| Daily notes | Off | Not used in this workflow |

## Plugins (minimal)

Start with core plugins only:

- **Graph view** — visualize client/playbook relationships
- **Search** — find entities across clients
- **Backlinks** — see what references a playbook

Defer **Dataview** until post-mortem volume justifies queries.

## What you'll see after MAS scaffold

When `scaffold_client.py` runs for a client, Obsidian immediately shows:

- `~/Upwork/llmwiki/{ClientName}/00_overview.md`
- `index.md`, `log.md`
- Empty `entities/`, `playbooks/`, `decisions/` folders ready for agent writes

Cross-link to Global KB entity at `~/.claude/kb/wiki/entities/{slug}.md` (open via second vault or absolute path).

## MAS postmortems

MAS-local postmortems live at `~/MAS/llm_wiki/postmortems/`.

Options:
- Symlink into Upwork wiki: `_shared/postmortems/` → MAS postmortems folder
- Or open MAS as a third vault root for orchestrator run history

## Git sync reminder

The Upwork wiki is edited from PC and laptop. Before any agent writes:

```bash
git -C ~/Upwork/llmwiki pull --ff-only
```

After writes: commit + push. See `~/Upwork/llmwiki/CLAUDE.md` for full sync rules.

## Read-only discipline

Treat Obsidian as **read + navigate**, not **write**. All writes go through agents following atomic-write rules (page + log + index in same turn).
