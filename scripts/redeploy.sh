#!/usr/bin/env bash
# redeploy.sh — rebuild images and FORCE-RECREATE containers so the latest build
# is served (data preserved). Use after code changes.
#   ./scripts/redeploy.sh         # all services
#   ./scripts/redeploy.sh web     # just the frontend container
set -euo pipefail
cd "$(dirname "$0")/.."

echo "Rebuilding + recreating ${*:-all services}..."
docker compose up -d --build --force-recreate "$@"

sleep 4
if idx=$(curl -fsS http://localhost:8080 2>/dev/null); then
  js=$(printf '%s' "$idx" | grep -oE 'src="(/assets/[^"]+\.js)"' | sed -E 's/.*"(.*)".*/\1/' | head -1)
  echo "Web is serving bundle: $js"
fi
echo "Done. Hard-refresh the browser (Ctrl+Shift+R) at http://localhost:8080"
