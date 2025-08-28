#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# 1) Składnia strony
python3 - <<'PY'
import ast, sys
p = "app/pages/02_Przeglad.py"
src = open(p, encoding="utf-8").read()
ast.parse(src)
print("[PASS] syntax OK:", p)
PY

# 2) Integracja z backendem decyzji (symulacja klików z UI)
mkdir -p data/uploads data/decisions data/exports

TODAY="$(date +%Y%m%d)"
IN="data/uploads/przeglad_sample.csv"
OUT="data/exports/with_decisions_${TODAY}.csv"
DEC="data/decisions/decisions_${TODAY}.csv"

cat > "$IN" <<CSV
id,nazwa_pliku,status,kwota,kontrahent
301,fv_301.pdf,needs_review,10.00,Alpha
302,fv_302.pdf,ok,20.00,Beta
303,fv_303.pdf,needs_review,30.00,Gamma
CSV

.venv/bin/python -m app.decisions save --ids "301,302" --decision approved --reason "ui-sim approve" >/dev/null
.venv/bin/python -m app.decisions save --ids "303" --decision rejected --reason "ui-sim reject" >/dev/null
.venv/bin/python -m app.decisions merge --in "$IN" --out "$OUT" >/dev/null

[ -s "$DEC" ] || { echo "[FAIL] decisions file missing or empty: $DEC"; exit 1; }
[ -s "$OUT" ] || { echo "[FAIL] export missing or empty: $OUT"; exit 1; }
head -n1 "$OUT" | grep -q "decision,decision_ts,decision_user" || {
  echo "[FAIL] export header lacks decision columns"
  exit 1
}
echo "[PASS] 02_Przeglad integration OK → $OUT"
