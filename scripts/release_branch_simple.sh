#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

BR="${1:-release/client-pack}"

# Upewnij się, że pliki pakietu są wygenerowane
[ -f Dockerfile ] || ./scripts/client_pack_simple.sh >/dev/null

# Wymagane pliki do commita
FILES=(
  Dockerfile
  docker-compose.yml
  .dockerignore
  .env.sample
  docs/QUICKSTART.md
  scripts/client_pack_simple.sh
)

# Sprawdź repo
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "[FAIL] not a git repo"; exit 1; }

# Gałąź
git checkout -B "$BR"

# Dodaj pliki i commit
git add "${FILES[@]}" || true
git commit -m "chore: client pack (Docker CPU, compose, env sample, QUICKSTART)" || true

# Jeśli jest pre-commit, uruchom i zatwierdź poprawki
if command -v pre-commit >/dev/null 2>&1; then
  pre-commit run -a || true
  git add -A
  git commit -m "chore: format (pre-commit)" || true
fi

echo "[OK] Branch prepared: $BR"
echo "[NEXT] push with: git push -u origin $BR"
