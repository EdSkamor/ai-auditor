# 🚀 AI Auditor - Instrukcje dla HOSTA

## ✅ Naprawione problemy

1. **Devcontainer terminal** - poprawiono `postAttachCommand` (nie będzie się już zamykać)
2. **Skrypty hosta** - utworzono kompletne skrypty do uruchomienia na hoście

## 📋 Instrukcje wykonania

### Krok 1: Restart devcontainera
W VS Code/Cursor:
1. Otwórz paletę poleceń (`Ctrl+Shift+P`)
2. Wybierz `Dev Containers: Rebuild Container`
3. Po restarcie terminal nie będzie się już zamykać

### Krok 2: Skopiuj skrypty do właściwego repo

```bash
# Skopiuj skrypty do ai-auditor-clean
cp /workspaces/ai-auditor/scripts/dev/host_*.sh /home/romaks/ai_2/ai-auditor-clean/scripts/dev/
chmod +x /home/romaks/ai_2/ai-auditor-clean/scripts/dev/host_*.sh
```

### Krok 3: Uruchom na hoście (2 terminale)

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

## 🎯 Oczekiwane wyniki

- **AI healthz**: `{"status":"healthy","ready":true}`
- **UI health**: `ok`
- **TUN health**: `{"status":"healthy","ready":true}`
- **CORS preflight**: `HTTP/2 200` z nagłówkami `Access-Control-Allow-*`

## 📊 Raport do zwrócenia

Po wykonaniu wszystkich kroków, zwróć:

1. `docker compose ps`
2. Ostatnie 80 linii z `docker compose logs ai` i `docker compose logs ui`
3. Wartość `TUN=...`
4. Wyniki:
   - `curl -s http://127.0.0.1:8001/healthz`
   - `curl -s http://127.0.0.1:8501/_stcore/health`
   - `curl -s https://$TUN/healthz`
   - Pierwsze 20 linii z CORS preflight
5. `git rev-parse --abbrev-ref HEAD` i `git log -1 --oneline`
6. `curl -s https://ai-auditor-87.streamlit.app/_stcore/health`

## 🌐 Streamlit Cloud

Po pomyślnej weryfikacji:
1. Skopiuj `TUN=...` z wyniku testów
2. W Streamlit Cloud ustaw: `AI_API_BASE=https://$TUN`
3. Tunel jest efemeryczny - po restarcie trzeba zaktualizować URL

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
