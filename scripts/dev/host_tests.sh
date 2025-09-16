#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/../.."  # repo root

echo "== compose ps =="
docker compose ps || true

echo "== Local health =="
echo -n "AI : "; curl -i -s http://127.0.0.1:8001/healthz | head -n 5 || true
echo -n "UI : "; curl -i -s http://127.0.0.1:8501/_stcore/health | head -n 5 || true

echo "== detect tunnel URL =="
LOG="/tmp/cloudflared.log"
if [[ -f "$LOG" ]]; then
  TUN="$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOG" | tail -n 1 || true)"
fi
if [[ -z "${TUN:-}" ]]; then
  echo "[WARN] No trycloudflare URL found yet. Is host_tunnel.sh running?"
else
  echo "TUN=$TUN"
  echo "== TUN health =="
  curl -i -s "$TUN/healthz" | head -n 20 || true

  echo "== Preflight (CORS) OPTIONS =="
  curl -i -s -X OPTIONS \
    -H "Origin: https://ai-auditor-87.streamlit.app" \
    -H "Access-Control-Request-Method: POST" \
    "$TUN/analyze" | head -n 40 || true
fi

echo "== Streamlit Cloud health =="
curl -i -s https://ai-auditor-87.streamlit.app/_stcore/health | head -n 5 || true

echo "== git info =="
git rev-parse --abbrev-ref HEAD || true
git log -1 --oneline || true

echo "== tail (ai/ui) =="
docker compose logs -n 120 ai | tail -n 120 || true
docker compose logs -n 120 ui | tail -n 120 || true

echo "DONE host_tests"
