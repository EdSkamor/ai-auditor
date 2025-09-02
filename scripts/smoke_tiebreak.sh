#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
[ -f ".venv/bin/activate" ] && source .venv/bin/activate

# Zestaw dwóch PDF o tym samym numerze (różne NAZWY plików)
rm -rf tie_pdfs && mkdir -p tie_pdfs
cp -f demo_invoices/f1_pln.pdf tie_pdfs/x1.pdf
cp -f demo_invoices/f1_pln.pdf tie_pdfs/FV_1_12_2024_prefname.pdf

# Minimalna populacja z jednym wierszem FV/1/12/2024
python - <<'PY'
import pandas as pd
df = pd.DataFrame([{
  "Pozycja_ID": 611,
  "Numer": "FV/1/12/2024",
  "Data": "2024-12-05",
  "Netto": 1000.00,
  "Kontrahent": "ACME Sp. z o.o."
}])
with pd.ExcelWriter("pop_tie_fname.xlsx") as w:
  df.to_excel(w, sheet_name="Koszty", index=False)
PY

# Indeks
OUT="web_runs/tb_smoke_$(date +%Y%m%d_%H%M%S)"
python pdf_indexer.py tie_pdfs "$OUT/All_invoices.csv"

# A) Tie-breaker po nazwie pliku (fname)
python pop_matcher.py --pop pop_tie_fname.xlsx --pdf-root tie_pdfs \
  --index-csv "$OUT/All_invoices.csv" --amount-tol 0.01 \
  --tiebreak-weight-fname 0.9 --tiebreak-min-seller 0
grep -q '"kryterium": "numer+fname"' verdicts.jsonl || { echo "FAIL: brak numer+fname"; exit 1; }

# B) Tie-breaker po kontrahencie (seller)
sed -i '0,/ACME Sp. z o.o./s//ACME Services SA/' "$OUT/All_invoices.csv"
python pop_matcher.py --pop pop_tie_fname.xlsx --pdf-root tie_pdfs \
  --index-csv "$OUT/All_invoices.csv" --amount-tol 0.01 \
  --tiebreak-weight-fname 0.1 --tiebreak-min-seller 40
grep -q '"kryterium": "numer+seller"' verdicts.jsonl || { echo "FAIL: brak numer+seller"; exit 1; }

echo "✅ SMOKE TIEBREAKER OK"
