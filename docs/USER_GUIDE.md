# AI Auditor — Przewodnik użytkownika

## Wymagania
- Linux Mint 22.1 (XFCE) / Ubuntu 24.04 LTS
- Python 3.12 + venv, git, curl
- (Opcjonalnie) NVIDIA + CUDA

## Szybki start (lokalnie)
1. Klon repo, venv, `pip install -r requirements.txt`.
2. Start: `uvicorn server:app --reload --host 0.0.0.0 --port 8000`
3. UI: `http://127.0.0.1:8000/`
   API:
   - `GET /healthz` → `{"status":"ok"}`
   - `POST /analyze` → `{ "output": "..." }`
   - `POST /analyze-file` → metryki + wykryte *prompts* + próbka danych.

## Ładowanie pliku
- Obsługiwane: `.xlsx`, `.csv`, `.tsv`. Nagłówek wykrywany w pierwszych 10 wierszach.
- Wiersze nad nagłówkiem zwracamy jako `prompts` (np. instrukcje testowe z arkusza).

## Typowe problemy
- Port 8000 zajęty → `pkill -f "uvicorn server:app"`.
- Brak `python-multipart` → `pip install python-multipart` (w venv).
- Poufność danych → patrz `docs/DATA_HANDLING.md`.
