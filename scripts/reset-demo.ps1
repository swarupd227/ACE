<#
  reset-demo.ps1 - wipe the database, rebuild everything, and pre-code the worklist
  to a PRISTINE demo state. Run this before a demo (or between dry-runs).

  Usage:  .\scripts\reset-demo.ps1
  Skip the (slow) pre-coding:  .\scripts\reset-demo.ps1 -NoCode
#>
param([switch]$NoCode)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Write-Host "Created .env from .env.example - add your ANTHROPIC_API_KEY for live coding." -ForegroundColor Yellow
}

Write-Host "Resetting demo: wiping volume, rebuilding, reseeding..." -ForegroundColor Cyan
docker compose down -v
docker compose up -d --build

Write-Host -NoNewline "Waiting for API"
$ready = $false; $hasKey = $false
for ($i = 0; $i -lt 60; $i++) {
  try {
    $m = Invoke-RestMethod "http://localhost:8000/api/meta" -TimeoutSec 5
    $ready = $true; $hasKey = [bool]$m.llm_available; break
  } catch { Start-Sleep -Seconds 3; Write-Host -NoNewline "." }
}
Write-Host ""
if (-not $ready) { Write-Error "API did not become ready in time."; exit 1 }

if ($NoCode) {
  Write-Host "Skipping pre-coding (-NoCode). Charts are uncoded; click 'Run autonomous coding' in the UI." -ForegroundColor Yellow
} elseif (-not $hasKey) {
  Write-Host "ANTHROPIC_API_KEY not set; charts left uncoded." -ForegroundColor Yellow
  Write-Host "Add the key to .env, run .\scripts\redeploy.ps1 api, then 'Run autonomous coding'." -ForegroundColor Yellow
} else {
  Write-Host "Pre-coding the worklist (real Claude calls, ~5-8 min)..." -ForegroundColor Cyan
  $res = Invoke-RestMethod -Method Post "http://localhost:8000/api/coding/run-all" -TimeoutSec 1200
  Write-Host ("Coded {0} charts: STB {1} / QA {2} / Manual {3}" -f $res.coded, $res.lanes.STB, $res.lanes.QA, $res.lanes.MANUAL) -ForegroundColor Green
}

Write-Host "Pristine. UI: http://localhost:8080   API docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "(Hard-refresh the browser with Ctrl+Shift+R.)" -ForegroundColor Green
