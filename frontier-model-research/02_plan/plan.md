---
tags: [plan, frontier-models, orchestration, mas]
date: 2026-05-24
status: draft-pending-approval
prompt: c:/Users/Nicol/.claude/kb/_reference/frontier-model-research/01_prompt/prompt.md
plan_file_origin: c:/Users/Nicol/.claude/plans/figure-out-a-way-zesty-lightning.md
---

# Plan: Frontier-Model Selection Research + Auto-Login + North Star Autonomy

Response to [[../../01_prompt/prompt]] (canonical copy in Global KB).

## Context

Nick is building a 4-tier agentic orchestration system (Orchestrator → Manager → Supervisor → Worker) and wants:

1. **A research-backed frontier-model selection matrix** stored in the LLM wiki, so every future session has a "selection context" page to consult when deciding which model runs which role. The matrix must evolve over time as new models ship — kept, swapped, or logged-as-worse.
2. **The auto-login subproblem solved**: stop manually logging into sites like Twilio Console for read-only status checks. Today's session lost time when Chrome's session expired; the orchestrator should have either (a) used a non-browser path (API token) or (b) deferred non-blocking work and kept driving toward the North Star.
3. **A "North Star" mindset captured as durable instructions** — when a path fails, try alternatives before pausing for human input. Don't lose sight of the actual deliverable (e.g., "give Marc an update today") because one sub-step is blocked.

This is groundwork for the long-term self-improving agent system Nick is building. The plan deliberately uses today's frontier models (Anthropic Claude Mythos Preview, Opus 4.7, GPT-5.5, Gemini 3.5 Flash, etc.) but is written so it survives model churn.

## Findings from Phase 1 exploration

**Frontier models, May 2026 (from WebSearch):**

| Lab | Top model | Specialty | Notable |
|---|---|---|---|
| Anthropic | Claude Mythos Preview (preview) | Long-horizon coding | 93.9% SWE-bench Verified, cleared 32-step cyber range in single run |
| Anthropic | Claude Opus 4.7 (current session) | Complex multi-file coding + 1M ctx | 87.6% SWE-bench Verified, 64.3% SWE-bench Pro |
| Anthropic | Claude Sonnet 4.6 | Cost-balanced coding | Mid-tier go-to |
| Anthropic | Claude Haiku 4.5 | Fast / cheap | Log analysis, mechanical work |
| OpenAI | GPT-5.5 (released Apr 23, 2026) | Agentic terminal | #1 SWE-bench 88.7%, 82.7% Terminal-Bench 2.0 |
| OpenAI | GPT-5.3 Codex | Code | 85% SWE-bench |
| OpenAI | GPT-5 | "Unified system" | Internal router picks sub-model per request |
| Google | Gemini 3.1 Pro | Scientific reasoning | 94.3% GPQA Diamond (leader) |
| Google | Gemini 3.5 Flash | Price/perf for agent workflows | 76.2% Terminal-Bench 2.1, 83.6% MCP Atlas, $1.50/$9.00 per 1M |
| DeepSeek | V4 Pro Max | Open-weight challenger | 80.6% SWE-bench |
| Kimi | K2.6 | Open-weight | 80.2% SWE-bench |

**Existing local routing config (from reads):**

- `~/.claude/agents/orchestrator.md` already uses `model: opus`; 7 other team-leads exist (architect-lead, backend-lead, frontend-lead, tests-lead, research-lead, client-lead, content-lead).
- `CLAUDE.md` has a "Model Selection & Routing" table: Opus for arch/plan, Sonnet for single-file edits, Haiku for log analysis, Pi+Gemini Flash for free scaffolding.
- `~/.claude/skills/pi-agent/SKILL.md` is the canonical Pi/Gemini Flash dispatcher (free tier, daily-limit guarded, auto-falls-back to Haiku).
- MAS orchestrator (`MAS/orchestrator/domains.yaml`) maps domains → team-leads (all on Sonnet currently).
- No existing page captures **per-role model preference** with current frontier IDs or a swap-log.

**Auto-login state (from reads):**

- `~/Upwork/llmwiki/_shared/playbooks/unattended-ops/entities/chrome-automation-profile.md` documents `C:/Users/Nicol/chrome-automation/` — a dedicated Chrome user-data-dir with persistent cookies for Upwork (per playbook step 2 of profile setup) but NOT Twilio Console, Stripe Dashboard, Meta BM, or Bouncie dev portal.
- No documented 1Password / Bitwarden / secret-manager pattern.
- Twilio creds (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`) are referenced in the Turo repo's Netlify env but NOT in the orchestrator's shell env — that's why today's Twilio check fell back to Chrome.

## The plan

### Goal A — Frontier-Model Selection KB (cross-project, in Global KB)

Build a structured set of pages at **`~/.claude/kb/_reference/frontier-model-selection/`** (new folder). Cross-link from Upwork wiki where relevant.

**Pages to create:**

| File | Purpose |
|---|---|
| `00_overview.md` | Entry point. Summarises the current state in 200 words. Pointer to the matrix + log. |
| `model-roster-2026-05.md` | The May 2026 snapshot table (above). Frozen snapshot — never edit; create a new dated file next quarter. |
| `role-to-model-matrix.md` | The decision artifact. For each of the 7 roles (orchestrator, manager, supervisor, worker, research, code-review, drafting), name the primary model + fallback chain + rationale. |
| `selection-criteria.md` | How to evaluate a new model when it launches. Benchmarks to check, decision rule, log format. |
| `evolution-log.md` | Append-only. Each entry: date, model swapped in/out, reason, observed outcome. This is the "what works / what doesn't" memory across sessions. |
| `cost-quality-tradeoffs.md` | Cost-per-task table per role + per model. Updated quarterly with current pricing. |

**Initial role → model assignments** (will be the matrix's seed values):

| Role | Primary | Fallback | Why |
|---|---|---|---|
| Orchestrator (Tier 1) | **Claude Opus 4.7** (1M ctx) | Claude Mythos Preview when GA | Long-context decomposition; already on it. Mythos when stable for the cyber-range-style 32-step planning. |
| Manager / Team Lead (Tier 2) | **Claude Sonnet 4.6** | GPT-5.5 for terminal-heavy domains | Domain decomposition; Sonnet is cost-aligned. GPT-5.5 better when the domain is terminal/CLI-heavy. |
| Supervisor (Tier 3) | **Claude Sonnet 4.6** | Gemini 3.5 Flash for QA loops | Specialty management. Flash for cheap QA passes. |
| Worker (Tier 4) | **Claude Haiku 4.5** | Gemini 3.5 Flash (via Pi) | Mechanical single-task work. Pi+Flash for boilerplate to preserve Max-plan budget. |
| Research / Explore | **Claude Opus 4.7** (when ctx matters) OR Gemini 3.1 Pro (when web/scientific) | Sonnet 4.6 for code-base only | Opus for deep multi-source synthesis, Gemini Pro for GPQA-style reasoning. |
| Code review (fresh-context) | **Claude Haiku 4.5** sub-agent | Gemini 3.5 Flash | Cheap, fresh eyes, structured output. Quality is good enough for the second-pass role. |
| Drafting (client deliverables) | **Claude Opus 4.7** | Claude Sonnet 4.6 | Tone + structure matter; cost matters less because per-deliverable usage is low. |

### Goal B — Auto-Login / Persistent-Auth Strategy

Build **`~/.claude/kb/_reference/persistent-auth-strategy.md`** — one cross-project page mapping each external service to its preferred Claude-access mechanism, ranked by Claude-autonomy.

**Ranking (highest autonomy first):**

1. **MCP server** — Claude calls it directly. Best. (Stripe, Monday, Airtable, Asana, Slack, Supabase, Figma, Vercel already on this tier.)
2. **API token in env var** — Bash `curl` with env-loaded creds. (Twilio, Make.com, n8n, Netlify, Cloudflare belong here.)
3. **Chrome automation profile with persistent cookies** — `chrome-automation/` dir; assumes the profile is already logged in. (Upwork is here.)
4. **User intervention** — Claude asks user to log in. **Last resort only.**

**For each service Marc/Turo uses, the page documents:**
- Service name
- Tier 1/2/3/4 (above)
- The actual mechanism (MCP name, env var name, profile name)
- The path Claude should attempt first, and the fallback chain

**Concrete migrations to do as part of this work:**

| Service | Current state | Target |
|---|---|---|
| Twilio Console | Manual browser login | Tier 2: Bash + `curl` with `$TWILIO_ACCOUNT_SID` and `$TWILIO_AUTH_TOKEN` exported in shell profile (or loaded via skill) |
| Stripe Dashboard | Manual browser login (Nick has Admin) | Tier 1: Stripe MCP (`mcp__plugin_stripe_stripe__authenticate`) — already available, just needs auth flow |
| Bouncie dev portal | Manual browser login | Tier 3: log in once in `chrome-automation/`, persist cookies. (Bouncie has no MCP / public API for dev-app creds retrieval.) |
| Meta Business Manager | Manual browser login | Tier 3: same — log in once in `chrome-automation/`, persist cookies. |

### Goal C — North Star Behavior Rules (durable instructions)

Append to **`CLAUDE.md`** (under a new section "Driving Toward the Goal"):

> When a sub-step is blocked, the Orchestrator must:
> 1. **Identify the actual deliverable** the user asked for (e.g., "give Marc an update today" — Twilio is one *input*, not the deliverable).
> 2. **Try alternative paths** before pausing for human input: MCP → API token → Chrome → manual. Try at least 2 before escalating.
> 3. **Decide if the sub-step is critical-path or nice-to-have.** If it's nice-to-have, document the gap (e.g., "Twilio status not verified this session — last-known: TFV pending, A2P in progress") and **continue toward the deliverable**.
> 4. **Never let a blocked sub-step block the user-visible deliverable** unless the entire deliverable depends on it.

Add a single bullet to the global Session Habits: *"Don't pause for low-stakes uncertainty — log the gap and continue toward the North Star."*

### Goal D — Self-Improvement Loop

Add a `## Logging model swaps` section to `~/.claude/agents/orchestrator.md` rules:

> When you dispatch a model that's different from `role-to-model-matrix.md`'s default, append a line to `evolution-log.md`:
> `YYYY-MM-DD | role | from-model → to-model | reason | observed outcome`
>
> Quarterly review (or on new model launch): re-read `evolution-log.md`. Promote consistent winners to the matrix; demote consistent losers.

## Critical files to read/write

**To read (already covered in Phase 1):**
- `~/.claude/agents/orchestrator.md` (template for adding sections)
- `c:/Users/Nicol/CLAUDE.md` (template for North Star append)
- `c:/Users/Nicol/.claude/kb/_reference/three-layer-architecture.md` (pattern template for new KB pages — `concept → reference → playbook` shape)
- `~/Upwork/llmwiki/_shared/playbooks/unattended-ops/entities/chrome-automation-profile.md` (already read; reference for Tier-3 Chrome state)

**To create:**
- `~/.claude/kb/_reference/frontier-model-selection/00_overview.md`
- `~/.claude/kb/_reference/frontier-model-selection/model-roster-2026-05.md`
- `~/.claude/kb/_reference/frontier-model-selection/role-to-model-matrix.md`
- `~/.claude/kb/_reference/frontier-model-selection/selection-criteria.md`
- `~/.claude/kb/_reference/frontier-model-selection/evolution-log.md`
- `~/.claude/kb/_reference/frontier-model-selection/cost-quality-tradeoffs.md`
- `~/.claude/kb/_reference/persistent-auth-strategy.md`

**To edit:**
- `c:/Users/Nicol/CLAUDE.md` — add "Driving Toward the Goal" section + Session-Habits bullet.
- `~/.claude/agents/orchestrator.md` — add "Model dispatch" + "Logging model swaps" sections.
- `~/.claude/kb/index.md` — add catalog entries for the new pages.

## Verification

1. **Pages exist and link:** `ls ~/.claude/kb/_reference/frontier-model-selection/` returns 6 files. `~/.claude/kb/index.md` shows the new entries. Cross-links resolve.
2. **Role matrix is actionable:** open `role-to-model-matrix.md` — for every one of the 7 roles, there's a primary, a fallback, and a one-line rationale.
3. **Auto-login: Twilio API path works.** Run `curl -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN" https://verify.twilio.com/v2/Services` (or equivalent) and confirm 200. If creds aren't yet in the shell env, document the gap + the path to populate them.
4. **North Star rule in CLAUDE.md:** new section is present and is reachable from the Table of Contents.
5. **Evolution log seeded:** first entry in `evolution-log.md` is dated 2026-05-24 with "matrix established — seed values from May 2026 frontier survey."

## Sources

- [SWE-bench Verified Leaderboard May 2026](https://andrew.ooo/answers/swe-bench-verified-leaderboard-may-2026/)
- [Best AI Models May 2026](https://www.buildfastwithai.com/blogs/latest-best-ai-models-may-2026)
- [State of AI: May 2026](https://press.airstreet.com/p/state-of-ai-may-2026)
- [Frontier AI Field Is Splitting (Q1 2026)](https://medium.com/@marc.bara.iniesta/q1-2026-the-frontier-ai-field-is-splitting-b5b7f6a49ba9)
