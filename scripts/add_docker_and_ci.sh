#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p .github/workflows scripts logs docker
echo "[info] writing Dockerfile"
cat > Dockerfile <<'DF'
# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# system deps (curl for HEALTHCHECK)
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Python deps: najpierw podstawy do testów/UI, potem llm cpu wheel (bez kompilacji)
RUN python -m pip install --upgrade pip wheel setuptools && \
    ( [ -f requirements.txt ] && pip install -r requirements.txt || true ) && \
    pip install "streamlit>=1.32" "pandas>=2.0" "matplotlib>=3.8" && \
    pip install "llama-cpp-python>=0.3" --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

EXPOSE 8501

# HEALTHCHECK: Streamlit ma /healthz
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -fsS http://localhost:8501/healthz || exit 1

ENTRYPOINT ["streamlit","run","app/Home.py","--server.port=8501","--server.address=0.0.0.0"]
DF

echo "[info] writing .dockerignore"
cat > .dockerignore <<'IGN'
.git
.gitmodules
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

echo "[info] writing docker-compose.yml"
cat > docker-compose.yml <<'YML'
services:
  ai-auditor:
    build: .
    image: ai-auditor:local
    ports:
      - "8585:8501"
    env_file:
      - .env.local
    environment:
      STREAMLIT_BROWSER_GATHER_USAGE_STATS: "false"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      # Opcjonalnie modele z hosta:
      # - ~/models:/models
    command: streamlit run app/Home.py --server.port=8501 --server.address=0.0.0.0
YML

echo "[info] writing requirements-ci.txt"
cat > requirements-ci.txt <<'REQ'
streamlit>=1.32
pandas>=2.0
matplotlib>=3.8
# brak llama-cpp-python w CI testach (nie jest potrzebny do naszych testów)
REQ

echo "[info] writing GitHub Actions workflow"
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'YML'
name: CI

on:
  push:
  pull_request:

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

  docker-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build -t ai-auditor:ci .
YML

echo "[info] writing scripts/ci_run_tests.sh"
cat > scripts/ci_run_tests.sh <<'TEST'
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p data/uploads data/decisions data/exports logs/charts

# 1) decisions + merge (używa systemowego pythona, nie .venv)
TODAY="$(date +%Y%m%d)"
IN="data/uploads/sample_ci.csv"
OUT="data/exports/with_decisions_${TODAY}.csv"
DEC="data/decisions/decisions_${TODAY}.csv"

cat > "$IN" <<CSV
id,nazwa_pliku,status,kwota,kontrahent
401,fv_401.pdf,needs_review,10.00,A
402,fv_402.pdf,ok,20.00,B
403,fv_403.pdf,needs_review,30.00,C
CSV

python -m app.decisions save --ids "401,402" --decision approved --reason "ci approve" >/dev/null
python -m app.decisions save --ids "403" --decision rejected --reason "ci reject" >/dev/null
python -m app.decisions merge --in "$IN" --out "$OUT" >/dev/null

[ -s "$DEC" ] || { echo "[FAIL] missing $DEC"; exit 1; }
[ -s "$OUT" ] || { echo "[FAIL] missing $OUT"; exit 1; }

# 2) charts: wygeneruj donut
python - <<'PY'
import os
from app.ui_charts import donut_save_png
p="logs/charts/donut_ci.png"
donut_save_png({"ok":2,"needs_review":1}, p, title="CI")
assert os.path.isfile(p) and os.path.getsize(p)>0
print("[PASS] donut generated", p)
PY

# 3) szybki AST check stron (bez uruchamiania streamlit)
python - <<'PY'
import ast, pathlib
for p in ["app/pages/01_Walidacja.py","app/pages/02_Przeglad.py"]:
    try:
        ast.parse(pathlib.Path(p).read_text(encoding="utf-8"))
        print("[PASS] syntax OK:", p)
    except Exception as e:
        raise SystemExit(f"[FAIL] syntax error in {p}: {e}")
PY

echo "[PASS] CI tests completed"
TEST
chmod +x scripts/ci_run_tests.sh

echo "[OK] Docker + CI files written."
