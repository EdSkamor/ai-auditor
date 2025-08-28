#!/usr/bin/env bash
set -o pipefail; set +e
ROOTS=("$HOME/models" "$HOME/Downloads" "$PWD/models")
echo "== Szukam *.gguf w: ${ROOTS[*]}"
found=()
for d in "${ROOTS[@]}"; do
  [ -d "$d" ] || continue
  while IFS= read -r -d '' f; do
    found+=("$f")
  done < <(find "$d" -type f -name "*.gguf" -print0 2>/dev/null)
done
if [ ${#found[@]} -eq 0 ]; then
  echo "Brak .gguf — wrzuć modele do ~/models i uruchom ponownie."
  exit 0
fi
printf "%3s | %s\n" "No" "Ścieżka"
printf "%3s-+-%s\n" "---" "---------------------"
i=0
for f in "${found[@]}"; do
  printf "%3d | %s\n" "$i" "$f"
  i=$((i+1))
done
echo
echo "Aby ustawić ALT:  echo 'LLM_GGUF_ALT=\"<pełna_ścieżka>\"' >> .env.local"
