# Start MAS orchestrator with Claude Code Remote Control (Max subscription).
# Requires: claude CLI, full-scope /login (not setup-token), workspace trust in MAS.

$ErrorActionPreference = "Stop"
$MasRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $MasRoot

# Force Max-subscription auth path for this launcher.
if ($env:ANTHROPIC_API_KEY) {
    Remove-Item Env:ANTHROPIC_API_KEY -ErrorAction SilentlyContinue
    Write-Host "Cleared ANTHROPIC_API_KEY in this session."
}

Write-Host "Starting MAS Orchestrator with Remote Control..."
Write-Host "  Workspace: $MasRoot"
Write-Host "  Mobile: Claude app -> Code -> 'MAS Orchestrator'"
Write-Host "  Web:    https://claude.ai/code"
Write-Host ""

& claude --remote-control "MAS Orchestrator"
