#!/usr/bin/env bash
set -euo pipefail
TS=$(date +%Y%m%d-%H%M%S)
OUT="$HOME/Pulpit/dla AI/DEPLOY_REPORT_${TS}.md"
mkdir -p "$HOME/Pulpit/dla AI"

{
  echo "# AI Auditor — Deployment Report ($TS)"
  echo
  echo "## Git"
  git remote -v || true
  git rev-parse --abbrev-ref HEAD || true
  git log -1 --oneline || true

  echo
  echo "## Docker"
  docker --version || true
  docker compose ps || true

  echo
  echo "### AI /healthz"
  curl -s http://127.0.0.1:8001/healthz || true

  echo
  echo "### UI /_stcore/health"
  curl -s http://127.0.0.1:8501/_stcore/health || true

  TUN=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflared.log | head -n 1 || true)
  echo
  echo "## Tunnel"
  echo "TUN=${TUN:-<none>}"

  if [[ -n "${TUN:-}" ]]; then
    echo
    echo "### TUN /healthz (head)"
    curl -i -s "$TUN/healthz" | head -n 20 || true

    echo
    echo "### CORS preflight (head)"
    curl -i -s -X OPTIONS \
      -H "Origin: https://ai-auditor-87.streamlit.app" \
      -H "Access-Control-Request-Method: POST" \
      "$TUN/analyze" | head -n 40 || true
  fi

  echo
  echo "## Logs (tail ai/ui)"
  docker compose logs -n 200 ai | tail -n 120 || true
  echo
  docker compose logs -n 200 ui | tail -n 120 || true
} > "$OUT"

echo "✅ Raport zapisany: $OUT"
