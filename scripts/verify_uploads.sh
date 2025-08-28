#!/usr/bin/env bash
set -o pipefail; set +e
cd "$(dirname "$0")/.." || exit 1
source .venv/bin/activate
set -a; [ -f .env.local ] && source .env.local; set +a

echo "== Ścieżki =="
printf "CHAT uploads:   %s\n" "$(realpath -m data/uploads)"
printf "KOSZTY_FACT:    %s\n" "${KOSZTY_FACT:-<nie ustawiono>}"
printf "PRZYCHODY_FACT: %s\n\n" "${PRZYCHODY_FACT:-<nie ustawiono>}"

report_dir () {
  local d="$1" title="$2"
  [ -z "$d" ] && return
  [ ! -d "$d" ] && { echo "— $title: katalog nie istnieje: $d"; return; }
  echo "== $title ($d) =="
  echo "(ostatnie 10)"
  find "$d" -maxdepth 1 -type f -printf '%TY-%Tm-%Td %TT  %9s  %p\n' | sort -r | head
  echo
}

report_dir "data/uploads" "CHAT uploads"
report_dir "$KOSZTY_FACT" "KOSZTY_FACT"
report_dir "$PRZYCHODY_FACT" "PRZYCHODY_FACT"

echo "Tip: zostaw to okno i wgraj plik w UI — po chwili uruchom ponownie skrypt."
