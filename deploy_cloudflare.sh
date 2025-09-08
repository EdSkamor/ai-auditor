#!/bin/bash
# AI Auditor Cloudflare Deployment Script

set -e

echo "🚀 Rozpoczynam wdrożenie AI Auditor na Cloudflare..."

# Sprawdź zmienne środowiskowe
if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo "❌ Błąd: CLOUDFLARE_API_TOKEN nie jest ustawiony"
    exit 1
fi

if [ -z "$CLOUDFLARE_ACCOUNT_ID" ]; then
    echo "❌ Błąd: CLOUDFLARE_ACCOUNT_ID nie jest ustawiony"
    exit 1
fi

if [ -z "$CLOUDFLARE_ZONE_ID" ]; then
    echo "❌ Błąd: CLOUDFLARE_ZONE_ID nie jest ustawiony"
    exit 1
fi

echo "✅ Zmienne środowiskowe sprawdzone"

# Utwórz KV namespaces
echo "📦 Tworzenie KV namespaces..."
python3 cloudflare_config.py create-kv

# Wdróż Worker
echo "👷 Wdrażanie Cloudflare Worker..."
wrangler deploy

# Utwórz rekordy DNS
echo "🌐 Tworzenie rekordów DNS..."
python3 cloudflare_config.py create-dns

# Skonfiguruj reguły bezpieczeństwa
echo "🔒 Konfigurowanie reguł bezpieczeństwa..."
python3 cloudflare_config.py create-security

echo "✅ Wdrożenie zakończone pomyślnie!"
echo "🌐 AI Auditor dostępny pod adresem: https://ai-auditor.ai-auditor-client.com"
echo "🔑 Hasło dostępu: TwojPIN123!"
