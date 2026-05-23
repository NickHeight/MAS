# Start MAS orchestrator with Claude Code Remote Control (Max subscription).
# Requires: claude CLI, full-scope /login (not setup-token), workspace trust in MAS.

$ErrorActionPreference = "Stop"
$MasRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $MasRoot

if ($env:ANTHROPIC_API_KEY) {
    Write-Warning "ANTHROPIC_API_KEY is set — Claude Code may bill API instead of Max. Unset for subscription auth."
}

Write-Host "Starting MAS Orchestrator with Remote Control..."
Write-Host "  Workspace: $MasRoot"
Write-Host "  Mobile: Claude app -> Code -> 'MAS Orchestrator'"
Write-Host "  Web:    https://claude.ai/code"
Write-Host ""

& claude --remote-control "MAS Orchestrator"
