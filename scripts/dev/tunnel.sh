#!/usr/bin/env bash
set -euo pipefail

rm -f /tmp/cloudflared-ai.log
echo "Starting cloudflared tunnel to http://127.0.0.1:8001 ..."
cloudflared tunnel --url http://127.0.0.1:8001 --no-autoupdate 2>&1 | tee /tmp/cloudflared-ai.log
