#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

OUT_DIR="logs/diag/latest"
[ -L "$OUT_DIR" ] || { echo "[FAIL] missing logs/diag/latest"; exit 1; }

[ -f "$OUT_DIR/summary.json" ] || { echo "[FAIL] missing summary.json"; exit 1; }
python3 - <<'PY'
import json, os
p = os.path.join("logs","diag","latest","summary.json")
j = json.load(open(p,"r",encoding="utf-8"))
req = ["has_env_local","llm_gguf_configured","llm_gguf_path_exists","syntax_ok","streamlit_running","models_indexed"]
missing = [k for k in req if k not in j]
assert not missing, f"missing keys: {missing}"
print("[PASS] summary.json keys present")
PY

# ✅ Poprawna pętla: lista plików rozdzielona spacjami (bez nawiasów)
for f in git_status.txt python_check.txt streamlit_process.txt models.json syntax_check.txt tree.txt; do
  [ -f "$OUT_DIR/$f" ] || { echo "[FAIL] missing $f"; exit 1; }
done

echo "[PASS] diag artifacts exist in $OUT_DIR"
