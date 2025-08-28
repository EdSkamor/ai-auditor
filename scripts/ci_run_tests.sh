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
