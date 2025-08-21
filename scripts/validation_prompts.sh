#!/usr/bin/env bash
# Walidacja na danych demo (strict + fallback ANYWHERE)
set -e
export DONUT_MODEL="${DONUT_MODEL:-SKamor/ai-audytor-donut-local}"
export USE_DONUT=1
# KOSZTY
scripts/validate2.sh koszty strict
scripts/validate2.sh koszty anywhere1p
# PRZYCHODY
scripts/validate2.sh przychody strict
scripts/validate2.sh przychody anywhere1p
