# AI Auditor - Skrypty Deweloperskie

Skrypty pomocnicze do zarządzania lokalnym środowiskiem AI Auditor.

## Workflow Operacyjny

### 1. Uruchomienie lokalnego środowiska
```bash
./scripts/dev/up.sh
```
- Czyści stare kontenery i sieci
- Buduje i uruchamia serwisy (AI + UI)
- Sprawdza health checki
- Pokazuje status kontenerów

### 2. Uruchomienie tunelu (osobna zakładka)
```bash
./scripts/dev/tunnel.sh
```
- Uruchamia cloudflared tunnel do portu 8001
- Zapisuje logi do `/tmp/cloudflared-ai.log`
- **Zostaw otwarte** - tunel musi działać

### 3. Testy E2E
```bash
# Testy bez Basic Auth (domyślnie)
./scripts/dev/e2e.sh

# Testy z Basic Auth (jeśli włączony)
./scripts/dev/e2e-auth.sh
```

### 4. Pobranie URL tunelu
```bash
./scripts/dev/tun-url.sh
```

## Konfiguracja Streamlit Cloud

Po uruchomieniu tunelu, skopiuj URL i ustaw w Streamlit Cloud:
```
AI_API_BASE=https://<tunnel-url>.trycloudflare.com
```

## Troubleshooting

### UI nie odpowiada na 127.0.0.1:8501
```bash
docker compose logs -n 200 ui
docker compose ps
```

### AI nie odpowiada na 127.0.0.1:8001
```bash
docker compose logs -n 200 ai
docker compose ps
```

### Tunel zwraca 404 na /analyze
1. Sprawdź czy tunel wskazuje na port 8001: `./scripts/dev/tun-url.sh`
2. Porównaj curl lokalny vs tunelowy: `./scripts/dev/e2e.sh`
3. Sprawdź logi AI: `docker compose logs -n 200 ai`

### CORS błędy
- Sprawdź preflight OPTIONS: `./scripts/dev/e2e.sh`
- Upewnij się, że `allow_credentials=False` w CORS (dla demo)

## Szybkie komendy

```bash
# Restart wszystkiego
docker compose down -v && ./scripts/dev/up.sh

# Sprawdź status
docker compose ps
curl -s http://127.0.0.1:8001/healthz
curl -s http://127.0.0.1:8501/_stcore/health

# Logi
docker compose logs -f ai
docker compose logs -f ui
```
