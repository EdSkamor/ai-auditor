#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

BR="${1:-release/client-pack}"

mkdir -p scripts docs .github/workflows

# --- Docker (CPU) ---
cat > Dockerfile <<'DF'
# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN python -m pip install --upgrade pip wheel setuptools && \
    ( [ -f requirements.txt ] && pip install -r requirements.txt || true ) && \
    pip install "streamlit>=1.32" "pandas>=2.0" "matplotlib>=3.8" && \
    (pip install "llama-cpp-python>=0.3" --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu || echo "[warn] llama-cpp-python wheel not installed")

EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -fsS http://localhost:8501/healthz || exit 1

ENTRYPOINT ["streamlit","run","app/Home.py","--server.port=8501","--server.address=0.0.0.0"]
DF

# --- Docker (GPU, cuBLAS) ---
cat > Dockerfile.gpu <<'DFG'
# syntax=docker/dockerfile:1
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv python3-distutils curl && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    python -m pip install --upgrade pip wheel setuptools && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN ( [ -f requirements.txt ] && pip install -r requirements.txt || true ) && \
    pip install "streamlit>=1.32" "pandas>=2.0" "matplotlib>=3.8" && \
    pip install "llama-cpp-python>=0.3" --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cuBLAS

EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD curl -fsS http://localhost:8501/healthz || exit 1

ENTRYPOINT ["streamlit","run","app/Home.py","--server.port=8501","--server.address=0.0.0.0"]
DFG

# --- docker-compose (CPU) ---
cat > docker-compose.yml <<'YML'
services:
  ai-auditor:
    build:
      context: .
      dockerfile: Dockerfile
    image: ai-auditor:cpu
    ports:
      - "8585:8501"
    env_file:
      - .env.local
    environment:
      STREAMLIT_BROWSER_GATHER_USAGE_STATS: "false"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      # - ./models:/app/models
    command: streamlit run app/Home.py --server.port=8501 --server.address=0.0.0.0
YML

# --- .dockerignore ---
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

# --- .env.sample ---
cat > .env.sample <<'ENV'
LLM_GGUF="/app/models/meta-llama-3-8b-instruct.Q4_K_M.gguf"
LLM_GGUF_ALT=""
KOSZTY_FACT="/app/data/faktury/koszty"
PRZYCHODY_FACT="/app/data/faktury/przychody"
ENV

# --- QUICKSTART (jeden plik dla klienta) ---
cat > docs/QUICKSTART.md <<'MD'
# QUICKSTART – AI-Audytor

## CPU via Docker (zalecane)
1) `cp .env.sample .env.local`
2) `docker compose up --build`
3) UI: `http://localhost:8585`

## GPU (host lub kontener)
- **Kontener GPU (wymaga NVIDIA + Docker GPU):**

docker build -f Dockerfile.gpu -t ai-auditor:gpu .
docker run --gpus all --rm -p 8585:8501 --env-file .env.local ai-auditor:gpu

- **Host (venv + GPU wheel):**

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-ci.txt
pip install "llama-cpp-python>=0.3" --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cuBLAS


./scripts/ui_restart.sh


## Co potrafi
- **🧾 Walidacja:** CSV → filtry + donut + liczniki + link do PDF (1 wiersz) → eksport.
- **📋 Przegląd:** multiselect → Zatwierdź/Odrzuć (CSV w `data/decisions/`) → eksport „po decyzjach”.
- **Chat:** lokalny LLM `.gguf` (llama-cpp-python).

## Zalety / wady
**+ lokalnie (bez chmury)**, **+ proste CSV-in/out**, **+ Docker/Compose/CI**
**− CPU wolniejsze**, **− decyzje w CSV (dla multi-user zalecana DB)**, **− brak OCR PDF (do rozbudowy)**

## Konfiguracja (.env.local)

LLM_GGUF="/app/models/twoj_model.gguf"
KOSZTY_FACT="/app/data/faktury/koszty"
PRZYCHODY_FACT="/app/data/faktury/przychody"

MD

# --- requirements-ci.txt (minimal do dev/testów) ---
cat > requirements-ci.txt <<'REQ'
streamlit>=1.32
pandas>=2.0
matplotlib>=3.8
REQ

# --- Git: branch + commit (pre-commit friendly) ---
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git checkout -B "$BR"
  if command -v pre-commit >/dev/null 2>&1; then pre-commit run -a || true; fi
  git add -A
  git commit -m "chore: client pack (Docker CPU/GPU, compose, env sample, QUICKSTART)" || true
  printf "[OK] Branch prepared: %s\n" "$BR"
  printf "Next push:\n  git push -u origin %s\n" "$BR"
else
  printf "[WARN] Not a git repo; skipped git steps.\n"
fi

printf "[DONE] client_pack generated.\n"
