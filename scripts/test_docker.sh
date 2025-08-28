#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# 0) pliki Docker/CI
./scripts/add_docker_and_ci.sh >/dev/null

# 1) build
docker build -t ai-auditor:local .

# 2) run (port 8585 żeby nie kłócił się z lokalnym 8501)
CID=$(docker run -d -p 8585:8501 --rm --name ai-auditor-test ai-auditor:local)
trap 'docker rm -f "$CID" >/dev/null 2>&1 || true' EXIT

# 3) czekaj aż wstanie i sprawdź health
for i in {1..30}; do
  if curl -fsS http://localhost:8585/healthz >/dev/null 2>&1; then
    echo "[PASS] container healthy at http://localhost:8585"
    exit 0
  fi
  sleep 1
done

echo "[FAIL] container did not become healthy"
docker logs "$CID" || true
exit 1
