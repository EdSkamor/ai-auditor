#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate 2>/dev/null || true
./scripts/ui_restart.sh
