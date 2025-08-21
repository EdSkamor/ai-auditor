#!/usr/bin/env bash
# usage:
#   scripts/validate2.sh koszty strict
#   scripts/validate2.sh koszty anywhere1p
#   scripts/validate2.sh przychody strict
#   scripts/validate2.sh przychody anywhere1p
# env:
#   DONUT_MODEL=SKamor/ai-audytor-donut-local (domyślnie użyje HF)
#   USE_DONUT=1 (wymuś użycie Donut)
#   OMP_THREADS=4 (ile wątków na CPU)

# --- ensure PYTHONPATH points to repo root ---
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="${PYTHONPATH:-}"
case ":$PYTHONPATH:" in *":$ROOT:"*) ;; *) export PYTHONPATH="$ROOT:$PYTHONPATH" ;; esac



set -euo pipefail

KIND="${1:-}"
MODE="${2:-strict}"

if [[ -z "$KIND" ]]; then
  echo "Podaj: {koszty|przychody} oraz {strict|anywhere1p}"
  exit 2
fi

# znajdź wejścia
if [[ "$KIND" == "koszty" ]]; then
  RES="$(find data/incoming -type f -iwholename '*koszty*populacja_normalized_resolved.xlsx' | head -n1)"
  FACT="$(dirname "$RES")/../Faktury"
  OUT="out_koszty_${DONUT_MODEL:+hf}.csv"; OUT="${OUT//\//_}"; OUT="${OUT//:/_}"
elif [[ "$KIND" == "przychody" ]]; then
  RES="$(find data/incoming -type f -iwholename '*przychody*populacja_normalized_resolved.xlsx' | head -n1)"
  FACT="$(dirname "$RES")/../Faktury"
  OUT="out_przychody_${DONUT_MODEL:+hf}.csv"; OUT="${OUT//\//_}"; OUT="${OUT//:/_}"
else
  echo "Nieznany rodzaj: $KIND (dozwolone: koszty | przychody)"; exit 2
fi

[[ -f "$RES" ]] || { echo "❌ Nie znalazłem arkusza: $RES"; exit 3; }
[[ -d "$FACT" ]] || { echo "❌ Nie znalazłem katalogu z PDF: $FACT"; exit 3; }

: "${OMP_THREADS:=4}"
export USE_DONUT="${USE_DONUT:-1}"

echo "== Walidacja ($KIND) =="
echo "RES=$RES"
echo "FACT=$FACT"
echo "MODEL=${DONUT_MODEL:-<lokalny>}"
echo "TRYB=$MODE"
echo

# 1) walidacja podstawowa
CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS="$OMP_THREADS" \
python3 scripts/validate_cli_flex.py "$RES" "$FACT" "$OUT"

# 2) opcjonalny post-proces ANYWHERE ≤1%
if [[ "$MODE" == "anywhere1p" ]]; then
  OUT2="${OUT%.csv}_anywhere.csv"
  CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS="$OMP_THREADS" \
  python3 scripts/recheck_anywhere.py "$RES" "$FACT" "$OUT" "$OUT2" --pct 1.0
fi

# 3) szybkie podsumowanie
python - <<PY
import os, pandas as pd, sys
for f in ("$OUT", "${OUT%.csv}_anywhere.csv"):
    if os.path.isfile(f):
        s=pd.read_csv(f)["status"].value_counts(dropna=False).to_string()
        print(f"== {f} ==\n{s}\n")
PY
