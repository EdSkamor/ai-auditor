#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Starting AI Auditor locally..."

# Setup virtual environment
echo "📦 Setting up virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
pip -q install -r requirements.txt
pip -q install -e .

# Set default AI API base
export AI_API_BASE="${AI_API_BASE:-http://127.0.0.1:8001}"

# Start AI server in background
echo "🤖 Starting AI server..."
bash ./start_ai_server.sh &
AI_PID=$!

# Wait for AI server to be ready
echo "⏳ Waiting for AI server to be ready..."
sleep 3

# Check if AI server is running
if ! curl -s "${AI_API_BASE}/healthz" > /dev/null; then
    echo "❌ AI server failed to start. Check logs."
    exit 1
fi

echo "✅ AI server is ready at ${AI_API_BASE}"

# Start Streamlit
echo "🌐 Starting Streamlit UI..."
streamlit run streamlit_app_multipage.py --server.port 8501

# Cleanup on exit
trap "kill $AI_PID 2>/dev/null || true" EXIT
