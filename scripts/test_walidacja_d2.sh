#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# 1) Składnia strony
python3 - <<'PY'
import ast
p = "app/pages/01_Walidacja.py"
ast.parse(open(p, encoding="utf-8").read())
print("[PASS] syntax OK:", p)
PY

# 2) Przygotuj przykładowy CSV (użyjesz go w UI)
mkdir -p data/uploads data/exports
CSV_IN="data/uploads/walidacja_sample.csv"
cat > "$CSV_IN" <<CSV
id,status,nazwa_pliku,kwota,kontrahent
1,ok,fv_1.pdf,100.00,Firma A
2,needs_review,fv_2.pdf,200.00,Firma B
3,error,fv_3.pdf,300.00,Firma C
4,ok,fv_4.pdf,400.00,Firma D
CSV

echo "[PASS] sample CSV ready at $CSV_IN"
