#!/usr/bin/env bash
set -euo pipefail

JSON='{"prompt":"hello","max_new_tokens":50}'
BASIC_USER="user"
BASIC_PASS="TwojPIN123!"

echo "== Local (with Basic Auth) =="
curl -s http://127.0.0.1:8001/healthz || true
echo
curl -s -u "${BASIC_USER}:${BASIC_PASS}" -H "Content-Type: application/json" -d "$JSON" http://127.0.0.1:8001/analyze || true
echo

if [[ -f /tmp/cloudflared-ai.log ]]; then
  TUN=$(scripts/dev/tun-url.sh)
  echo "== Tunnel (${TUN}) with Basic Auth =="
  curl -s "${TUN}/healthz" || true
  echo
  curl -s -u "${BASIC_USER}:${BASIC_PASS}" -H "Content-Type: application/json" -d "$JSON" "${TUN}/analyze" || true
  echo
  echo "== CORS preflight (OPTIONS) =="
  curl -i -X OPTIONS \
    -H "Origin: https://ai-auditor-87.streamlit.app" \
    -H "Access-Control-Request-Method: POST" \
    "${TUN}/analyze" || true
else
  echo "Cloudflared log not found. Run scripts/dev/tunnel.sh in a separate terminal."
fi
