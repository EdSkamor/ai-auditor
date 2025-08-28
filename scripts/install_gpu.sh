#!/usr/bin/env bash
set -euo pipefail
# Wymaga hosta z NVIDIA + CUDA runtime.
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install -r requirements-ci.txt
pip install "llama-cpp-python>=0.3" --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cuBLAS
echo "[OK] gpu install complete (pamiętaj o n_gpu_layers w kodzie)"
