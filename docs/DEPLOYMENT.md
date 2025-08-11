# Wdrożenie (skrót)

## systemd
- Unit uruchamia `uvicorn server:app` w venv.
- Env: `PATH`, `TRANSFORMERS_VERBOSITY`, opcjonalnie `AIAUDITOR_*`.

## Nginx (reverse proxy)
- Proxy na `127.0.0.1:8000`, nagłówki `X-Forwarded-*`.
- HTTPS: Let's Encrypt (Certbot).

Kroki szczegółowe: `README_QuickStart.md`.
