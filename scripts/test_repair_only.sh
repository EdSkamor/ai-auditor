#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python scripts/repair_przeglad.py
echo "[PASS] repair_przeglad.py OK"
