# 2026-05-25 — Bentley/Telegram debug + bg-session stash

## What happened

Background session opened to investigate HIRO's Bentley (Hermes Agent) timing
out on Telegram. Two concurrent issues collided:

1. **Primary task** — diagnosed dual-poller 409 Conflict (BoBBoe still polling
   the same `TELEGRAM_BOT_TOKEN` alongside Bentley). Documented as the same
   incident class as 2026-04-26. Fix block delivered for user to execute while
   remoted into the Mac Mini: cold-standby (sed-disable BoBBoe's token, drop
   pending updates, `launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway`).

2. **Hook loop** — stop hook fired repeatedly on 5 pre-existing dirty files
   from before the session started. After user authorization, those files
   were stashed (reversible) so the hook would release.

## Stashed contents — worth a look on next interactive pass

Stash name: `bg-session 2026-05-25 pause: in-flight pre-session work`
Restore with: `git stash pop` (or `git stash apply stash@{0}` to keep)

| File | Notable diff | Action |
|------|--------------|--------|
| `CLAUDE.md` | Guardrail line update: "HIRO client runs Hermes in production; MAS does not host Hermes runtime (client Mac Mini)" replacing old "Hermes remains eval-only" line | Already present in live `CLAUDE.md` (linter or user re-applied during session) — stash entry is redundant, safe to drop on pop |
| `scripts/upwork_audit.py` | `KNOWN_BUNDLES` display_name: `OpenClaw / HIRO` → `Hermes / HIRO` | **Keep** — matches the wiki rename already committed in `llmwiki/OpenClaw/log.md` (2026-05-25 entry) |
| `llm_wiki/audits/upwork_gap_report.md` | Re-audited 2026-05-25. HIRO message tag count jumped 47 → **897**; Marc 136 → **2539**. XML file count 286 → 288. Also flags orphan `Weekly-Review-2026-05-24.md` at Upwork root | **Keep** — vastly more SMS context now available for HIRO/Marc workflows. Worth referencing when building the SMS → Monday pipeline |
| `llm_wiki/audits/upwork_inventory.json` | Refreshed by re-audit run | Keep — paired with gap report |
| `llm_wiki/audits/orphan_moves.json` | Refreshed by re-audit run | Keep — paired with gap report |

## Recommended next step

```powershell
cd C:\Users\Nicol\MAS
git stash pop                  # restore all 5 files
# CLAUDE.md will likely conflict (line was re-applied during session) — resolve
# by keeping the live version. Other 4 files apply cleanly.
git status
```

Then commit the 4 audit/script changes as a single `audit: refresh upwork
inventory + rename to Hermes / HIRO` commit when ready.

## Bentley/Telegram diagnostic — quick-paste link

See `BOBBOE-TO-NICK.md` 2026-04-21 entry and `docs/hermes-startup-runbook.md`
§3 for the original incident context. The fix block from today's session is
in the chat transcript — not copied here to avoid drift if it gets revised.
