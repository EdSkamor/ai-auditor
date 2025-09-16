# 🚀 AI Auditor - Weryfikacja na HOŚCIE

## ✅ Gotowe skrypty "kuloodporne"

Utworzono 3 skrypty do uruchomienia na hoście w `/home/romaks/ai_2/ai-auditor-clean`:

- `host_setup.sh` - setup Docker Compose + health checks
- `host_tunnel.sh` - tunel Cloudflared (zostaw otwarty)
- `host_tests.sh` - testy tunelu, CORS, Git, Streamlit Cloud

## 📋 Instrukcje wykonania

### Krok 1: Skopiuj skrypty do właściwego repo

```bash
# Skopiuj skrypty do ai-auditor-clean
mkdir -p /home/romaks/ai_2/ai-auditor-clean/scripts/dev
cp /workspaces/ai-auditor/scripts/dev/host_*.sh /home/romaks/ai_2/ai-auditor-clean/scripts/dev/
chmod +x /home/romaks/ai_2/ai-auditor-clean/scripts/dev/host_*.sh
```

### Krok 2: Uruchom na hoście (2 terminale)

#### Terminal #1 - Setup i testy:
```bash
cd /home/romaks/ai_2/ai-auditor-clean
bash scripts/dev/host_setup.sh
```

#### Terminal #2 - Tunel (zostaw otwarty):
```bash
cd /home/romaks/ai_2/ai-auditor-clean
bash scripts/dev/host_tunnel.sh
```

#### Terminal #1 - Testy tunelu:
```bash
cd /home/romaks/ai_2/ai-auditor-clean
bash scripts/dev/host_tests.sh
```

## 🎯 Co sprawdzają skrypty

### `host_setup.sh`:
- ✅ Cleanup Docker Compose
- ✅ Build AI (szybszy feedback)
- ✅ Wait for AI health (90s timeout)
- ✅ Start UI
- ✅ Wait for UI health (60s timeout)
- ✅ Local health checks
- ✅ Sample analyze test (bez auth)

### `host_tunnel.sh`:
- ✅ Uruchamia Cloudflared tunnel
- ✅ Logi do `/tmp/cloudflared.log`
- ✅ Zostaw otwarty (tunel musi działać)

### `host_tests.sh`:
- ✅ Docker status
- ✅ AI/UI log tails
- ✅ Local health checks
- ✅ Tunnel URL extraction
- ✅ Tunnel health check
- ✅ CORS preflight test
- ✅ Streamlit Cloud health
- ✅ Git info (branch, remote, last commit)

## 🎯 Oczekiwane wyniki

- **AI healthz**: `{"status":"healthy","ready":true}`
- **UI health**: `ok`
- **TUN health**: `{"status":"healthy","ready":true}`
- **CORS preflight**: `HTTP/2 200` z nagłówkami `Access-Control-Allow-*`
- **Git branch**: `main`
- **Streamlit Cloud**: `ok`

## 📊 Raport do zwrócenia

Po uruchomieniu `host_tests.sh` wklej:

1. `docker compose ps`
2. Końcówki logów AI i UI (z tego skryptu)
3. Linię `TUN=...`
4. Wyniki curl dla:
   - local AI
   - local UI
   - TUN health
   - Nagłówki z OPTIONS (pierwsze ~20-30 linii)
5. `git rev-parse --abbrev-ref HEAD` + `git log -1 --oneline`
6. `https://ai-auditor-87.streamlit.app/_stcore/health`

## 🔧 Troubleshooting

### AI nie startuje (ImportError/libGL)
```bash
# Sprawdź logi
docker compose logs ai

# Jeśli brakuje bibliotek systemowych, dodaj do Dockerfile.ai:
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     curl build-essential libglib2.0-0 libsm6 libxext6 libxrender1 libgl1 ffmpeg \
#  && rm -rf /var/lib/apt/lists/*

# Przebuduj
docker compose build ai --no-cache
docker compose up -d ai
```

### Port 8001 zajęty
```bash
fuser -k 8001/tcp 2>/dev/null || true
docker compose up -d ai
```

### CORS błędy
Sprawdź w `app/main.py` czy CORS jest poprawnie skonfigurowany:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lub konkretne originy
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
```

## 🌐 Streamlit Cloud

Po pomyślnej weryfikacji:
1. Skopiuj `TUN=...` z wyniku testów
2. W Streamlit Cloud ustaw: `AI_API_BASE=https://$TUN`
3. Tunel jest efemeryczny - po restarcie trzeba zaktualizować URL

## 🎯 Success Criteria

- ✅ AI: GET /healthz → 200 locally and via $TUN
- ✅ UI: GET /_stcore/health → 200 locally
- ✅ CORS preflight from https://ai-auditor-87.streamlit.app to $TUN/analyze → 200 with proper Access-Control-Allow-* headers
- ✅ Branch is `main`, changes pushed if modified
- ✅ Streamlit Cloud `_stcore/health` returns "ok"

**Wszystko gotowe do testowania na hoście!** 🚀
