#!/usr/bin/env bash
set -euo pipefail

LOG="/tmp/cloudflared.log"
: > "$LOG"

echo "Starting cloudflared quick tunnel to http://127.0.0.1:8001 ..."
cloudflared tunnel --url http://127.0.0.1:8001 --no-autoupdate 2>&1 | tee -a "$LOG" | sed -nE 's@.*(https://[a-z0-9-]+\.trycloudflare\.com).*@\1@p' &
PID=$!

# Czekamy aż w logu pojawi się URL
for i in {1..30}; do
  TUN="$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOG" | head -n 1 || true)"
  if [[ -n "${TUN:-}" ]]; then
    echo "TUN=$TUN"
    break
  fi
  sleep 1
done

if [[ -z "${TUN:-}" ]]; then
  echo "[WARN] No trycloudflare URL found yet. Check $LOG"
fi

echo "cloudflared running (PID=$PID). Keep this terminal open."
wait $PID
