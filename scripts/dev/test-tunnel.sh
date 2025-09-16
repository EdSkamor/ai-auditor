#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

echo "🌐 Testing tunnel connection..."

if [[ ! -f /tmp/cloudflared-ai.log ]]; then
    echo "❌ Cloudflared log not found. Run: ./scripts/dev/tunnel.sh"
    exit 1
fi

TUN=$(./scripts/dev/tun-url.sh)
echo "Tunnel URL: $TUN"

echo "🔍 Testing tunnel endpoints..."

# Test healthz
echo "Testing /healthz..."
if curl -s "$TUN/healthz" > /dev/null; then
    echo "✅ /healthz OK"
else
    echo "❌ /healthz FAILED"
    exit 1
fi

# Test analyze
echo "Testing /analyze..."
JSON='{"prompt":"test","max_new_tokens":50}'
if curl -s -H "Content-Type: application/json" -d "$JSON" "$TUN/analyze" > /dev/null; then
    echo "✅ /analyze OK"
else
    echo "❌ /analyze FAILED"
    exit 1
fi

# Test CORS preflight
echo "Testing CORS preflight..."
if curl -s -X OPTIONS \
    -H "Origin: https://ai-auditor-87.streamlit.app" \
    -H "Access-Control-Request-Method: POST" \
    "$TUN/analyze" > /dev/null; then
    echo "✅ CORS preflight OK"
else
    echo "❌ CORS preflight FAILED"
    exit 1
fi

echo "✅ Tunnel tests completed successfully!"
echo "Set in Streamlit Cloud: AI_API_BASE=$TUN"
