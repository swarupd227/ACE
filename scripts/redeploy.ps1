<#
  redeploy.ps1 - rebuild images and FORCE-RECREATE containers so the browser gets
  the latest build (data is preserved). Use after code changes.

  Usage:
    .\scripts\redeploy.ps1            # all services
    .\scripts\redeploy.ps1 web        # just the web (frontend) container
    .\scripts\redeploy.ps1 api        # just the api (backend) container
#>
param([string]$Service = "")

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

if ($Service) {
  Write-Host "Rebuilding + recreating '$Service'..." -ForegroundColor Cyan
  docker compose up -d --build --force-recreate $Service
} else {
  Write-Host "Rebuilding + recreating all services..." -ForegroundColor Cyan
  docker compose up -d --build --force-recreate
}

Start-Sleep -Seconds 4
try {
  $idx = (Invoke-WebRequest "http://localhost:8080" -UseBasicParsing -TimeoutSec 10).Content
  $js = ([regex]::Match($idx, 'src="(/assets/[^"]+\.js)"')).Groups[1].Value
  Write-Host "Web is serving bundle: $js" -ForegroundColor Green
} catch {
  Write-Host "(web not reachable yet - give it a few seconds)" -ForegroundColor Yellow
}
Write-Host "Done. Hard-refresh the browser (Ctrl+Shift+R) at http://localhost:8080" -ForegroundColor Green
