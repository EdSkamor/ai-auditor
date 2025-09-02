#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
[ -f ".venv/bin/activate" ] && source .venv/bin/activate

# 0) clean
rm -rf tie_pdfs

# 1) dwa PDF-y z tym samym numerem (bez brace-expansion, dwa jawne cp)
mkdir -p tie_pdfs
cp -f demo_invoices/f1_pln.pdf tie_pdfs/x1.pdf
cp -f demo_invoices/f1_pln.pdf tie_pdfs/FV_1_12_2024_prefname.pdf

# 2) run-dir
OUT="web_runs/tb_smoke_v2_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUT"

# 3) indeks do OUT
python pdf_indexer.py tie_pdfs "$OUT/All_invoices.csv"

# sanity: indeks powinien mieć 3 wiersze (1 header + 2 rekordy)
lines=$(wc -l < "$OUT/All_invoices.csv")
if [ "$lines" -ne 3 ]; then
  echo "FAIL: indeks ma $lines wierszy, oczekiwano 3"; exit 1
fi

# 4A) TIE wg NAZWY PLIKU  (fname > seller)
python pop_matcher.py \
  --pop populacja.xlsx \
  --pdf-root tie_pdfs \
  --index-csv "$OUT/All_invoices.csv" \
  --amount-tol 0.01 \
  --tiebreak-weight-fname 0.9 \
  --tiebreak-min-seller 0 \
  --out-jsonl "$OUT/verdicts_tb_fname.jsonl"

grep -q '"kryterium": "numer\+fname"' "$OUT/verdicts_tb_fname.jsonl" \
  && echo "OK: znaleziono numer+fname" \
  || { echo "FAIL: brak numer+fname"; sed -n '1,20p' "$OUT/verdicts_tb_fname.jsonl"; exit 1; }

# 4B) TIE wg KONTRAHENTA  (seller > fname) – zmień seller_guess w 1. rekordzie
# podmieniamy pierwsze wystąpienie ACME… na bardzo inną nazwę
sed -i '0,/ACME Sp. z o.o./s//Totalnie Inny Kontrahent SA/' "$OUT/All_invoices.csv"

python pop_matcher.py \
  --pop populacja.xlsx \
  --pdf-root tie_pdfs \
  --index-csv "$OUT/All_invoices.csv" \
  --amount-tol 0.01 \
  --tiebreak-weight-fname 0.1 \
  --tiebreak-min-seller 40 \
  --out-jsonl "$OUT/verdicts_tb_seller.jsonl"

grep -q '"kryterium": "numer\+seller"' "$OUT/verdicts_tb_seller.jsonl" \
  && echo "OK: znaleziono numer+seller" \
  || { echo "FAIL: brak numer+seller"; sed -n '1,20p' "$OUT/verdicts_tb_seller.jsonl"; exit 1; }

echo "✅ SMOKE TIEBREAKER V2 – OK"
echo "Wyniki:"
echo " - $OUT/verdicts_tb_fname.jsonl"
echo " - $OUT/verdicts_tb_seller.jsonl"
