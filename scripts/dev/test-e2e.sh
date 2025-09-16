#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

echo "🧪 Running E2E tests..."

# Set environment variables for tests
export RUN_E2E=1
export BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8001}"
export APP_URL="${APP_URL:-http://127.0.0.1:8501}"
export E2E_FRONT_TIMEOUT=10
export E2E_BACK_TIMEOUT=10

echo "Backend URL: $BACKEND_URL"
echo "App URL: $APP_URL"

# Check if services are running
echo "🔍 Checking if services are running..."

if ! curl -s "$BACKEND_URL/healthz" > /dev/null; then
    echo "❌ Backend not running at $BACKEND_URL"
    echo "Run: ./scripts/dev/up.sh"
    exit 1
fi

if ! curl -s "$APP_URL/_stcore/health" > /dev/null; then
    echo "❌ Frontend not running at $APP_URL"
    echo "Run: ./scripts/dev/up.sh"
    exit 1
fi

echo "✅ Services are running"

# Run tests
echo "🚀 Running pytest..."
python -m pytest tests/test_e2e.py -v --tb=short

echo "✅ E2E tests completed"
