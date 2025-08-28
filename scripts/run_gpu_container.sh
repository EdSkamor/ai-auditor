#!/usr/bin/env bash
set -euo pipefail
IMG="${1:-ai-auditor:gpu}"
docker image inspect "$IMG" >/dev/null 2>&1 || docker build -f Dockerfile.gpu -t "$IMG" .
docker run --gpus all --rm -p 8585:8501 --env-file .env.local \
  -v "$(pwd)/data:/app/data" -v "$(pwd)/logs:/app/logs" \
  "$IMG"
