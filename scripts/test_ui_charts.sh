#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# upewnij się, że matplotlib jest w .venv i plik jest poprawny
./scripts/fix_ui_charts_and_install.sh >/dev/null

mkdir -p logs/charts
python3 - <<'PY'
import os
from app.ui_charts import donut_save_png
out = "logs/charts/donut_demo.png"
p = donut_save_png({"ok": 7, "needs_review": 3, "error": 1}, out, title="Statusy (demo)")
assert os.path.isfile(p) and os.path.getsize(p) > 0, "PNG not created"
print("[PASS] donut saved at", p)
PY
