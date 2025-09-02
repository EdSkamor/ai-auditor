#!/usr/bin/env bash
set -u  # bez -e, żeby nie zamykać konsoli
cd "$(dirname "$0")/.." || exit 0

# venv (opcjonalnie)
[ -f ".venv/bin/activate" ] && source .venv/bin/activate

ZIP="${1:-}"
POP="${2:-populacja.xlsx}"

if [ -z "$ZIP" ] || [ ! -f "$ZIP" ]; then
  echo "Użycie: scripts/audit_zip.sh <pakiet.zip> [populacja.xlsx]"
  exit 0
fi

ts="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="web_runs/zip_${ts}"
mkdir -p "$RUN_DIR/pdfs"
cp -f "$POP" "$RUN_DIR/populacja.xlsx" 2>/dev/null || true
unzip -q "$ZIP" -d "$RUN_DIR/pdfs"

python run_audit.py --pdf-root "$RUN_DIR/pdfs" --pop "$RUN_DIR/populacja.xlsx" --outdir "$RUN_DIR" --amount-tol 0.01

# Executive Summary (jeśli są wyniki)
if [ -f "$RUN_DIR/verdicts_summary.json" ] && [ -f "$RUN_DIR/All_invoices.csv" ]; then
  python make_exec_summary.py \
    --summary   "$RUN_DIR/verdicts_summary.json" \
    --mismatches "$RUN_DIR/All_invoices.csv" \
    --out       "$RUN_DIR/invoices_report_ExecutiveSummary.pdf" \
    --title     "Asystent Audytora – Executive Summary"
fi

echo "== WYNIKI ($RUN_DIR) =="
ls -1 "$RUN_DIR" 2>/dev/null || true
