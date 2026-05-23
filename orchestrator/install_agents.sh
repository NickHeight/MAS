#!/usr/bin/env bash
# Install MAS-specific subagents to ~/.claude/agents/
# Usage: bash orchestrator/install_agents.sh [--force]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENTS_SRC="$SCRIPT_DIR/agents"
CLAUDE_AGENTS="$HOME/.claude/agents"
FORCE=""

if [ "$1" = "--force" ]; then
  FORCE="true"
fi

mkdir -p "$CLAUDE_AGENTS"

for agent in "$AGENTS_SRC"/*.md; do
  [ -f "$agent" ] || continue
  name=$(basename "$agent")
  dest="$CLAUDE_AGENTS/$name"
  if [ -f "$dest" ] && [ -z "$FORCE" ]; then
    echo "EXISTS (use --force to overwrite): $dest"
  else
    cp "$agent" "$dest"
    echo "INSTALLED: $name -> $dest"
  fi
done

echo ""
echo "MAS agents installed. Available Team Leads:"
echo "  - client-lead (client-bootstrap, upwork-ops stub)"
echo "  - content-lead (content stub, Phase 2)"
