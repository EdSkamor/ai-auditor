#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p data/uploads data/decisions data/exports

TODAY="$(date +%Y%m%d)"
IN="data/uploads/przeglad_sample.csv"
OUT="data/exports/with_decisions_${TODAY}.csv"
DEC="data/decisions/decisions_${TODAY}.csv"

# 1) Przygotuj CSV (jak na stronie)
cat > "$IN" <<CSV
id,nazwa_pliku,status,kwota,kontrahent
201,fv_201.pdf,needs_review,10.00,Alpha
202,fv_202.pdf,ok,20.00,Beta
203,fv_203.pdf,needs_review,30.00,Gamma
CSV

# 2) "Masowe decyzje" jak w UI: 201,202 -> approved; 203 -> rejected
.venv/bin/python -m app.decisions save --ids "201,202" --decision approved --reason "batch ok" >/dev/null
.venv/bin/python -m app.decisions save --ids "203" --decision rejected --reason "bad data" >/dev/null

# 3) Eksport po decyzjach
.venv/bin/python -m app.decisions merge --in "$IN" --out "$OUT" >/dev/null

# 4) Asercje
[ -s "$DEC" ] || { echo "[FAIL] decisions file missing or empty: $DEC"; exit 1; }
[ -s "$OUT" ] || { echo "[FAIL] export missing or empty: $OUT"; exit 1; }

# Nagłówek eksportu zawiera kolumny z decyzjami
head -n1 "$OUT" | grep -q "decision,decision_ts,decision_user" || {
  echo "[FAIL] export header lacks decision columns"
  exit 1
}

echo "[PASS] Przegląd backend OK → $OUT"
