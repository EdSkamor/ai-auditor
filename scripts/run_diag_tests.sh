#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

./scripts/diag_collect.sh >/dev/null
./scripts/test_diag_collect.sh

echo "[PASS] diag_collect + test_diag_collect OK"
