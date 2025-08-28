#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p data/uploads data/decisions data/exports

TODAY="$(date +%Y%m%d)"
IN="data/uploads/sample_for_review.csv"
OUT="data/exports/with_decisions_${TODAY}.csv"
DEC="data/decisions/decisions_${TODAY}.csv"

cat > "$IN" <<CSV
id,nazwa_pliku,status,kwota,kontrahent
101,fv_101.pdf,needs_review,123.45,Firma A
102,fv_102.pdf,ok,222.22,Firma B
103,fv_103.pdf,needs_review,999.99,Firma C
CSV

.venv/bin/python -m app.decisions save --ids "101,102" --decision approved --reason "bulk approve" >/dev/null
.venv/bin/python -m app.decisions save --ids "103" --decision rejected --reason "not matching" >/dev/null
.venv/bin/python -m app.decisions merge --in "$IN" --out "$OUT" >/dev/null

echo "[INFO] Decisions file: $DEC"
tail -n +1 "$DEC" || true
echo
echo "[INFO] Export with decisions: $OUT"
head -n 10 "$OUT" || true
echo "[OK] Demo finished"
