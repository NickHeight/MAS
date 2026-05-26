# Security boundaries — per-agent API key scope

## The rule

Every API key used by a workflow is scoped to **exactly one client**. No agent — Bentley or Katya — ever has the ability to act on another client's data.

| Agent | Client scope | Lives on | Reads/writes |
|-------|--------------|----------|--------------|
| **Bentley** (Hermes Agent) | HIRO / Elijah Booker | Hiro's Mac Mini M4 | Hiro's HubSpot, Hiro's Twilio number, hiro@* Gmail aliases, Hiro's Calendly/Outlook/Google Calendar, Hiro's social accounts |
| **Katya** (Hermes Agent) | Height Consulting | Nick's machine / VPS | Height's HubSpot, Height's Twilio number, nick@* Gmail aliases, Nick's Calendly/Outlook/Google Calendar, Nick's social accounts |

**No shared credentials.** Same workflow JSON, different env files, different n8n credential records.

## Why this matters

If Bentley were ever to get a Height-Consulting API key, an LLM prompt-injection bug, a confused-deputy issue, or even a typo in a workflow could push messages from Hiro's outreach pipeline into Nick's HubSpot. From Nick's clients' perspective: a stranger just texted them claiming to be a CPA. That's an immediate trust failure and probably a TCPA / CAN-SPAM violation depending on the channel.

This is also why we're choosing Path A architecture (n8n owns I/O, agents own AI). With Path B/C, the agent process is the one holding the bot tokens and would be a single mistake away from cross-contamination.

## Concrete mechanics

### 1. Two separate n8n instances (recommended)

| Instance | Owns | Credentials |
|----------|------|-------------|
| `n8n-hiro` (on Hiro's Mac Mini OR on a Hiro-only VPS) | HIRO production workflows | Twilio HIRO, HubSpot HIRO, Gmail Hiro@*, Calendly HIRO, etc. |
| `n8n-nick` (on Nick's machine OR a Nick-only VPS) | Height Consulting workflows + the testbed for everything | Twilio Height, HubSpot Height, Gmail nick@*, Calendly Nick, etc. |

Same workflow JSON deploys to both. Different `.env`. Different credential records. Different n8n user accounts on each instance.

### 2. Two separate Hermes agents

| Agent | Hermes runtime | `~/.hermes/.env` contents |
|-------|----------------|---------------------------|
| Bentley | Hiro's Mac Mini | Anthropic key, Telegram token (Hiro's bot), HubSpot HIRO Private App, GHL HIRO (read-only standby), no Nick-scope keys at all |
| Katya | Nick's machine | Anthropic key, Telegram token (Nick's bot), HubSpot Height Private App, no Hiro-scope keys at all |

The Anthropic key can be the same (it's not client-scoped — it's billed to your master account), but everything else MUST be different.

### 3. n8n → agent HTTP routing

When a workflow needs AI judgment (qualification, copy generation, briefing narration), it calls `$env.KATYA_HTTP_URL` or `$env.BENTLEY_HTTP_URL`. **The env var that's set on each n8n instance determines which agent it talks to.** A workflow doesn't choose at runtime — it can't, because the other agent's URL isn't reachable from this instance.

In the lead-gen workflow:

```
url: "={{ $env.KATYA_HTTP_URL || $env.BENTLEY_HTTP_URL }}"
```

This pattern works because only one is ever set on a given n8n instance. If both are set, that instance has a misconfiguration — investigate immediately.

### 4. Audit log

Every workflow that writes to HubSpot, sends SMS, or sends email must log:
- Timestamp
- Workflow name
- Target identifier (contact_email or contact_id)
- Channel used
- Outcome

Log destinations: n8n executions panel (built-in), plus optional Monday item update for high-signal events. If a cross-tenant write ever happens, the audit log is how you catch it.

## What to do when adding a new credential

1. Choose: HIRO-scope or Height-scope?
2. Create the credential record in the corresponding n8n instance only.
3. Add the env var name + scope to `ENV-VARS.md`.
4. NEVER copy a credential between instances. If a key needs to exist in both, **provision a separate key from the source service** (e.g. two HubSpot Private Apps, one per portal).

## What to do if you suspect cross-contamination

1. Stop the suspect workflow (deactivate in n8n).
2. Pull the n8n execution log — look for any item with a `contact_email` or `phone` that doesn't belong to that instance's tenant.
3. Revoke the suspect credential immediately.
4. If outbound messages went out: file a record of who was contacted, draft an apology/correction sequence, decide whether legal notice is required.
5. Post-mortem in `llm_wiki/postmortems/` with the env-var or workflow change that caused the bleed.

## Why we're not using one shared n8n instance with credential ACLs

In principle n8n Enterprise has role-based credential access — you could grant per-workflow access to per-credential. But:

- We're on n8n self-hosted (or single-tenant cloud), not Enterprise.
- Even Enterprise ACLs are a soft boundary — an admin (you) can always bypass them.
- Two separate instances is a hard boundary at the OS/network level. A misconfigured env var on n8n-hiro can't even reach Height's Twilio account.

The cost of two instances is ~$5-10/month extra hosting. Cheaper than one cross-tenant incident.
