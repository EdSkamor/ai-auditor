#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.." || exit 0
[ -f ".venv/bin/activate" ] && source .venv/bin/activate

FAILED=0

# A) DEMO
python gen_dummy_invoices.py && python gen_dummy_population.py
RUN_DIR="web_runs/smoke_demo_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RUN_DIR" && cp -f populacja.xlsx "$RUN_DIR/populacja.xlsx"
python run_audit.py --pdf-root demo_invoices --pop "$RUN_DIR/populacja.xlsx" --outdir "$RUN_DIR" || FAILED=1

# B) BULK 47
rm -rf demo_invoices_bulk && mkdir -p demo_invoices_bulk
for i in $(seq 1 35); do cp -f demo_invoices/f1_pln.pdf "demo_invoices_bulk/f1_$i.pdf"; done
for i in $(seq 1 10); do cp -f demo_invoices/f2_eur.pdf "demo_invoices_bulk/f2_$i.pdf"; done
cp -f demo_invoices/{f3_usd.pdf,f4_dup_pln.pdf} demo_invoices_bulk/ || true
RUN_DIR2="web_runs/smoke_bulk_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RUN_DIR2" && cp -f populacja.xlsx "$RUN_DIR2/populacja.xlsx"
python run_audit.py --pdf-root demo_invoices_bulk --pop "$RUN_DIR2/populacja.xlsx" --outdir "$RUN_DIR2" || FAILED=1

# C) ZIP 47
( cd demo_invoices_bulk && zip -q -r ../bulk_demo.zip . )
RUN_ZIP="web_runs/smoke_zip_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RUN_ZIP/pdfs" && cp -f populacja.xlsx "$RUN_ZIP/populacja.xlsx"
unzip -q bulk_demo.zip -d "$RUN_ZIP/pdfs"
python run_audit.py --pdf-root "$RUN_ZIP/pdfs" --pop "$RUN_ZIP/populacja.xlsx" --outdir "$RUN_ZIP" || FAILED=1

# D) OVERRIDE + RENAME
OV="$RUN_ZIP/overrides.csv"
echo "pozycja_id,sciezka_pdf" > "$OV"
echo "0,$(realpath "$RUN_ZIP/pdfs/$(ls -1 "$RUN_ZIP/pdfs" | grep -E '^f1_' | head -n1)")" >> "$OV"
python pop_matcher.py --pop "$RUN_ZIP/populacja.xlsx" --pdf-root "$RUN_ZIP/pdfs" \
  --index-csv "$RUN_ZIP/All_invoices.csv" --overrides "$OV" \
  --rename --apply --rename-dir "$RUN_ZIP/renamed" \
  --attach-col "ZAŁĄCZNIK" \
  --out-jsonl "$RUN_ZIP/verdicts_after.jsonl" \
  --out-xlsx "$RUN_ZIP/populacja_enriched_after.xlsx" || FAILED=1

# E) PACK
scripts/pack_run.sh "$RUN_ZIP" || FAILED=1
PKG="$(ls -t ${RUN_ZIP%/}/handoff_*.zip | head -n1 || true)"
echo "PKG=$PKG"
[ -f "$PKG" ] || FAILED=1
unzip -l "$PKG" | grep -E 'Audyt_koncowy|ExecutiveSummary|verdicts_summary|README|MANIFEST' || FAILED=1

if [ $FAILED -eq 0 ]; then
  echo "✅ SMOKE-ALL OK"
else
  echo "❌ SMOKE-ALL – znaleziono problemy"
fi
