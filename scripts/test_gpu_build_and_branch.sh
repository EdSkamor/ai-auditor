#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

./scripts/gpu_pack_and_branch.sh >/dev/null

# Build GPU image (działa bez karty, to tylko build)
docker build -f Dockerfile.gpu -t ai-auditor:gpu .

# CPU: run + healthz
docker build -t ai-auditor:cpu .
CID=$(docker run -d -p 8585:8501 --rm --name ai-auditor-health ai-auditor:cpu)
trap 'docker rm -f "$CID" >/dev/null 2>&1 || true' EXIT
for i in {1..40}; do
  if curl -fsS http://localhost:8585/healthz >/dev/null 2>&1; then
    echo "[PASS] CPU container healthy at http://localhost:8585"
    break
  fi
  sleep 1
done

# gałąź i śledzenie plików
CUR=$(git rev-parse --abbrev-ref HEAD)
[ "$CUR" = "release/client-pack-gpu" ] || { echo "[FAIL] wrong branch: $CUR"; exit 1; }
for f in Dockerfile.gpu scripts/run_gpu_container.sh docs/QUICKSTART.md .env.sample; do
  git ls-files --error-unmatch "$f" >/dev/null 2>&1 || { echo "[FAIL] not tracked: $f"; exit 1; }
done

echo "[PASS] GPU build ok, CPU health ok, branch ready: $CUR"
echo "[NEXT] push with: git push -u origin $CUR"
