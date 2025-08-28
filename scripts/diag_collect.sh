#!/usr/bin/env bash
set -euo pipefail

# === USTAWIENIA PODSTAWOWE ===
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

LOG_DIR="logs/diag"
TS="$(date +"%Y%m%d_%H%M%S")"
OUT_DIR="$LOG_DIR/$TS"
mkdir -p "$OUT_DIR"
export OUT_DIR

log(){ printf "[diag] %s\n" "$*"; }

log "Repo root: $ROOT_DIR"
printf "%s\n" "$TS" > "$OUT_DIR/timestamp.txt"

# === INFO O GIT ===
if [ -d .git ]; then
  git status --porcelain=v1 > "$OUT_DIR/git_status.txt" || true
  git rev-parse --short HEAD > "$OUT_DIR/git_head.txt" || true
  git remote -v > "$OUT_DIR/git_remote.txt" || true
  git log --oneline -n 20 > "$OUT_DIR/git_log.txt" || true
  git branch -vv > "$OUT_DIR/git_branches.txt" || true
else
  echo "NO_GIT_REPO" > "$OUT_DIR/git.txt"
fi

# === SYSTEM & GPU ===
{
  echo "== uname -a =="; uname -a
  echo; echo "== lsb_release -a =="; lsb_release -a 2>/dev/null || echo "lsb_release not available"
} > "$OUT_DIR/system.txt"

{
  echo "== nvidia-smi -L =="; nvidia-smi -L 2>&1 || echo "nvidia-smi not available"
  echo; echo "== nvidia-smi query =="; nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader 2>&1 || true
} > "$OUT_DIR/gpu.txt"

{
  echo "== free -h =="; free -h || true
  echo; echo "== df -h =="; df -h || true
} > "$OUT_DIR/resources.txt"

# === PYTHON / VENV ===
{
  echo "== which python3 =="; command -v python3 || true
  echo "== system python3 --version =="; python3 --version || true
  echo "== .venv python --version =="; .venv/bin/python --version 2>/dev/null || echo ".venv python not available"
  echo "VIRTUAL_ENV=${VIRTUAL_ENV-<none>}"
} > "$OUT_DIR/python_env.txt"

.venv/bin/python - <<'PY' > "$OUT_DIR/python_check.txt" 2>&1 || true
import sys, importlib
mods=["streamlit","llama_cpp","pandas","matplotlib"]
def ver(m):
    try:
        x=importlib.import_module(m)
        return getattr(x,"__version__","unknown")
    except Exception as e:
        return f"ERR:{e}"
print("PY_VERSION:", sys.version.replace("\n"," "))
for m in mods:
    print(f"{m}:", ver(m))
PY

.venv/bin/pip freeze > "$OUT_DIR/pip_freeze.txt" 2>/dev/null || true
.venv/bin/pip list > "$OUT_DIR/pip_list.txt" 2>/dev/null || true

# === PROCES STREAMLIT / PORT 8501 ===
{
  echo "== streamlit process =="; pgrep -a -f "streamlit run app/Home.py" || true
  echo; echo "== port 8501 =="; ss -tulpn 2>/dev/null | grep -E ":8501\\b" || echo "no listener on 8501"
} > "$OUT_DIR/streamlit_process.txt"

# === .env.local (redakcja sekretów) ===
if [ -f ".env.local" ]; then
  sed -E 's/((TOKEN|KEY|SECRET|PASSWORD|PASS|API|AUTH|BEARER|COOKIE|CREDENTIALS|ACCESS|REFRESH)[A-Z_]*\s*=\s*).*/\1***REDACTED***/I' ".env.local" > "$OUT_DIR/env_local.redacted" || true
else
  echo "MISSING_ENV_LOCAL" > "$OUT_DIR/env_local.redacted"
fi

# === LISTA MODELI GGUF ===
python3 - <<'PY' > "$OUT_DIR/models.json"
import os, json, glob
candidates=[]
for base in ["./models", os.path.expanduser("~/models"), os.path.expanduser("~/Downloads")]:
    for p in glob.glob(os.path.join(base,"**","*.gguf"), recursive=True):
        try:
            st=os.stat(p)
            candidates.append({"path": os.path.abspath(p), "size_bytes": st.st_size, "mtime": int(st.st_mtime)})
        except FileNotFoundError:
            pass
candidates.sort(key=lambda x: -x["mtime"])
print(json.dumps(candidates[:100], indent=2))
PY

# === DRZEWO PROJEKTU (przycięte) ===
python3 - <<'PY' > "$OUT_DIR/tree.txt"
from pathlib import Path
skip = {".git",".venv","__pycache__",".mypy_cache",".pytest_cache",".idea",".vscode"}
def walk(p: Path, d=0, maxd=3):
    if d>maxd: return
    for ch in sorted(p.iterdir(), key=lambda x:(x.is_file(), x.name.lower())):
        if ch.name in skip: continue
        print("  "*d + ("📄 " if ch.is_file() else "📁 ") + ch.name)
        if ch.is_dir(): walk(ch, d+1, maxd)
walk(Path("."))
PY

# === CHECK: składnia plików w app/ ===
python3 - <<'PY' > "$OUT_DIR/syntax_check.txt"
import ast, pathlib
bad=[]
for p in pathlib.Path("app").rglob("*.py"):
    try:
        ast.parse(p.read_text(encoding="utf-8"))
    except Exception as e:
        bad.append((str(p), f"{type(e).__name__}: {e}"))
print("OK" if not bad else "\n".join(f"BAD {p}: {e}" for p,e in bad))
PY

# === DEMO CSV obecność ===
if [ -f "data/uploads/test_walidacja_ui.csv" ]; then
  echo "PRESENT" > "$OUT_DIR/demo_csv.txt"
else
  echo "MISSING data/uploads/test_walidacja_ui.csv" > "$OUT_DIR/demo_csv.txt"
fi

# === PODSUMOWANIE JSON ===
python3 - <<'PY' > "$OUT_DIR/summary.json"
import os, json
out = os.environ.get("OUT_DIR",".")
def read(p, default=""):
    try:
        with open(p,"r",encoding="utf-8",errors="ignore") as f: return f.read()
    except: return default

env_local = read(".env.local")
llm_path = None
for line in env_local.splitlines():
    if line.strip().startswith("LLM_GGUF="):
        llm_path = line.split("=",1)[1].strip().strip('"').strip("'")
        break

syntax = read(os.path.join(out,"syntax_check.txt")).strip()
streamlit = read(os.path.join(out,"streamlit_process.txt"))
models = read(os.path.join(out,"models.json"))

summary = {
  "has_env_local": os.path.exists(".env.local"),
  "llm_gguf_configured": bool(llm_path),
  "llm_gguf_path_exists": os.path.exists(llm_path) if llm_path else False,
  "syntax_ok": (syntax=="OK"),
  "streamlit_running": ("streamlit run app/Home.py" in streamlit),
  "models_indexed": models.count('"path":'),
}
print(json.dumps(summary, indent=2))
PY

# === SYMLINK "latest" ===
mkdir -p "$LOG_DIR"
rm -f "$LOG_DIR/latest"
ln -s "$TS" "$LOG_DIR/latest"

log "Diag complete → $OUT_DIR"
echo "[OK] Diag collected at: $OUT_DIR"
