#!/usr/bin/env bash
set -euo pipefail

# Ngrok tunnel with Basic Auth for AI Auditor backend
echo "🚀 Starting Ngrok tunnel with Basic Auth for AI Auditor backend..."
echo "📍 Tunneling http://127.0.0.1:8000 to public HTTPS with Basic Auth"
echo "🔐 Credentials: user:TwojPIN123!"

# Start tunnel with Basic Auth
ngrok http 8000 --basic-auth "user:TwojPIN123!"
