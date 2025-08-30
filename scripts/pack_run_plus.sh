#!/usr/bin/env bash
set -uo pipefail
RUN="${1:-}"
[ -z "$RUN" ] && { echo "Użycie: $0 <RUN_DIR>"; exit 2; }
# 1) standardowy pack
bash scripts/pack_run.sh "$RUN" || exit $?
# 2) znajdź świeży ZIP
ZIP="$(find "$RUN" -maxdepth 1 -name '*.zip' -type f -printf '%T@ %p\n' | sort -nr | head -1 | awk '{print $2}')"
[ -z "$ZIP" ] && { echo "Brak ZIP w $RUN"; exit 3; }
# 3) dopnij metadane (jeśli brak – pomiń z komunikatem)
[ -f "$RUN/run_metadata.json" ] && zip -j -u "$ZIP" "$RUN/run_metadata.json" >/dev/null && echo "→ appended run_metadata.json"
# 4) dopnij ExecutiveSummary.pdf, jeśli istnieje
[ -f "$RUN/ExecutiveSummary.pdf" ] && zip -j -u "$ZIP" "$RUN/ExecutiveSummary.pdf" >/dev/null && echo "→ appended ExecutiveSummary.pdf"
echo "OK -> $ZIP"
