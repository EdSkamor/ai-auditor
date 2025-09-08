#!/bin/bash

# AI Auditor - Start AI Server
# Uruchamia lokalny serwer AI z modelem Llama 3

echo "🚀 Uruchamianie serwera AI Auditor..."

# Sprawdź czy jesteśmy w wirtualnym środowisku
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Aktywuj wirtualne środowisko: source venv/bin/activate"
    exit 1
fi

# Sprawdź czy GPU jest dostępne
if command -v nvidia-smi &> /dev/null; then
    echo "✅ GPU NVIDIA wykryte:"
    nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader,nounits
else
    echo "⚠️  GPU NVIDIA nie wykryte - model będzie działał na CPU (wolniej)"
fi

# Ustaw zmienne środowiskowe
export TRANSFORMERS_VERBOSITY=error
export AI_SERVER_URL="http://localhost:8000"

echo "🔧 Konfiguracja:"
echo "   - Serwer AI: $AI_SERVER_URL"
echo "   - Model: Llama 3 8B + LoRA adapter"
echo "   - Temperatura: 0.8"
echo "   - Timeout: 30s"

# Uruchom serwer
echo "🌐 Uruchamianie serwera na porcie 8000..."
echo "📱 Panel Streamlit będzie dostępny na: http://localhost:8501"
echo "🤖 API AI będzie dostępne na: http://localhost:8000"
echo ""
echo "Naciśnij Ctrl+C aby zatrzymać serwer"
echo ""

# Uruchom serwer w tle
uvicorn server:app --host 0.0.0.0 --port 8000 --reload &
SERVER_PID=$!

# Poczekaj chwilę na uruchomienie
sleep 3

# Sprawdź czy serwer działa
if curl -s http://localhost:8000/healthz > /dev/null; then
    echo "✅ Serwer AI uruchomiony pomyślnie!"
    echo "🔗 Sprawdź status: http://localhost:8000/healthz"
    echo "🔗 Sprawdź gotowość modelu: http://localhost:8000/ready"
else
    echo "❌ Błąd uruchamiania serwera AI"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

# Funkcja cleanup
cleanup() {
    echo ""
    echo "🛑 Zatrzymywanie serwera AI..."
    kill $SERVER_PID 2>/dev/null
    echo "✅ Serwer zatrzymany"
    exit 0
}

# Przechwyć sygnał przerwania
trap cleanup SIGINT SIGTERM

# Czekaj na zakończenie
wait $SERVER_PID
