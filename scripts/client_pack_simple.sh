#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p docs

# Dockerfile (CPU)
cat > Dockerfile <<'DF'
# syntax=docker/dockerfile:1
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
RUN python -m pip install --upgrade pip wheel setuptools && \
    ( [ -f requirements.txt ] && pip install -r requirements.txt || true ) && \
    pip install "streamlit>=1.32" "pandas>=2.0" "matplotlib>=3.8" && \
    (pip install "llama-cpp-python>=0.3" --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu || true)
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -fsS http://localhost:8501/healthz || exit 1
ENTRYPOINT ["streamlit","run","app/Home.py","--server.port=8501","--server.address=0.0.0.0"]
DF

# docker-compose (CPU)
cat > docker-compose.yml <<'YML'
services:
  ai-auditor:
    build: .
    image: ai-auditor:cpu
    ports:
      - "8585:8501"
    env_file:
      - .env.local
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      # - ./models:/app/models
    command: streamlit run app/Home.py --server.port=8501 --server.address=0.0.0.0
YML

# .dockerignore
cat > .dockerignore <<'IGN'
.git
.github
__pycache__/
*.py[cod]
*.log
*.tgz
*.gz
.venv/
logs/
data/uploads/*
data/exports/*
models/*
IGN

# .env.sample
cat > .env.sample <<'ENV'
LLM_GGUF="/app/models/meta-llama-3-8b-instruct.Q4_K_M.gguf"
LLM_GGUF_ALT=""
KOSZTY_FACT="/app/data/faktury/koszty"
PRZYCHODY_FACT="/app/data/faktury/przychody"
ENV

# QUICKSTART
cat > docs/QUICKSTART.md <<'MD'
# QUICKSTART – AI-Audytor

## CPU via Docker
1) `cp .env.sample .env.local`
2) `docker compose up --build`
3) UI: `http://localhost:8585`

## Co potrafi
- 🧾 Walidacja: filtry + donut + liczniki + PDF (1 wiersz) → eksport.
- 📋 Przegląd: multiselect → Zatwierdź/Odrzuć (CSV w `data/decisions/`) → eksport „po decyzjach”.
- Chat: lokalny LLM `.gguf` (llama-cpp-python).

## Konfiguracja (.env.local)

LLM_GGUF="/app/models/twoj_model.gguf"
KOSZTY_FACT="/app/data/faktury/koszty"
PRZYCHODY_FACT="/app/data/faktury/przychody"

MD
