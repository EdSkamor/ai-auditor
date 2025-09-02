#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
[ -f ".venv/bin/activate" ] && source .venv/bin/activate

rm -rf tie_pdfs && mkdir -p tie_pdfs
cp -f demo_invoices/f1_pln.pdf tie_pdfs/x1.pdf
cp -f demo_invoices/f1_pln.pdf tie_pdfs/FV_1_12_2024_prefname.pdf

python - <<'PY'
import pandas as pd
df = pd.DataFrame([{
  "Pozycja_ID": 611, "Numer": "FV/1/12/2024", "Data": "2024-12-05",
  "Netto": "1 000,00", "Kontrahent": "ACME Sp. z o.o."
}])
with pd.ExcelWriter("pop_tie_fname.xlsx") as w:
    df.to_excel(w, sheet_name="Koszty", index=False)
print("OK: pop_tie_fname.xlsx")
PY

TS="$(date +%Y%m%d_%H%M%S)"; RUN="web_runs/tb_ab_${TS}"; mkdir -p "$RUN"
python pdf_indexer.py tie_pdfs "$RUN/All_invoices.csv"

# v1: preferuj nazwę pliku
python pop_matcher.py --pop pop_tie_fname.xlsx --pdf-root tie_pdfs \
  --index-csv "$RUN/All_invoices.csv" --amount-tol 0.01 \
  --tiebreak-weight-fname 0.98 --tiebreak-min-seller 0 \
  --out-jsonl "$RUN/v1.jsonl" --summary "$RUN/v1_summary.json"
grep -q 'FV_1_12_2024_prefname.pdf' "$RUN/v1.jsonl" && echo "V1 OK" || { echo "V1 FAIL"; exit 1; }

# zmień seller_guess w 1. wierszu
python - <<'PY'
import csv, os
from pathlib import Path
p = Path(os.environ["RUN"]) / "All_invoices.csv"
rows = list(csv.DictReader(open(p, encoding="utf-8")))
rows[0]["seller_guess"] = "ACME Services SA"
with open(p, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print("OK: seller_guess updated")
PY

# v2: preferuj kontrahenta
python pop_matcher.py --pop pop_tie_fname.xlsx --pdf-root tie_pdfs \
  --index-csv "$RUN/All_invoices.csv" --amount-tol 0.01 \
  --tiebreak-weight-fname 0.05 --tiebreak-min-seller 40 \
  --out-jsonl "$RUN/v2.jsonl" --summary "$RUN/v2_summary.json"
grep -q 'x1.pdf' "$RUN/v2.jsonl" && echo "V2 OK" || { echo "V2 FAIL"; exit 1; }

echo "ALL GOOD -> $RUN"
