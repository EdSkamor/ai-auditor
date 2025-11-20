#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Starting AI Auditor (Docker stack)..."

# Start services in background (build only if needed)
docker compose up -d

echo "⏳ Waiting for services to become healthy..."
sleep 20

echo "🤖 AI service health:"
if curl -s http://127.0.0.1:8001/healthz > /dev/null; then
  curl -s http://127.0.0.1:8001/healthz
  echo
else
  echo "❌ AI docker health failed (port 8001)"
fi

echo
echo "🖥️ UI service health:"
if curl -s http://127.0.0.1:8501/_stcore/health > /dev/null; then
  echo "ok"
else
  echo "❌ UI docker health failed (port 8501)"
fi
