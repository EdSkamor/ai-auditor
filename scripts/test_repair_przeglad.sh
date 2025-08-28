#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# 1) Patch strony
python scripts/repair_przeglad.py

# 2) Testy funkcjonalne (jeśli istnieją)
if [[ -x scripts/test_przeglad_cli.sh ]]; then
  ./scripts/test_przeglad_cli.sh
else
  echo "[WARN] Brak scripts/test_przeglad_cli.sh"
fi

if [[ -x scripts/test_przeglad_summary.sh ]]; then
  ./scripts/test_przeglad_summary.sh
else
  echo "[WARN] Brak scripts/test_przeglad_summary.sh"
fi

echo "[PASS] repair+tests zakończone."
