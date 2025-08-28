#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker build -f Dockerfile.gpu -t ai-auditor:gpu .
echo "[PASS] GPU image built: ai-auditor:gpu"
