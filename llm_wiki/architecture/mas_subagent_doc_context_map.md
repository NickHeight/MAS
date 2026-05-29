# MAS Sub-Agent Documentation Context Map

**Generated:** 2026-05-26  
**Source cache:** `C:/Users/Nicol/MAS/.firecrawl/mas-docs/`  
**Purpose:** Tell future MAS sub-agents which public documentation to load for each domain before planning or implementation.

## Access Model

- Use Firecrawl for public docs, public websites, public API references, and broad research.
- Use Cursor/Chrome browser control for logged-in/private surfaces after Nick signs in manually.
- Firecrawl's cloud browser does not automatically inherit local Chrome cookies or Skool login state.
- For private Skool content, extract summaries and actionable patterns only; do not bulk-copy private course material.

## Core Agent Infrastructure

Use for `orchestrator`, `architect-lead`, `tests-lead`, and any task changing MAS routing, skills, MCPs, or agent workflows.

- `.firecrawl/mas-docs/core-agent/claude-code-skills.md`
- `.firecrawl/mas-docs/core-agent/claude-code-mcp.md`
- `.firecrawl/mas-docs/core-agent/claude-code-features-overview.md`
- `.firecrawl/mas-docs/search-claude-code-agent-infra.json`

Context to extract:

- Skill structure and invocation boundaries.
- MCP configuration and authentication patterns.
- Subagent/tooling capabilities.
- Hooks, slash commands, and extension points.
- When to use durable instructions vs on-demand docs.

## Automation Domain

Use for `backend-lead` automation work, Make.com/n8n workflow engineering, webhook debugging, scenario design, and workflow handoffs.

- `.firecrawl/mas-docs/automation/n8n-webhook-node.md`
- `.firecrawl/mas-docs/automation/n8n-error-handling.md`
- `.firecrawl/mas-docs/automation/make-webhooks.md`
- `.firecrawl/mas-docs/search-n8n-workflow-docs.json`
- `.firecrawl/mas-docs/search-make-api-docs.json`

Context to extract:

- Webhook trigger semantics.
- Error handling and retry patterns.
- Payload shape, auth, and response behavior.
- Operational limits and testing workflow.

## Client Systems

Use for `client-lead`, `upwork-ops`, PM sync, client onboarding, Airtable/Monday reconciliation, and source-of-truth automation.

- `.firecrawl/mas-docs/client-systems/monday-api-basics.md`
- `.firecrawl/mas-docs/client-systems/monday-graphql-overview.md`
- `.firecrawl/mas-docs/client-systems/airtable-web-api-getting-started.md`
- `.firecrawl/mas-docs/search-monday-api-docs.json`
- `.firecrawl/mas-docs/search-airtable-api-docs.json`

Context to extract:

- Monday GraphQL query/mutation shape.
- Board, item, column, and webhook basics.
- Airtable base/table/record semantics.
- Linked record handling and field typing.

## Integrations

Use for payment, messaging, notifications, and client delivery systems.

- `.firecrawl/mas-docs/integrations/twilio-messaging-webhooks.md`
- `.firecrawl/mas-docs/integrations/twilio-message-resource.md`
- `.firecrawl/mas-docs/integrations/stripe-webhooks.md`
- `.firecrawl/mas-docs/integrations/stripe-checkout-sessions.md`
- `.firecrawl/mas-docs/search-twilio-messaging-docs.json`
- `.firecrawl/mas-docs/search-stripe-api-docs.json`

Context to extract:

- Twilio inbound/outbound message payloads.
- SMS/MMS status callback behavior.
- Stripe webhook verification and event handling.
- Checkout Session lifecycle and required server endpoints.

## Firecrawl / Research Agent Context

Use for research, website scraping, competitor research, documentation ingest, and public data extraction.

- `.firecrawl/mas-docs/search-firecrawl-docs.json`
- Existing global KB page: `C:/Users/Nicol/.claude/kb/wiki/entities/firecrawl-cli.md`

Context to extract:

- Search vs scrape vs map vs crawl vs agent boundaries.
- When to prefer public crawl vs logged-in browser.
- Output organization and `.firecrawl/` cache hygiene.

## Auxiliary Docs To Map Later

Map these only when a task needs them:

- GitHub CLI and GitHub Actions docs for PR/CI automation.
- Figma MCP and Code Connect docs for design-to-code/code-to-design work.
- Netlify and Vercel deployment docs for web delivery.
- Supabase docs for auth/database/RLS work.
- Google Sheets/Drive APIs for client reporting workflows.
- Slack/Telegram/Discord MCP docs for channel-based agent operation.
- Upwork-facing tooling docs if an official/API-accessible route becomes available.
- Skool member content after manual login, summarized by newest/highest-signal posts.

## Recommended Sub-Agent Prompt Snippet

Before a sub-agent starts domain work:

> Load `llm_wiki/architecture/mas_subagent_doc_context_map.md`. Select only the docs for your assigned domain. Summarize the relevant API/tool constraints in 5 bullets before planning. Do not load every cached file unless the task spans multiple domains.

