#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

./scripts/client_pack.sh >/dev/null

docker build -t ai-auditor:cpu .
CID=$(docker run -d -p 8585:8501 --rm --name ai-auditor-health ai-auditor:cpu)
trap 'docker rm -f "$CID" >/dev/null 2>&1 || true' EXIT

for i in {1..40}; do
  if curl -fsS http://localhost:8585/healthz >/dev/null 2>&1; then
    echo "[PASS] container healthy at http://localhost:8585"
    echo "[NEXT] push branch: git push -u origin release/client-pack"
    exit 0
  fi
  sleep 1
done

echo "[FAIL] container did not become healthy"
docker logs "$CID" || true
exit 1
