#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../"

echo "== compose down =="
docker compose down -v --remove-orphans || true

echo "== build ai (opt no-cache) =="
if [[ "${1:-}" == "--no-cache" ]]; then
  docker compose build ai --no-cache
else
  docker compose build ai
fi

echo "== build ui =="
docker compose build ui

echo "== up -d =="
docker compose up -d

echo "== wait ai (healthz) =="
for i in {1..120}; do
  if curl -fsS http://127.0.0.1:8001/healthz >/dev/null; then
    echo "AI healthy ✅"; break
  fi
  sleep 1
done || true

echo "== ui health =="
curl -s http://127.0.0.1:8501/_stcore/health || true

echo "== compose ps =="
docker compose ps
