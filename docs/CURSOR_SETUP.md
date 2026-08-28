# Cursor Pro + Composer 2.5 Setup

MAS development uses **Cursor Pro subscription** for IDE work. External APIs power autonomous n8n/Make pipelines only.

## Subscription vs API keys

| Context | Use | Why |
|---------|-----|-----|
| Cursor IDE (Composer, Agent) | **Cursor Pro ($20/mo)** | Composer 2.5 is subsidized; BYOK gets expensive for multi-file edits |
| Claude desktop / Cowork | **Claude Pro ($20/mo)** | Daily brainstorming, file management |
| Autonomous pipelines (n8n, Make) | **Pay-as-you-go APIs** | Required for unattended agent loops |

Do **not** run Composer 2.5 on your own Anthropic/OpenAI keys inside Cursor unless debugging a specific model behavior.

## Cursor configuration

1. **Install Cursor Pro** — [cursor.com](https://cursor.com)
2. **Open MAS workspace** — `~/MAS`
3. **Enable Composer 2.5** — Settings → Models → enable Composer 2.5 for Agent/Composer
4. **Indexing** — Settings → Indexing → ensure MAS folder is indexed
5. **Rules** — `.cursor/rules/mas-orchestrator.mdc` applies automatically

### Optional: Docs indexing

Add these URLs in Settings → Docs for better Composer context:

- LangGraph docs (when Phase 2 LangGraph starts)
- Remotion docs (when content pipeline starts)
- Monday.com GraphQL API docs (when Upwork pipeline starts)

## API key setup (for scripts and Phase 2 pipelines)

Set spend caps on each provider console before generating keys.

| Provider | Console | Monthly cap | MAS usage |
|----------|---------|-------------|-----------|
| Anthropic | console.anthropic.com | $75 | Client comms, coding workers |
| OpenAI | platform.openai.com | $60 | Supervisors, Whisper |
| Google | aistudio.google.com | $50 | Repo analyzer `--use-gemini`, ingestion |

Store keys in environment variables (never commit):

```powershell
# PowerShell profile or .env (gitignored)
$env:ANTHROPIC_API_KEY = "..."
$env:OPENAI_API_KEY = "..."
$env:GOOGLE_API_KEY = "..."
```

## Monday.com MCP (Cursor vs Claude Code)

**Claude Code** already supports Monday via the official remote HTTP MCP (`https://mcp.monday.com/mcp`). Turo's project uses `mcp__claude_ai_monday_com__*` tools there after OAuth. Reference: `~/Upwork/llmwiki/_shared/references/monday_mcp.md`.

**Cursor (this workspace)** does **not** have Monday MCP enabled yet. Current MCP servers: GitHub, Context7, Figma, Asana.

To add Monday in Cursor:

1. Open **Cursor Settings → MCP** (or create `.cursor/mcp.json` in the MAS workspace).
2. Add the remote HTTP server:

```json
{
  "mcpServers": {
    "monday": {
      "url": "https://mcp.monday.com/mcp"
    }
  }
}
```

3. Restart Cursor and complete OAuth on first tool use (browser → Monday workspace picker).
4. Board IDs for active clients are in Global KB entities (e.g. `marc-walden-turo-fleet.md`) and `~/.claude/kb/_reference/monday-board-template.md`.

Until Monday MCP is wired in Cursor, use **Claude Code** for board reads/writes, or document board IDs in wiki overviews to clear audit "Monday documented" gaps.

## First-run workflow (audit before scaffold)

If Nick's Upwork folder already has clients scattered across `clients/`, `projects/`, and `llmwiki/`:

```powershell
cd ~/MAS

# 1. Audit entire Upwork root
python scripts/upwork_audit.py --root ~/Upwork

# 2. Review gap report
#    llm_wiki/audits/upwork_gap_report.md

# 3. Apply cross-links (safe — no repo moves)
python scripts/upwork_audit.py --root ~/Upwork --apply-cross-links --bundles turo,openclaw

# 4. New clients only
python scripts/scaffold_client.py --name "..." --slug ... --modules web --dry-run
```

Inventory lives at `llm_wiki/audits/upwork_inventory.json` — MAS client-lead reads this for routing.

## Prompt execution order

Run these in Cursor Composer (`Ctrl+I`):

1. `@prompts/1-core-orchestrator-engine.md` — verify orchestrator scaffolding
2. Review `scripts/models.py` GlobalState schema
3. `@prompts/2-client-template-explorer.md` — run Upwork audit, then scaffolder if needed
4. Test audit: `python scripts/upwork_audit.py --root ~/Upwork --dry-run`

Phase 2 prompts (reference only — do not execute yet):

- `prompts/3-upwork-delivery-pipeline.md`
- `prompts/4-video-clipping-captions.md`

## Budget summary (foundation phase)

| Item | Monthly |
|------|---------|
| Cursor Pro | $20 |
| Claude Pro | $20 |
| API keys (combined) | $50–150 |
| n8n/Make (when wired) | $20–30 |
| **Total** | **~$110–220** |

3-month foundation estimate: **$330–660** (month 1 higher due to prompt tuning).

## Claude Max downgrade timing

Keep Claude Max through the first MAS scaffold sprint. Downgrade to Pro once:

- [ ] `scaffold_client.py --dry-run` passes
- [ ] Agent Teams routes to `client-lead` successfully
- [ ] First real client scaffold completes

Freed ~$180/mo from Max → reallocate to API caps.
