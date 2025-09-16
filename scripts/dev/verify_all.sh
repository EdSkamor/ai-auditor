#!/usr/bin/env bash
set -euo pipefail

echo "🔧 AI Auditor - Weryfikacja kompletna"
echo "======================================"

# Sprawdź czy jesteśmy w właściwym repo
if [[ ! -f "docker-compose.yml" ]]; then
    echo "❌ Błąd: uruchom skrypt z katalogu ai-auditor-clean"
    echo "   cd /home/romaks/ai_2/ai-auditor-clean"
    exit 1
fi

echo "📁 Katalog: $(pwd)"
echo "🐳 Docker Compose: $(docker compose version 2>/dev/null || echo 'nie dostępny')"
echo ""

# 1. Sprzątanie i start
echo "🧹 Sprzątanie i start serwisów..."
docker compose down -v --remove-orphans || true
docker compose up -d --build

echo ""
echo "📊 Status kontenerów:"
docker compose ps

echo ""
echo "📋 Logi AI (ostatnie 60 linii):"
docker compose logs -n 120 ai | tail -n 60 || true

echo ""
echo "📋 Logi UI (ostatnie 60 linii):"
docker compose logs -n 120 ui | tail -n 60 || true

echo ""
echo "🏥 Testy zdrowia lokalne:"
echo "AI healthz:"
curl -s http://127.0.0.1:8001/healthz || echo "❌ AI nie odpowiada"
echo ""
echo "UI health:"
curl -s http://127.0.0.1:8501/_stcore/health || echo "❌ UI nie odpowiada"

echo ""
echo "🌐 Uruchamianie tunelu..."
pkill -f cloudflared || true
nohup cloudflared tunnel --url http://127.0.0.1:8001 --no-autoupdate > /tmp/cloudflared-ai.log 2>&1 &

# Czekaj na URL tunelu
echo "⏳ Czekam na URL tunelu (max 25s)..."
TUN=""
for i in {1..25}; do
  TUN=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflared-ai.log | tail -1 || true)
  [ -n "${TUN:-}" ] && break
  sleep 1
  echo -n "."
done
echo ""

if [[ -z "${TUN:-}" ]]; then
    echo "❌ Nie udało się uzyskać URL tunelu"
    echo "Logi cloudflared:"
    tail -20 /tmp/cloudflared-ai.log || true
    exit 1
fi

echo "✅ Tunel URL: $TUN"

echo ""
echo "🏥 Testy zdrowia przez tunel:"
echo "AI healthz przez tunel:"
curl -i "$TUN/healthz" | sed -n '1,20p' || echo "❌ Tunel nie odpowiada"

echo ""
echo "📋 Dostępne endpointy (OpenAPI):"
curl -s "$TUN/openapi.json" | jq '.paths | keys' || echo "❌ Nie można pobrać OpenAPI"

echo ""
echo "🧪 Testy endpointu /analyze:"
JSON='{"prompt":"hello","max_new_tokens":50}'

echo "Lokalnie (bez auth):"
LOCAL_CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "Content-Type: application/json" -d "$JSON" http://127.0.0.1:8001/analyze || echo "000")
echo "LOCAL: $LOCAL_CODE"

echo "Przez tunel (bez auth):"
TUN_CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "Content-Type: application/json" -d "$JSON" "$TUN/analyze" || echo "000")
echo "TUN: $TUN_CODE"

# Jeśli 401, sprawdź z Basic Auth
if [[ "$LOCAL_CODE" == "401" || "$TUN_CODE" == "401" ]]; then
    echo ""
    echo "🔐 Testy z Basic Auth (endpoint wymaga autoryzacji):"
    echo "Lokalnie z auth:"
    LOCAL_AUTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" -u 'user:TwojPIN123!' -H "Content-Type: application/json" -d "$JSON" http://127.0.0.1:8001/analyze || echo "000")
    echo "LOCAL_AUTH: $LOCAL_AUTH_CODE"

    echo "Przez tunel z auth:"
    TUN_AUTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" -u 'user:TwojPIN123!' -H "Content-Type: application/json" -d "$JSON" "$TUN/analyze" || echo "000")
    echo "TUN_AUTH: $TUN_AUTH_CODE"
fi

echo ""
echo "🌐 Test CORS preflight (Streamlit Cloud):"
curl -i -X OPTIONS \
  -H "Origin: https://ai-auditor-87.streamlit.app" \
  -H "Access-Control-Request-Method: POST" \
  "$TUN/analyze" | sed -n '1,30p' || echo "❌ CORS preflight nie działa"

echo ""
echo "📋 Podsumowanie:"
echo "================"
echo "TUN=$TUN"
echo "LOCAL_CODE=$LOCAL_CODE"
echo "TUN_CODE=$TUN_CODE"
if [[ "$LOCAL_CODE" == "401" || "$TUN_CODE" == "401" ]]; then
    echo "LOCAL_AUTH_CODE=$LOCAL_AUTH_CODE"
    echo "TUN_AUTH_CODE=$TUN_AUTH_CODE"
fi

echo ""
echo "🎯 Następne kroki:"
echo "1. Jeśli wszystko OK (200), ustaw w Streamlit Cloud:"
echo "   AI_API_BASE=$TUN"
echo "2. Jeśli 401, endpoint wymaga Basic Auth"
echo "3. Jeśli 404, sprawdź ścieżki w OpenAPI powyżej"
echo "4. Jeśli CORS błąd, sprawdź konfigurację w app/main.py"
