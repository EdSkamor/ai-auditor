#!/usr/bin/env bash
set -euo pipefail

# Cloudflared tunnel for AI Auditor backend
echo "🚀 Starting Cloudflared tunnel for AI Auditor backend..."
echo "📍 Tunneling http://127.0.0.1:8000 to public HTTPS"

# Start tunnel
cloudflared tunnel --url http://127.0.0.1:8000 --no-autoupdate
