#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

# sprzątanie ostrożne
pkill -f 'uvicorn|streamlit' || true
docker compose down -v --remove-orphans || true
docker container prune -f || true
docker network prune -f || true

# build + up
docker compose up -d --build

echo -e "\n== docker compose ps =="
docker compose ps || true

echo -e "\n== AI healthz (local) =="
curl -s http://127.0.0.1:8001/healthz || true

echo -e "\n== UI health (local) =="
curl -s http://127.0.0.1:8501/_stcore/health || true

echo -e "\nTip: logs -> docker compose logs -n 200 ai | ui"
