# Install MAS-specific subagents to ~/.claude/agents/
# Usage: powershell -File orchestrator/install_agents.ps1 [-Force]

param([switch]$Force)

$AgentsSrc = Join-Path $PSScriptRoot "agents"
$ClaudeAgents = Join-Path $env:USERPROFILE ".claude\agents"

New-Item -ItemType Directory -Force -Path $ClaudeAgents | Out-Null

Get-ChildItem -Path $AgentsSrc -Filter "*.md" | ForEach-Object {
    $dest = Join-Path $ClaudeAgents $_.Name
    if ((Test-Path $dest) -and -not $Force) {
        Write-Host "EXISTS (use -Force to overwrite): $dest"
    } else {
        Copy-Item $_.FullName $dest -Force
        Write-Host "INSTALLED: $($_.Name) -> $dest"
    }
}

Write-Host ""
Write-Host "MAS agents installed. Available Team Leads:"
Write-Host "  - client-lead (client-bootstrap, upwork-ops stub)"
Write-Host "  - content-lead (content stub, Phase 2)"
