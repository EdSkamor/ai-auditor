#!/bin/bash
# AI Auditor - RTX 4090 Start Script

echo "🚀 Starting AI Auditor on RTX 4090..."

# Activate virtual environment
source .venv/bin/activate

# Check GPU status
echo "🖥️ GPU Status:"
nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free --format=csv

# Start web interface
echo "🌐 Starting web interface..."
streamlit run web/auditor_panel.py --server.port 8501 --server.address 0.0.0.0 &

# Start API server
echo "🔌 Starting API server..."
uvicorn server:app --host 0.0.0.0 --port 8000 &

echo "✅ AI Auditor started!"
echo "🌐 Web Interface: http://localhost:8501"
echo "🔌 API Server: http://localhost:8000"
echo "📚 Documentation: http://localhost:8000/docs"

# Keep script running
wait
