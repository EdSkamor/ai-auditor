#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/../.."  # repo root

echo "== compose down =="
docker compose down -v --remove-orphans || true

echo "== build (no cache only for AI if needed) =="
docker compose build ai
docker compose build ui

echo "== compose up -d =="
docker compose up -d

echo "== wait for AI health =="
for i in {1..90}; do
if curl -fsS http://127.0.0.1:8001/healthz >/dev/null; then
  echo "AI healthy"
  break
fi
sleep 1
if [[ $i -eq 90 ]]; then
  echo "AI not healthy after 90s"; exit 1
fi
done

echo "== wait for UI health =="
for i in {1..60}; do
if curl -fsS http://127.0.0.1:8501/_stcore/health >/dev/null; then
  echo "UI healthy"
  break
fi
sleep 1
if [[ $i -eq 60 ]]; then
  echo "UI not healthy after 60s"; exit 1
fi
done

echo "== sample analyze (no auth) =="
curl -s -X POST -H 'Content-Type: application/json' \
-d '{"prompt":"hello","max_new_tokens":10}' \
http://127.0.0.1:8001/analyze || true

echo "DONE host_setup"
