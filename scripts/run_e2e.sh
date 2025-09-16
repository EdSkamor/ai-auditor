#!/usr/bin/env bash
set -e

echo "🚀 Uruchamianie testów E2E dla AI Auditor..."

# Konfiguracja środowiska
export AIAUDITOR_PASSWORD="TwojPIN123!"
export BACKEND_URL="http://localhost:8000"
export BASIC_AUTH_USER="user"
export BASIC_AUTH_PASS="TwojPIN123!"
export RUN_E2E="1"

# Sprawdź czy backend jest uruchomiony
echo "🔍 Sprawdzam czy backend jest uruchomiony..."
if ! curl -s http://localhost:8000/healthz > /dev/null; then
    echo "❌ Backend nie jest uruchomiony na localhost:8000"
    echo "💡 Uruchom backend: uvicorn local_test.server:app --port 8000"
    exit 1
fi

echo "✅ Backend działa, uruchamiam testy E2E..."

# Uruchom testy E2E
pytest -m e2e -v tests/test_e2e.py

echo "✅ Testy E2E zakończone pomyślnie!"
