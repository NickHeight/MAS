# SMS → Monday Review Agent

Weekly or on-demand agent for scanning Marc/HIRO SMS backups and drafting Monday.com updates.

## Trigger

- User: "review Marc texts" / "SMS to Monday" / weekly cron
- Orchestrator domain: `upwork-ops` → `client-lead`

## Steps

1. Run `python scripts/suggest_monday_from_messages.py --days 30 --wiki-copy <wiki path>`
2. Read `Turo/concepts/workflow_architecture.md` for workflow context
3. Read `Turo/decisions/2026-05-22_monday_wiki_reconciliation.md` for open Monday gaps
4. Produce a **draft post list** (plain text) — one block per suggested item
5. Wait for human `APPROVE` before calling Monday MCP `create_update` / `create_item`
6. Log to `Turo/log.md` and refresh `sources/marc_messages/index.md`

## Tools

- `scripts/suggest_monday_from_messages.py`
- `scripts/scan_message_backups.py`
- Monday MCP (`https://mcp.monday.com/mcp`) — requires OAuth with `boards:write`

## Output format (draft)

```
MONDAY DRAFT — [workflow area]
Board: 18408242353
Action: new item | update on [item_id]
Status: Pending Marc | Pending Nick
Category: Financials
Body:
  [plain text, no HTML]
Source SMS: [date] [preview]
Wiki ref: Turo/log.md [date entry]
```
