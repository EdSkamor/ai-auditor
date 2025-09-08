#!/bin/bash

# AI Auditor - Start Streamlit with AI Connection
# Uruchamia Streamlit z połączeniem do lokalnego serwera AI

echo "🚀 Uruchamianie Streamlit z połączeniem AI..."

# Sprawdź czy jesteśmy w wirtualnym środowisku
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Aktywuj wirtualne środowisko: source venv/bin/activate"
    exit 1
fi

# Sprawdź czy serwer AI działa
echo "🔍 Sprawdzanie połączenia z serwerem AI..."
if curl -s http://localhost:8000/healthz > /dev/null; then
    echo "✅ Serwer AI dostępny na localhost:8000"
    
    # Sprawdź gotowość modelu
    if curl -s http://localhost:8000/ready | grep -q '"model_ready":true'; then
        echo "✅ Model AI gotowy"
    else
        echo "⏳ Model AI się dogrzewa..."
    fi
else
    echo "⚠️  Serwer AI niedostępny na localhost:8000"
    echo "   Uruchom najpierw: ./start_ai_server.sh"
    echo "   Lub uruchom Streamlit w trybie mock (bez AI)"
    read -p "Czy chcesz kontynuować w trybie mock? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Ustaw zmienne środowiskowe
export AI_SERVER_URL="http://localhost:8000"
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"

echo "🔧 Konfiguracja Streamlit:"
echo "   - Port: 8501"
echo "   - Serwer AI: $AI_SERVER_URL"
echo "   - Tryb: $(if curl -s http://localhost:8000/healthz > /dev/null; then echo "AI + Mock"; else echo "Mock"; fi)"
echo ""

# Uruchom Streamlit
echo "🌐 Uruchamianie Streamlit..."
echo "📱 Panel będzie dostępny na: http://localhost:8501"
echo "🔗 Status AI: http://localhost:8000/healthz"
echo ""
echo "Naciśnij Ctrl+C aby zatrzymać"
echo ""

streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
