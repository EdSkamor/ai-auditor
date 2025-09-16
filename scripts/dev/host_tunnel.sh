#!/usr/bin/env bash
set -euo pipefail
LOG=/tmp/cloudflared.log
: > "$LOG"
echo "Running cloudflared (AI on 8001). Keep this tab open."
cloudflared tunnel --url http://127.0.0.1:8001 --no-autoupdate | tee -a "$LOG"
