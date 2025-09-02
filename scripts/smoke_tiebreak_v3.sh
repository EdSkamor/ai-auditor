#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
[ -f ".venv/bin/activate" ] && source .venv/bin/activate

# 0) czysto
rm -rf tie_pdfs
mkdir -p tie_pdfs

# 1) dwa fizyczne pliki z tym samym numerem z PDF (różne NAZWY plików)
cp -f demo_invoices/f1_pln.pdf tie_pdfs/x1.pdf
cp -f demo_invoices/f1_pln.pdf tie_pdfs/FV_1_12_2024_prefname.pdf

# 2) minimalna populacja (1 rekord Koszty) z dokładnym numerem/datem/kwotą
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

# 3) indeks
OUT="web_runs/tb_smoke_v3_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUT"
python pdf_indexer.py tie_pdfs "$OUT/All_invoices.csv"
lines=$(wc -l < "$OUT/All_invoices.csv")
[ "$lines" -eq 3 ] || { echo "FAIL: indeks ma $lines wierszy (oczekiwano 3)"; exit 1; }

# 4A) TIE po NAZWIE PLIKU (wysoka waga fname) – oczekujemy wyboru prefname.pdf
python pop_matcher.py \
  --pop pop_tie_fname.xlsx \
  --pdf-root tie_pdfs \
  --index-csv "$OUT/All_invoices.csv" \
  --amount-tol 0.01 \
  --tiebreak-weight-fname 0.9 \
  --tiebreak-min-seller 0 \
  --out-jsonl "$OUT/fname.jsonl"

python - <<PY
import json, os, sys
p = os.path.join(r"$OUT","fname.jsonl")
chosen = None
with open(p, encoding="utf-8") as f:
    for line in f:
        j = json.loads(line)
        if str(j.get("pozycja_id")) == "611" and j.get("dopasowanie",{}).get("status")=="znaleziono":
            chosen = j["pdf"]["sciezka"]
            break
print("FNAME_CHOSEN:", chosen)
assert chosen and chosen.endswith("FV_1_12_2024_prefname.pdf"), "Tie po fname nie wybrał prefname.pdf"
PY

# 4B) TIE po KONTRAHENCIE – degradujemy seller_guess dla prefname.pdf i oczekujemy x1.pdf
python - <<'PY'
import csv, pathlib
p = pathlib.Path(r"'"$OUT"'/All_invoices.csv")
rows = list(csv.DictReader(p.open(encoding="utf-8")))
for r in rows:
    if r["source_filename"]=="FV_1_12_2024_prefname.pdf":
        r["seller_guess"]="Totalnie Inny Kontrahent SA"
p.write_text("", encoding="utf-8")
with p.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
PY

python pop_matcher.py \
  --pop pop_tie_fname.xlsx \
  --pdf-root tie_pdfs \
  --index-csv "$OUT/All_invoices.csv" \
  --amount-tol 0.01 \
  --tiebreak-weight-fname 0.1 \
  --tiebreak-min-seller 40 \
  --out-jsonl "$OUT/seller.jsonl"

python - <<PY
import json, os
p = os.path.join(r"$OUT","seller.jsonl")
chosen = None
with open(p, encoding="utf-8") as f:
    for line in f:
        j = json.loads(line)
        if str(j.get("pozycja_id")) == "611" and j.get("dopasowanie",{}).get("status")=="znaleziono":
            chosen = j["pdf"]["sciezka"]
            break
print("SELLER_CHOSEN:", chosen)
assert chosen and chosen.endswith("x1.pdf"), "Tie po seller nie wybrał x1.pdf"
PY

echo "✅ SMOKE TIEBREAKER V3 – OK"
echo "Wyniki:"
echo " - $OUT/fname.jsonl"
echo " - $OUT/seller.jsonl"
