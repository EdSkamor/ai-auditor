#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p data/uploads data/decisions data/exports

TODAY="$(date +%Y%m%d)"
IN="data/uploads/sample_for_review.csv"
OUT="data/exports/with_decisions_${TODAY}.csv"
DEC="data/decisions/decisions_${TODAY}.csv"

# 1) Sample CSV
cat > "$IN" <<CSV
id,nazwa_pliku,status,kwota,kontrahent
101,fv_101.pdf,needs_review,123.45,Firma A
102,fv_102.pdf,ok,222.22,Firma B
103,fv_103.pdf,needs_review,999.99,Firma C
CSV

# 2) Decisions
.venv/bin/python -m app.decisions save --ids "101,102" --decision approved --reason "bulk approve" >/dev/null
.venv/bin/python -m app.decisions save --ids "103" --decision rejected --reason "not matching" >/dev/null

# 3) Merge
.venv/bin/python -m app.decisions merge --in "$IN" --out "$OUT" >/dev/null

# 4) Assertions
[ -f "$DEC" ] || { echo "[FAIL] missing $DEC"; exit 1; }
[ -s "$DEC" ] || { echo "[FAIL] empty $DEC"; exit 1; }
[ -f "$OUT" ] || { echo "[FAIL] missing $OUT"; exit 1; }

DEC_CNT="$(awk 'NR>1{c++} END{print c+0}' "$DEC")"
HEADER="$(head -n1 "$OUT")"

case "$HEADER" in
  *"decision,decision_ts,decision_user"*) : ;;
  *) echo "[FAIL] missing decision columns in $OUT"; exit 1;;
esac

if [ "$DEC_CNT" != "3" ]; then
  echo "[FAIL] expected 3 decisions, got $DEC_CNT"
  exit 1
fi

APPROVED="$(grep -c ',approved,' "$DEC" || true)"
REJECTED="$(grep -c ',rejected,' "$DEC" || true)"

if [ "$APPROVED" -ne 2 ] || [ "$REJECTED" -ne 1 ]; then
  echo "[FAIL] decisions distribution invalid (approved=$APPROVED rejected=$REJECTED)"
  exit 1
fi

echo "[PASS] decisions saved to $DEC and merged to $OUT"
