# Frontier-model research — complete plan (executable)

**Date:** 2026-05-24  
**Source prompt:** [`~/.claude/kb/_reference/frontier-model-research/01_prompt/prompt.md`](c:/Users/Nicol/.claude/kb/_reference/frontier-model-research/01_prompt/prompt.md)  
**Companion KB:** [`model-routing-matrix.md`](c:/Users/Nicol/.claude/kb/_reference/frontier-model-research/model-routing-matrix.md), [`03_findings.md`](c:/Users/Nicol/.claude/kb/_reference/frontier-model-research/03_findings.md)  
**Note:** This artifact is deliberately independent of any other file in `02_plan/` (e.g. `plan.md`).  

---

## 1. Executive summary

The North Star prompt asks for six parallel capabilities: frictionless credential access for simple checks (Twilio et al.), **goal-first autonomy** when a path is blocked, a **four-tier decomposition** ladder, **evidence-backed self-improvement**, **proposal-time challenge-with-proof**, and **frontier-aware model routing** with logged performance.

This document is **research + operational convention**, not orchestration implementation. It gives:

1. A **repeatable evaluation rubric** and **fallback chains** by tier.  
2. A **blocked-step ladder** every orchestrator prompt can cite verbatim.  
3. A **Twilio / Console bypass matrix** (API keys, restricted keys, when Chrome+HITL is unavoidable).  
4. **Structured probe specs** so empirical scores can replace guesses on the next cadence run.  
5. **Logging schemas** for model outcomes and playbook promotion (aligned with four-tier ratchet discipline).

Vendor facts below are summarized from official docs and announcements **as of 2026-05-24**; re-verify on each quarterly refresh (see §8).

---

## 2. Research methodology

### 2.1 Role × capability rubric

Score each model **1–5** per dimension (half-points allowed). Record **one evidence line** per score (benchmark, probe result, vendor claim, or postmortem).

| Dimension | What “5” means |
|-----------|----------------|
| Long-horizon planning / architecture | Multi-phase tradeoffs, dependency ordering, reversible decisions |
| Multi-file implementation | Coherent edits across repo, refactor safety |
| Fast cheap research | Broad synthesis, citations, low $/answer |
| Tool-use reliability | CLI, MCP, browser automation, fewer spurious retries |
| Verification | Test runs, log triage, deterministic checks |
| Cost / latency / context fit | Fits budget and SLA for that tier |

**Interpretation:**

- **Orchestrator (tier 1):** Planning ≥ 4, tool-use ≥ 3, verification ≥ 3. Cost secondary for low-volume routing.  
- **Team Lead (tier 2):** Balanced Sonnet-equivalent baseline; Planning 3–4, implementation 4.  
- **Supervisor (tier 3):** Same as tier 2 or one notch cheaper if work is narrower.  
- **Worker / skill-step (tier 4):** Minimize latency and cost; Haiku-equivalent acceptable when skill is deterministic.  
- **External free lane:** Gemini Flash via Pi (`~/.claude/skills/pi-agent/SKILL.md`) for research/doc scaffolding only—not production commits without review.

### 2.2 Candidate pool (2026-05 snapshot)

**Anthropic (Claude API)** — [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview)

| Alias | Typical use |
|-------|-------------|
| `claude-opus-4-7` | Frontier reasoning & agentic coding; 1M context; flagship |
| `claude-sonnet-4-6` | Production default balance; 1M context |
| `claude-haiku-4-5` | Fast, cheap paths; ~200k context |

**Deprecation (plan migrations):** `claude-sonnet-4-20250514` and `claude-opus-4-20250514` deprecated; **retire by 2026-06-15** per Anthropic docs—migrate callers to Sonnet 4.6 / Opus 4.7.

**OpenAI (API)** — [Models](https://developers.openai.com/api/docs/models), [Pricing](https://openai.com/api/pricing/), changelog May 2026

| Model | Role |
|-------|------|
| `gpt-5.5` | OpenAI flagship for coding/pro reasoning; Responses + Chat API; reasoning effort knobs |
| `gpt-5.5-pro` | Higher-compute variant (Responses API; latency cost tradeoff) |
| `gpt-5.4` | Lower per-token frontier tier vs 5.5 |
| `gpt-5.4-mini` / `nano` | High-volume cheaper steps |

Snapshot IDs (e.g. `gpt-5.5-2026-04-23`) should be pinned in **`model-routing-matrix.md`** when behavior stability matters.

**Google (Pi / zero-cost lane)**  

- Gemini **2.x Flash** via `pi-agent` for research, doc generation, transcript-style tasks—not a substitute for signed-off production code paths.

### 2.3 Empirical probes (lightweight, repeatable)

Run the **same five probes** quarterly; append rows to **`model_perf_log`** (§7). Each probe: record model, snapshot ID, duration, estimated cost, pass/fail, retry count.

| ID | Probe | Success criteria |
|----|-------|------------------|
| P1 | Plan refactor across 5+ files with explicit rollback | Ordered steps + risk notes; human can execute without clarification |
| P2 | Tool-heavy: branch checkout, grep, edit, run single test command | Correct file touched; test outcome reported truthfully |
| P3 | Research brief with 5+ citations on a narrow topic | Every claim traced to URL or primary doc |
| P4 | Failing CI log triage (50–150 lines) | Root cause hypothesis + smallest next patch |
| P5 | “Better proposal” challenge | Alternative approach + evidence + migration cost vs user draft |

Prefer **masked or fixed seeds** where possible so models are comparable across quarters.

---

## 3. Tier × model recommendations (defaults + fallbacks)

These defaults align with [`wiki/concepts/four-tier-team-of-teams`](c:/Users/Nicol/.claude/kb/wiki/concepts/four-tier-team-of-teams.md) and extend the pool cross-vendor.

| Tier | Primary | Fallback chain | Avoid |
|------|---------|----------------|-------|
| 1 Orchestrator | Claude Opus 4.7 | GPT-5.5 → GPT-5.5-pro (hard problems only) | Haiku-only for orchestration sessions |
| 2 Team Lead | Claude Sonnet 4.6 | GPT-5.4 → Opus 4.7 escalation | opus-4 / sonnet-4 deprecated IDs |
| 3 Supervisor | Sonnet 4.6 | GPT-5.4-mini (narrow tasks) → Sonnet again | Delegating risky auth to workers |
| 4 Worker steps | Haiku 4.5 | GPT-5.4-nano → Sonnet fix loop | Opus per trivial skill step |
| Research / scaffolding | Gemini Flash (Pi) | Haiku → Sonnet if citations weak | Uncited Flash output merged as fact |

**Cross-vendor rule:** Prefer **single stack per session** (Anthropic-native OR OpenAI-native) to reduce harness mismatch; escalate across vendors only on repeated failure after logged attempt.

---

## 4. North Star / blocked-step policy (orchestrator text)

Operational ladder—**advance down the ladder, never deadlock on step 2.**

```
1 Deliverable_goal (explicit: who receives what artifact by when)
2 Deterministic_API_or_CLI       (REST, SDK, scripted query)
3 MCP_or_registered_bridge       (hosted connector with scoped token)
4 Headless_or_profiled_browser    (persistent Chrome profile; see unattended-ops playbook)
5 Partial_deliverable_plus_gaps     (ship value; list blockers separately)
6 HITL_checkpoint                 (credential, legal, MFA, destructive action—human only)
```

**Twilio-shaped example:**

- Prefer **Restricted API keys** scoped to Messaging/Flex/logs needed for status checks—not Console scraping.  
- If Console-only UI needed once, **scheduled HITL** or **recording + script** afterward to eliminate repeat logins—don’t brute-force unattended SSO unless policy allows.

See §5 for the full bypass matrix.

---

## 5. Twilio / “no manual login window” matrix

Goal: eliminate **interactive** Console login for *simple read-only ops* Nick described.

| Approach | Fits | Prerequisites | Risks | HITL |
|----------|------|---------------|-------|------|
| **REST + API Key SID/secret** (`-u KEY:SECRET`) | Programmatic pulls of messages/calls/logs | Key created once in Console ([API keys docs](https://www.twilio.com/docs/usage/api/key)) | Key leakage = account abuse | One-time Console for key issuance |
| **Standard vs Restricted keys** | Apply least privilege to automation | Restricted = v1 Key API + permission design | Mis-scoped → 403 loops | Rare permission updates |
| **Auth Token path** | Local dev only | Account SID + token | Higher blast radius vs keys | Prefer migrate off |
| **SDK / CLI in agent** | Same as REST; deterministic | Env vars (`TWILIO_API_KEY`, etc.) per [`api-keys-storage`](c:/Users/Nicol/.claude/kb/wiki/concepts/api-keys-storage.md) pointers | Repo leak | Rotate on exposure |
| **MCP wrapper** | If MCP server wraps Twilio with stored token | Server config | Custom server maintenance | Initial token UX |
| **Chrome user-data-dir persistence** ([unattended-ops entity](~/Upwork/llmwiki/_shared/playbooks/unattended-ops/entities/chrome-automation-profile.md)) | Only when APIs cannot surface the field | Maintain profile + SSO policy | SSO refresh, flaky selectors | Periodic re-auth |

**Generic pattern for “other consoles”:** inventory **public API**, **export**, **email report**, **webhook**, before browser automation.

---

## 6. Proposal-time delegation pattern

When a client asks for X:

1. **Replay constraints** explicitly (budget, deadline, integrations).  
2. **Dispatch** Tier 2→3 with “challenge allowed” instruction.  
3. **Accept counter-proposals only with:**  
   - References (docs, prior postmortems, benchmarks).  
   - Delta table: simpler? cheaper to maintain? quality? timeline?  
   - Blast-radius / rollback paragraph.  

If evidence bar not met → execute user plan with flagged risks instead of speculative rewrite.

---

## 7. Logging schemas

### 7.1 `model_perf_log` (append-only row)

Use YAML list or CSV—the matrix file holds the latest rollup.

```yaml
- date: '2026-05-24'
  probe_id: P2
  model: claude-sonnet-4-6
  snapshot: 'claude-sonnet-4-6'
  tier: Supervisor
  pass: true
  retries: 1
  wall_ms: 42000
  est_cost_usd: 0.12
  notes: 'Flaky first bash path; succeeded on rerun'
```

### 7.2 Playbook promotion (four-tier alignment)

Mirror [`four-tier-team-of-teams/README.md`](c:/Users/Nicol/.claude/kb/_reference/four-tier-team-of-teams/README.md):

1. Surprise / failure → **postmortem** in tier folder *or* `MAS/llm_wiki/postmortems/`  
2. Repeat ≥2× → **playbook**  
3. **Never** speculate in `reference.md` without citations from prior runs  

Model-specific lessons attach to **`model-routing-matrix.md` changelog**.

---

## 8. Frontier freshness cadence

| Cadence | Action |
|---------|--------|
| Weekly skim | Vendor changelogs (Anthropic/OpenAI/Google), Cursor/CC release notes affecting harness |
| Monthly | Rotate any pinned snapshot IDs hitting drift; update pricing row |
| Quarterly | Run probe suite P1–P5 across primary + challenger; revise defaults |
| On major release | Bump `routing_matrix.version` field; preserve previous row **as fallback** with “known limits” |

---

## 9. Explicit non-goals (this spike)

- No LangGraph / always-on service build (per MAS `CLAUDE.md`).  
- No auto-post or client-facing send without HITL.  
- No filling empty `four-tier-team-of-teams/**/reference.md` with guesses.

---

## 10. Definition of done (research spike checklist)

- [x] Quantitative rubric + probes defined (this file §2–3).  
- [x] Blocked-step policy written for orchestrator copy-paste (§4).  
- [x] Twilio/console bypass matrix + HITL boundaries (§5).  
- [x] Logging schemas (§7).  
- [x] Published to Global KB `_reference/frontier-model-research/` + `index`/`log` atomic update.  

---

## 11. Sources (selected)

- Anthropic Opus 4.7 announcement: https://www.anthropic.com/news/claude-opus-4-7  
- Claude model overview (API IDs, deprecation): https://platform.claude.com/docs/en/about-claude/models/overview  
- OpenAI API changelog May 2026 (GPT-5.5 release): https://developers.openai.com/api/docs/changelog  
- GPT-5.5 model card: https://developers.openai.com/api/docs/models/gpt-5.5  
- OpenAI pricing: https://openai.com/api/pricing/  
- Twilio API authentication basics: https://www.twilio.com/docs/usage/api/key  
- Twilio API requests (Basic auth modes): https://www.twilio.com/docs/usage/requests-to-twilio  
