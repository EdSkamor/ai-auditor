#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.." || exit 0
[ -f ".venv/bin/activate" ] && source .venv/bin/activate

rm -rf perf_200 && mkdir -p perf_200
for i in $(seq 1 200); do cp -f demo_invoices/f1_pln.pdf "perf_200/f1_$i.pdf"; done

RUN_DIR="web_runs/perf200_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RUN_DIR" && cp -f populacja.xlsx "$RUN_DIR/populacja.xlsx"

ts=$(date +%s)
python run_audit.py --pdf-root perf_200 --pop "$RUN_DIR/populacja.xlsx" --outdir "$RUN_DIR"
dur=$(( $(date +%s) - ts ))
echo "Czas: ${dur}s"
ls -lh "$RUN_DIR/All_invoices.csv" "$RUN_DIR/Audyt_koncowy.xlsx"
