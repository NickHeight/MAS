# MAS — Multi-Agent System

Unified domain-routing orchestrator for Upwork delivery and social media pipelines.

## Quick start

```powershell
# Install MAS Team Lead subagents (Windows)
powershell -File orchestrator/install_agents.ps1

# Or on Git Bash / Linux
bash orchestrator/install_agents.sh

# Dry-run client scaffold
python scripts/scaffold_client.py --name "Test Client" --slug test-client --modules web --dry-run

# Audit entire Upwork root (existing clients + internal systems)
python scripts/upwork_audit.py --root ~/Upwork

# Scan SMS/XML message backups on OneDrive (Marc + HIRO threads)
python scripts/scan_message_backups.py

# Apply safe cross-links for client bundles
python scripts/upwork_audit.py --root ~/Upwork --apply-cross-links --bundles turo,openclaw
```

## Docs

- [Cursor setup](docs/CURSOR_SETUP.md)
- [Obsidian setup](docs/OBSIDIAN_SETUP.md)
- [Orchestrator routing](orchestrator/router.md)
- [Domain registry](orchestrator/domains.yaml)

## Architecture

Extends existing team-of-teams at `C:/Users/Nicol/agentic/`. MAS adds domain routing and client scaffolding — it does not replace Claude Code Agent Teams.

## Phase status

| Domain | Status |
|--------|--------|
| client-bootstrap | Active |
| coding | Active (via architect-lead) |
| upwork-ops | Stub |
| automation | Stub |
| content | Stub |
