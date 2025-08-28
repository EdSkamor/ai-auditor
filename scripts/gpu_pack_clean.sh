#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

BR="${1:-release/client-pack-gpu}"

# Ensure CPU pack exists (Dockerfile, compose, .env.sample, QUICKSTART)
[ -f Dockerfile ] || ./scripts/client_pack_simple.sh >/dev/null

# Dockerfile.gpu (cuBLAS)
cat > Dockerfile.gpu <<'DFG'
# syntax=docker/dockerfile:1
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive PIP_NO_CACHE_DIR=1 STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
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

# Run helper for GPU container
cat > scripts/run_gpu_container.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
IMG="${1:-ai-auditor:gpu}"
docker image inspect "$IMG" >/dev/null 2>&1 || docker build -f Dockerfile.gpu -t "$IMG" .
docker run --gpus all --rm -p 8585:8501 --env-file .env.local \
  -v "$(pwd)/data:/app/data" -v "$(pwd)/logs:/app/logs" \
  "$IMG"
SH
chmod +x scripts/run_gpu_container.sh

# QUICKSTART (append GPU section idempotently)
GPU_BLOCK_START="<!-- GPU-BLOCK-START -->"
GPU_BLOCK_END="<!-- GPU-BLOCK-END -->"
if [ -f docs/QUICKSTART.md ]; then
  # remove previous GPU block if present
  awk -v s="$GPU_BLOCK_START" -v e="$GPU_BLOCK_END" '
    BEGIN{skip=0}
    index($0,s){skip=1; next}
    index($0,e){skip=0; next}
    skip==0{print}
  ' docs/QUICKSTART.md > docs/QUICKSTART.tmp && mv docs/QUICKSTART.tmp docs/QUICKSTART.md
else
  mkdir -p docs
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
fi

cat >> docs/QUICKSTART.md <<'MD'
<!-- GPU-BLOCK-START -->
## GPU (opcjonalnie)
- Kontener (NVIDIA, Docker z GPU):

docker build -f Dockerfile.gpu -t ai-auditor:gpu .
./scripts/run_gpu_container.sh ai-auditor:gpu

- Host (venv, GPU wheel):

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-ci.txt
pip install "llama-cpp-python>=0.3" --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cuBLAS


./scripts/ui_restart.sh

<!-- GPU-BLOCK-END -->
MD

# Branch + commit (force-add .env.sample, skip hooks)
git rev-parse --is-inside-work-tree >/dev/null 2>&1
git checkout -B "$BR"
git add -A
git add -f .env.sample || true
git commit -m "client pack: add GPU (Dockerfile.gpu), run script, QUICKSTART GPU" --no-verify || true

echo "[OK] Branch ready: $BR"
echo "[NEXT] push with: git push -u origin $BR"
