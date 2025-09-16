#!/usr/bin/env bash
set -euo pipefail

TUN=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflared-ai.log | tail -1 || true)
if [[ -z "${TUN}" ]]; then
  echo "Tunnel URL not found yet. Is cloudflared running?" >&2
  exit 1
fi
echo "${TUN}"
