# 🚀 Wdrożenie AI Auditor na Cloudflare

## 📋 Wymagania

### 1. Konto Cloudflare
- Konto Cloudflare z aktywną domeną
- API Token z uprawnieniami:
  - `Zone:Zone:Read`
  - `Zone:Zone Settings:Edit`
  - `Account:Cloudflare Workers:Edit`
  - `Account:Account Settings:Read`

### 2. Zmienne środowiskowe
```bash
export CLOUDFLARE_API_TOKEN="your_api_token_here"
export CLOUDFLARE_ACCOUNT_ID="your_account_id_here"
export CLOUDFLARE_ZONE_ID="your_zone_id_here"
export CLOUDFLARE_DOMAIN="your-domain.com"
```

### 3. Narzędzia
- `wrangler` CLI (Cloudflare Workers CLI)
- `curl` lub `httpie` do testowania

## 🔧 Instalacja

### 1. Zainstaluj Wrangler CLI
```bash
npm install -g wrangler
# lub
curl -sS https://workers.cloudflare.com/install.sh | sh
```

### 2. Autoryzacja
```bash
wrangler login
```

### 3. Sprawdź konfigurację
```bash
wrangler whoami
```

## 🚀 Wdrożenie

### 1. Automatyczne wdrożenie
```bash
chmod +x deploy_cloudflare.sh
./deploy_cloudflare.sh
```

### 2. Ręczne wdrożenie

#### Krok 1: Utwórz KV Namespaces
```bash
wrangler kv:namespace create "AI_AUDITOR_FILES"
wrangler kv:namespace create "AI_AUDITOR_JOBS"
wrangler kv:namespace create "AI_AUDITOR_RESULTS"
```

#### Krok 2: Skonfiguruj wrangler.toml
Zaktualizuj `wrangler.toml` z rzeczywistymi ID namespaces.

#### Krok 3: Wdróż Worker
```bash
wrangler deploy
```

#### Krok 4: Utwórz rekordy DNS
```bash
# A record dla ai-auditor.your-domain.com
curl -X POST "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "A",
    "name": "ai-auditor",
    "content": "192.0.2.1",
    "ttl": 300,
    "proxied": true
  }'
```

#### Krok 5: Skonfiguruj reguły bezpieczeństwa
```bash
# Rate limiting
curl -X POST "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/firewall/rules" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "action": "rate_limit",
    "priority": 1,
    "paused": false,
    "description": "AI Auditor Rate Limiting",
    "filter": {
      "expression": "http.host eq \"ai-auditor.your-domain.com\""
    },
    "rate_limit": {
      "threshold": 100,
      "period": 60,
      "action": "block"
    }
  }'
```

## 🔒 Bezpieczeństwo

### 1. Autentykacja
- **Hasło dostępu**: `TwojPIN123!`
- **Typ**: Bearer Token w nagłówku `Authorization`
- **Format**: `Bearer TwojPIN123!`

### 2. Reguły bezpieczeństwa
- Rate limiting: 100 requestów/minutę
- Bot protection: Score < 30 = blokada
- File upload protection: Challenge dla `/upload`
- CORS: Ograniczony do domeny klienta

### 3. Szyfrowanie
- Wszystkie dane w KV są szyfrowane
- Klucz szyfrowania: `ai-auditor-encryption-key-2024`
- HTTPS wymagany dla wszystkich połączeń

## 📡 API Endpoints

### 1. Health Check
```bash
curl -H "Authorization: Bearer TwojPIN123!" \
  https://ai-auditor.your-domain.com/health
```

### 2. Upload File
```bash
curl -X POST \
  -H "Authorization: Bearer TwojPIN123!" \
  -F "file=@invoice.pdf" \
  https://ai-auditor.your-domain.com/upload
```

### 3. Start Audit
```bash
curl -X POST \
  -H "Authorization: Bearer TwojPIN123!" \
  -H "Content-Type: application/json" \
  -d '{
    "fileId": "file_abc123_1234567890",
    "auditType": "invoice_validation",
    "parameters": {
      "strict_mode": true,
      "include_ocr": true
    }
  }' \
  https://ai-auditor.your-domain.com/audit
```

### 4. Get Results
```bash
curl -H "Authorization: Bearer TwojPIN123!" \
  "https://ai-auditor.your-domain.com/results?jobId=job_xyz789_1234567890"
```

## 🔄 Integracja z lokalnym systemem

### 1. Webhook Configuration
Lokalny system powinien nasłuchiwać na webhooki z Cloudflare:

```python
# webhook_handler.py
from fastapi import FastAPI, Request
import httpx

app = FastAPI()

@app.post("/cloudflare-webhook")
async def handle_cloudflare_webhook(request: Request):
    data = await request.json()
    
    if data["type"] == "audit_request":
        # Przetwórz żądanie audytu
        result = await process_audit(data["fileId"], data["parameters"])
        
        # Wyślij wyniki z powrotem do Cloudflare
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://ai-auditor.your-domain.com/results",
                headers={"Authorization": "Bearer TwojPIN123!"},
                json={
                    "jobId": data["jobId"],
                    "results": result
                }
            )
```

### 2. Synchronizacja danych
```python
# sync_handler.py
import asyncio
import httpx

async def sync_with_cloudflare():
    """Synchronizuj dane z Cloudflare."""
    async with httpx.AsyncClient() as client:
        # Pobierz pending jobs
        response = await client.get(
            "https://ai-auditor.your-domain.com/jobs/pending",
            headers={"Authorization": "Bearer TwojPIN123!"}
        )
        
        jobs = response.json()
        
        for job in jobs:
            # Przetwórz job lokalnie
            result = await process_job_locally(job)
            
            # Wyślij wyniki
            await client.post(
                f"https://ai-auditor.your-domain.com/results",
                headers={"Authorization": "Bearer TwojPIN123!"},
                json={"jobId": job["id"], "results": result}
            )

# Uruchom synchronizację co 30 sekund
asyncio.create_task(sync_with_cloudflare())
```

## 🧪 Testowanie

### 1. Test podstawowej funkcjonalności
```bash
# Test health check
curl -H "Authorization: Bearer TwojPIN123!" \
  https://ai-auditor.your-domain.com/health

# Test upload
curl -X POST \
  -H "Authorization: Bearer TwojPIN123!" \
  -F "file=@test.pdf" \
  https://ai-auditor.your-domain.com/upload

# Test audit
curl -X POST \
  -H "Authorization: Bearer TwojPIN123!" \
  -H "Content-Type: application/json" \
  -d '{"fileId":"test_file","auditType":"test"}' \
  https://ai-auditor.your-domain.com/audit
```

### 2. Test bezpieczeństwa
```bash
# Test bez autoryzacji (powinien zwrócić 401)
curl https://ai-auditor.your-domain.com/health

# Test z nieprawidłowym tokenem (powinien zwrócić 401)
curl -H "Authorization: Bearer wrong_password" \
  https://ai-auditor.your-domain.com/health
```

### 3. Test rate limiting
```bash
# Wykonaj 101 requestów w ciągu minuty
for i in {1..101}; do
  curl -H "Authorization: Bearer TwojPIN123!" \
    https://ai-auditor.your-domain.com/health
done
```

## 📊 Monitoring

### 1. Cloudflare Analytics
- Dashboard: https://dash.cloudflare.com
- Workers Analytics: Real-time metrics
- Security Events: Bot protection, rate limiting

### 2. Custom Metrics
```javascript
// W Worker
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const start = Date.now()
  
  try {
    const response = await processRequest(request)
    
    // Log success
    console.log(`Request processed in ${Date.now() - start}ms`)
    
    return response
  } catch (error) {
    // Log error
    console.error(`Request failed: ${error.message}`)
    throw error
  }
}
```

## 🔧 Troubleshooting

### 1. Worker nie odpowiada
```bash
# Sprawdź logi
wrangler tail

# Sprawdź status
wrangler status
```

### 2. KV namespace nie działa
```bash
# Sprawdź bindingi
wrangler kv:namespace list

# Testuj dostęp
wrangler kv:key get "test_key" --namespace-id="your_namespace_id"
```

### 3. DNS nie działa
```bash
# Sprawdź rekordy DNS
dig ai-auditor.your-domain.com

# Sprawdź w Cloudflare Dashboard
# DNS > Records
```

### 4. Rate limiting zbyt restrykcyjny
```bash
# Zaktualizuj regułę
curl -X PUT "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/firewall/rules/$RULE_ID" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "rate_limit": {
      "threshold": 200,
      "period": 60
    }
  }'
```

## 📞 Wsparcie

### 1. Dokumentacja Cloudflare
- Workers: https://developers.cloudflare.com/workers/
- KV: https://developers.cloudflare.com/workers/runtime-apis/kv/
- Security: https://developers.cloudflare.com/firewall/

### 2. Kontakt
- Email: support@ai-auditor.com
- Dokumentacja: https://docs.ai-auditor.com
- GitHub: https://github.com/ai-auditor/cloudflare

---

**🔑 Hasło dostępu dla klienta: `TwojPIN123!`**

**🌐 URL po wdrożeniu: `https://ai-auditor.your-domain.com`**
