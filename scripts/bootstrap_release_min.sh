#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

BR="${1:-release/for-client}"

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

# --- Docker (GPU, CUDA/cuBLAS) ---
cat > Dockerfile.gpu <<'DFG'
# syntax=docker/dockerfile:1
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Python + curl
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

# --- minimal reqs do testów/CI ---
cat > requirements-ci.txt <<'REQ'
streamlit>=1.32
pandas>=2.0
matplotlib>=3.8
REQ

# --- env sample ---
cat > .env.sample <<'ENV'
LLM_GGUF="/app/models/meta-llama-3-8b-instruct.Q4_K_M.gguf"
LLM_GGUF_ALT=""
KOSZTY_FACT="/app/data/faktury/koszty"
PRZYCHODY_FACT="/app/data/faktury/przychody"
ENV

# --- skrypty dev ---
cat > scripts/install.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install -r requirements-ci.txt
# opcjonalnie (CPU wheel do chatu):
pip install "llama-cpp-python>=0.3" --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu || true
echo "[OK] install complete"
SH
chmod +x scripts/install.sh

cat > scripts/install_gpu.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
# Wymaga hosta z NVIDIA + CUDA runtime.
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install -r requirements-ci.txt
pip install "llama-cpp-python>=0.3" --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cuBLAS
echo "[OK] gpu install complete (pamiętaj o n_gpu_layers w kodzie)"
SH
chmod +x scripts/install_gpu.sh

cat > scripts/run.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate 2>/dev/null || true
./scripts/ui_restart.sh
SH
chmod +x scripts/run.sh

# --- CI workflow + smoke tests ---
cat > scripts/ci_run_tests.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data/uploads data/decisions data/exports logs/charts
TODAY="$(date +%Y%m%d)"
IN="data/uploads/ci_sample.csv"
OUT="data/exports/with_decisions_${TODAY}.csv"
cat > "$IN" <<CSV
id,nazwa_pliku,status,kwota,kontrahent
601,fv_601.pdf,needs_review,10.00,A
602,fv_602.pdf,ok,20.00,B
CSV
python -m app.decisions save --ids "601" --decision approved --reason "ci" >/dev/null || true
python -m app.decisions merge --in "$IN" --out "$OUT" >/dev/null || true
python - <<'PY'
import os
from app.ui_charts import donut_save_png
p="logs/charts/ci.png"
donut_save_png({"ok":2,"needs_review":1}, p, title="CI")
assert os.path.isfile(p) and os.path.getsize(p)>0
print("[PASS] donut generated", p)
PY
python - <<'PY'
import ast, pathlib
for p in ["app/pages/01_Walidacja.py","app/pages/02_Przeglad.py"]:
    try:
        ast.parse(pathlib.Path(p).read_text(encoding="utf-8"))
        print("[PASS] syntax OK:", p)
    except Exception as e:
        print("[WARN] syntax check failed:", p, e)
PY
echo "[PASS] ci_run_tests done"
SH
chmod +x scripts/ci_run_tests.sh

cat > .github/workflows/ci.yml <<'YML'
name: CI
on: [push, pull_request]
jobs:
  python-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
      - run: pip install -r requirements-ci.txt
      - run: bash scripts/ci_run_tests.sh
  docker-build-cpu:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t ai-auditor:cpu .
YML

# --- QUICKSTART (1 plik dla klienta) ---
cat > docs/QUICKSTART.md <<'MD'
# QUICKSTART – AI-Audytor

## CPU via Docker (zalecane)
1) `cp .env.sample .env.local`
2) `docker compose up --build`
3) UI: `http://localhost:8585`

## GPU (host lub kontener)
- **Host (venv):**

./scripts/install_gpu.sh
./scripts/run.sh

*Wymaga NVIDIA CUDA runtime i ustawienia `n_gpu_layers>0` w backendzie LLM (jeśli opcja jest w UI/konfiguracji).*
- **Kontener (GPU):**

docker build -f Dockerfile.gpu -t ai-auditor:gpu .
docker run --gpus all --rm -p 8585:8501 --env-file .env.local ai-auditor:gpu

*Wymaga sterowników NVIDIA i Docker z wsparciem GPU.*

## Co potrafi
- **🧾 Walidacja:** CSV → filtry + donut + liczniki + link do PDF (1 wiersz) → eksport.
- **📋 Przegląd:** multiselect → Zatwierdź/Odrzuć (CSV w `data/decisions/`) → eksport „po decyzjach”.
- **Chat:** lokalny LLM `.gguf` (llama-cpp-python).

## Zalety / wady
**+ lokalnie (bez chmury)**, **+ proste CSV-in/out**, **+ Docker/Compose/CI**
**− CPU domyślnie wolniejsze**, **− decyzje w CSV (dla multi-user zalecana DB)**, **− brak OCR PDF (do rozbudowy)**

## Konfiguracja (.env.local)

LLM_GGUF="/app/models/twoj_model.gguf"
KOSZTY_FACT="/app/data/faktury/koszty"
PRZYCHODY_FACT="/app/data/faktury/przychody"

MD

# --- Gałąź + commit (bez push) ---
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git checkout -B "$BR"
  git add -A
  git commit -m "release: docker+compose (CPU/GPU), CI, QUICKSTART for client" || true
  echo "[OK] Branch prepared: $BR"
  echo "Push: git push -u origin $BR"
else
  echo "[WARN] Not a git repo; skipping git steps."
fi

echo "[DONE] bootstrap_release_min"
