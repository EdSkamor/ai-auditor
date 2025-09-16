#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/../.."  # repo root

echo "🔍 AI Auditor - Quick Diagnostics"
echo "================================="

echo "== docker compose ps =="
docker compose ps || true

echo ""
echo "== AI logs (last 200 lines) =="
docker compose logs -n 200 ai | tail -n 200 || true

echo ""
echo "== UI logs (last 200 lines) =="
docker compose logs -n 200 ui | tail -n 200 || true

echo ""
echo "== Local health checks =="
echo "AI healthz:"
curl -s http://127.0.0.1:8001/healthz || echo "❌ AI not responding"
echo ""

echo "UI health:"
curl -s http://127.0.0.1:8501/_stcore/health || echo "❌ UI not responding"
echo ""

echo "== Tunnel diagnostics =="
LOG="/tmp/cloudflared.log"
if [[ -f "$LOG" ]]; then
  TUN="$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOG" | tail -n 1 || true)"
  if [[ -n "${TUN:-}" ]]; then
    echo "TUN=$TUN"
    echo "Tunnel health:"
    curl -i -s "$TUN/healthz" | head -n 20 || echo "❌ Tunnel not responding"
  else
    echo "❌ No tunnel URL found in $LOG"
  fi
else
  echo "❌ No cloudflared log found at $LOG"
fi

echo ""
echo "== Git info =="
git rev-parse --abbrev-ref HEAD || true
git log -1 --oneline || true

echo ""
echo "DONE diagnostics"
