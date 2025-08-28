#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

P="app/pages/02_Przeglad.py"

# 1) Sprawdź, że pierwsza niepusta i niekomentowana linia to 'from __future__ import annotations'
python3 - <<'PY'
import re
p="app/pages/02_Przeglad.py"
lines=open(p,encoding="utf-8").read().splitlines()
first_real=None
for ln in lines:
    if not ln.strip():
        continue
    if ln.lstrip().startswith("#"):
        continue
    first_real=ln
    break
assert first_real is not None, "empty file?"
assert first_real.strip()=="from __future__ import annotations", f"first real line is not future import: {first_real!r}"
print("[PASS] future import is first line")
PY

# 2) Sprawdź składnię (kompilacja do bytecode)
python3 - <<'PY'
import ast, sys
p="app/pages/02_Przeglad.py"
ast.parse(open(p,encoding="utf-8").read())
print("[PASS] syntax OK:", p)
PY

echo "[PASS] future+syntax checks OK"
