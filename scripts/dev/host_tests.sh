#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../"

echo "== compose ps =="
docker compose ps || true

echo "== local AI health (head) =="
curl -i -s http://127.0.0.1:8001/healthz | head -n 20 || true

echo "== local UI health (head) =="
curl -i -s http://127.0.0.1:8501/_stcore/health | head -n 20 || true

echo "== detect TUN =="
TUN=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflared.log | head -n 1 || true)
echo "TUN=${TUN:-<none>}"

if [[ -n "${TUN:-}" ]]; then
  echo "== TUN /healthz (head) =="
  curl -i -s "$TUN/healthz" | head -n 20 || true

  echo "== Preflight (CORS) from Streamlit Cloud =="
  curl -i -s -X OPTIONS \
    -H "Origin: https://ai-auditor-87.streamlit.app" \
    -H "Access-Control-Request-Method: POST" \
    "$TUN/analyze" | head -n 40 || true
fi

echo "== tail logs: ai =="
docker compose logs -n 200 ai | tail -n 120 || true

echo
echo "== tail logs: ui =="
docker compose logs -n 200 ui | tail -n 120 || true

echo
echo "== git info =="
git rev-parse --abbrev-ref HEAD || true
git log -1 --oneline || true
