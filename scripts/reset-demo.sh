#!/usr/bin/env bash
# reset-demo.sh — wipe the database, rebuild, and pre-code the worklist to a
# PRISTINE demo state. Run before a demo (or between dry-runs).
#   ./scripts/reset-demo.sh            # full reset + pre-code
#   ./scripts/reset-demo.sh --no-code  # reset only, leave charts uncoded
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example — add your ANTHROPIC_API_KEY for live coding."
fi

echo "Resetting demo: wiping volume, rebuilding, reseeding..."
docker compose down -v
docker compose up -d --build

printf "Waiting for API"
ready=""; haskey=""
for _ in $(seq 1 60); do
  if m=$(curl -fsS http://localhost:8000/api/meta 2>/dev/null); then
    ready=1
    printf '%s' "$m" | grep -q '"llm_available": *true' && haskey=1
    break
  fi
  sleep 3; printf "."
done
echo
[ -n "$ready" ] || { echo "API did not become ready in time." >&2; exit 1; }

if [ "${1:-}" = "--no-code" ]; then
  echo "Skipping pre-coding. Charts uncoded; click 'Run autonomous coding' in the UI."
elif [ -z "$haskey" ]; then
  echo "ANTHROPIC_API_KEY not set -> charts left uncoded. Add it to .env, then ./scripts/redeploy.sh api."
else
  echo "Pre-coding the worklist (real Claude calls, ~5-8 min)..."
  curl -fsS -X POST http://localhost:8000/api/coding/run-all && echo
fi

echo "Pristine. UI: http://localhost:8080   API docs: http://localhost:8000/docs"
echo "(Hard-refresh the browser with Ctrl+Shift+R.)"
