#!/bin/bash
# AI Auditor - Start Local Test

echo "🚀 Uruchamianie AI Auditor w trybie lokalnym..."

# Check Python
if ! python3 --version &> /dev/null; then
    echo "❌ Python 3 nie jest zainstalowany"
    exit 1
fi

echo "✅ Python 3 dostępny"

# Start web interface
echo "🌐 Uruchamianie interfejsu web..."
streamlit run web/panel_audytora.py --server.port 8501 --server.address 0.0.0.0 &

# Start API server
echo "🔌 Uruchamianie serwera API..."
uvicorn server:app --host 0.0.0.0 --port 8000 &

echo "✅ AI Auditor uruchomiony!"
echo "🌐 Interfejs Web: http://localhost:8501"
echo "🔌 Serwer API: http://localhost:8000"
echo "📚 Dokumentacja: http://localhost:8000/docs"

# Keep script running
wait
