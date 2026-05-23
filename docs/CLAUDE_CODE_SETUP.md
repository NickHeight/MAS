# Claude Code — MAS Orchestrator + Mobile Remote Control

Use **Claude Max subscription auth** for the orchestrator. Keep pay-as-you-go keys in `.env` only for non-Anthropic scripts (Gemini, OpenAI, xAI).

## Two auth pools (do not mix them up)

| Surface | Auth | Notes |
|---------|------|-------|
| **Claude Code orchestrator** (Agent Teams, MAS routing) | Max via **`/login`** (claude.ai) | No `ANTHROPIC_API_KEY` needed |
| **Mobile Remote Control** | Same **full-scope `/login` session** | Does **not** work with `setup-token` / `CLAUDE_CODE_OAUTH_TOKEN` |
| **Headless CI / scripted `claude` CLI** | `claude setup-token` → `CLAUDE_CODE_OAUTH_TOKEN` | Inference-only; no Remote Control |
| **Raw Python `anthropic` SDK** | `ANTHROPIC_API_KEY` from Console | Separate billing; not included in Max |

**Rule:** If `ANTHROPIC_API_KEY` is set anywhere (`.env`, PowerShell profile, system env), Claude Code prefers it over Max. For subscription billing, leave `ANTHROPIC_API_KEY` unset.

MAS `.env` intentionally has no Anthropic key — OpenAI / Google / xAI are for Phase 2 pipelines and `repo_analyzer.py --use-gemini`.

---

## Start the MAS orchestrator with mobile access

### One-time setup

1. **Sign in with full scope** (required for Remote Control):
   ```powershell
   cd c:\Users\Nicol\MAS
   claude
   /login
   ```
   Choose **claude.ai** (Max account). Do **not** use `claude setup-token` for mobile — that token is inference-only.

2. **Trust the workspace** — accept the trust dialog the first time you run `claude` in `c:\Users\Nicol\MAS`.

3. **Install agents** (if not done):
   ```powershell
   powershell -File orchestrator/install_agents.ps1 -Force
   ```

4. **Claude mobile app** — same account as Max. Tap **Code** in nav to see sessions.

### Every session (desk → phone)

**Option A — interactive + remote (recommended)**

```powershell
cd c:\Users\Nicol\MAS
claude --remote-control "MAS Orchestrator"
```

Or use the helper script:

```powershell
powershell -File scripts/start-orchestrator-remote.ps1
```

- Terminal stays interactive on the PC
- Scan QR or open session at [claude.ai/code](https://claude.ai/code)
- Phone: Claude app → **Code** → session **MAS Orchestrator** (green dot = online)
- Full local context: `TASKS.md`, wikis, MCP servers, Agent Teams

**Option B — server mode (phone-only driving)**

```powershell
cd c:\Users\Nicol\MAS
claude remote-control --name "MAS Orchestrator"
```

Press **spacebar** for QR. Process waits for mobile connections.

**Option C — enable for all sessions**

Inside any Claude Code session: `/config` → **Enable Remote Control for all sessions** → `true`.

---

## Talking to the orchestrator from your phone

Once connected, prompt naturally — the session reads `CLAUDE.md` and `TASKS.md` on startup:

- *"What's on the task board?"*
- *"Run Upwork audit and summarize gaps"*
- *"Route this to client-bootstrap: scaffold dry-run for Acme Corp"*
- *"Notify me when the audit finishes"* (push notifications; enable in `/config` → Push when Claude decides)

Remote Control runs **on your PC**. Laptop must stay awake and online; closing the terminal ends the session.

---

## When you need `setup-token` later

For unattended scripts (not mobile):

```powershell
claude setup-token
# paste into env as CLAUDE_CODE_OAUTH_TOKEN — never commit
```

Use for CI or cron-style `claude -p "..."` — **not** for Remote Control.

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| Remote Control requires claude.ai subscription | `/login` with claude.ai; unset `ANTHROPIC_API_KEY` |
| Requires a **full-scope** login token | You're on `setup-token`; run `/login` instead |
| Session not in mobile list | Same account on phone; PC session must be active |
| Version too old | `claude --version` — need ≥ 2.1.51 (you have 2.1.148 ✓) |

Docs: [Remote Control](https://code.claude.com/docs/en/remote-control) · [Authentication](https://code.claude.com/docs/en/authentication)
