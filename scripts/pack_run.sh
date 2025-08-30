#!/usr/bin/env bash
set -u
set -o pipefail

cd "$(dirname "$0")/.." || exit 0

latest_run() { ls -td web_runs/*/ 2>/dev/null | head -n1; }

RUN_DIR=""
WITH_PDFS=0
for a in "$@"; do
  case "$a" in
    --with-pdfs) WITH_PDFS=1 ;;
    *) RUN_DIR="$a" ;;
  esac
done
[ -z "${RUN_DIR:-}" ] && RUN_DIR="$(latest_run)"
if [ -z "${RUN_DIR:-}" ] || [ ! -d "$RUN_DIR" ]; then
  echo "Użycie: scripts/pack_run.sh [web_runs/<run_dir>] [--with-pdfs]"
  exit 0
fi

RUN_DIR="${RUN_DIR%/}"
BASE="$(basename "$RUN_DIR")"
TS="$(date +%Y%m%d_%H%M%S)"
STAGE="$RUN_DIR/pack_stage_$TS"
PKG="$RUN_DIR/handoff_${BASE}_${TS}.zip"

mkdir -p "$STAGE"

# 1) pliki główne
FILES="Audyt_koncowy.xlsx All_invoices.csv populacja_enriched.xlsx verdicts.jsonl verdicts_summary.json verdicts_top50_mismatches.csv invoices_report_ExecutiveSummary.pdf overrides.csv"
for f in $FILES; do
  if [ -f "$RUN_DIR/$f" ]; then
    cp -f "$RUN_DIR/$f" "$STAGE/"; echo "→ add $f"
  fi
done

# 2) katalogi wynikowe
if [ -d "$RUN_DIR/renamed" ]; then
  mkdir -p "$STAGE/renamed"
  cp -f "$RUN_DIR"/renamed/*.pdf "$STAGE/renamed/" 2>/dev/null || true
  echo "→ add renamed/"
fi
if [ $WITH_PDFS -eq 1 ] && [ -d "$RUN_DIR/pdfs" ]; then
  mkdir -p "$STAGE/pdfs"
  cp -f "$RUN_DIR"/pdfs/*.pdf "$STAGE/pdfs/" 2>/dev/null || true
  echo "→ add pdfs/ (RAW)"
fi

# 3) README z metrykami
{
  echo "# Asystent Audytora – paczka do przekazania"
  echo "- Run: $BASE"
  echo "- Data wygenerowania: $(date '+%Y-%m-%d %H:%M:%S')"
  echo
  echo "## Co jest w środku"
  echo "- Audyt_koncowy.xlsx – raport końcowy"
  echo "- invoices_report_ExecutiveSummary.pdf – skrócone podsumowanie (jeśli obecne)"
  echo "- All_invoices.csv – zindeksowane faktury"
  echo "- verdicts_summary.json / verdicts.jsonl – metryki i szczegóły dopasowań"
  echo "- populacja_enriched.xlsx – wzbogacona populacja"
  [ $WITH_PDFS -eq 1 ] && echo "- pdfs/ – surowe PDF-y (opcjonalne)"
  [ -d "$RUN_DIR/renamed" ] && echo "- renamed/ – PDF-y po ustandaryzowaniu nazw"
  echo
  echo "## Metryki"
  python - "$RUN_DIR" <<'PY' 2>/dev/null || true
import json, os, sys
run_dir = sys.argv[1]
p = os.path.join(run_dir,"verdicts_summary.json")
try:
  S = json.load(open(p,encoding="utf-8"))
  M = S.get("metryki",{})
  print(f"- liczba_pozycji_koszty: {M.get('liczba_pozycji_koszty')}")
  print(f"- liczba_pdf_koszty: {M.get('liczba_pdf_koszty')}")
  print(f"- liczba_pozycji_przychody: {M.get('liczba_pozycji_przychody')}")
  print(f"- liczba_pdf_przychody: {M.get('liczba_pdf_przychody')}")
  print(f"- braki_pdf: {M.get('braki_pdf')}")
  print(f"- niezgodnosci: {M.get('niezgodnosci')}")
except Exception as e:
  print(f"(brak metryk: {e})")
PY
  echo
  echo "## Manifest"
} > "$STAGE/README.txt"

# 4) checksumy (kolejność opcji w 'find' poprawna)
if command -v sha256sum >/dev/null 2>&1; then
  ( cd "$STAGE" && find . -maxdepth 2 -type f -print0 | sort -z | xargs -0 sha256sum > MANIFEST.sha256 )
fi

# 5) ZIP – tworzymy w katalogu RUN_DIR (wychodzimy jeden poziom w górę ze STAGE)
( cd "$STAGE" && zip -q -r "../handoff_${BASE}_${TS}.zip" . )
echo "OK -> $PKG"

# Info
unzip -l "$PKG" 2>/dev/null | sed -n '1,200p'

# [addon] append run_metadata.json / ExecutiveSummary.pdf if present
RUN_DIR="${1:-${RUN_DIR:-}}"
ZIP="$(find "$RUN_DIR" -maxdepth 1 -name "*.zip" -type f -printf "%T@ %p\n" | sort -nr | head -1 | awk "{print \$2}")"
[ -n "$ZIP" ] && [ -f "$RUN_DIR/run_metadata.json" ] && zip -j -u "$ZIP" "$RUN_DIR/run_metadata.json" >/dev/null && echo "→ appended run_metadata.json"
[ -n "$ZIP" ] && [ -f "$RUN_DIR/ExecutiveSummary.pdf" ] && zip -j -u "$ZIP" "$RUN_DIR/ExecutiveSummary.pdf" >/dev/null && echo "→ appended ExecutiveSummary.pdf"
