#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

./scripts/release_branch_simple.sh >/dev/null

CUR=$(git rev-parse --abbrev-ref HEAD)
[ "$CUR" = "release/client-pack" ] || { echo "[FAIL] wrong branch: $CUR"; exit 1; }

# Sprawdź, że pliki są śledzone w repo
for f in Dockerfile docker-compose.yml .dockerignore .env.sample docs/QUICKSTART.md scripts/client_pack_simple.sh; do
  git ls-files --error-unmatch "$f" >/dev/null 2>&1 || { echo "[FAIL] not tracked: $f"; exit 1; }
done

echo "[PASS] release branch prepared: $CUR"
echo "[NEXT] push with: git push -u origin $CUR"
