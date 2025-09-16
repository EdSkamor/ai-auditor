#!/usr/bin/env bash
set -Eeuo pipefail

LOGDIR=".logs"
BE_LOG="$LOGDIR/backend.log"
FR_LOG="$LOGDIR/streamlit.log"
AUDIT_MD="SELF_AUDIT.md"

say(){ echo -e "\n=== [$(date '+%H:%M:%S')] $* ==="; }

say "Kill stale processes (uvicorn/streamlit/cloudflared/pytest)"
pkill -f "uvicorn" || true
pkill -f "streamlit run" || true
pkill -f "cloudflared" || true
pkill -f "pytest" || true

say "Free ports 8000/8501"
if command -v lsof >/dev/null 2>&1; then
  lsof -ti :8000 -sTCP:LISTEN | xargs -r kill -9 || true
  lsof -ti :8501 -sTCP:LISTEN | xargs -r kill -9 || true
fi

say "Prepare venv"
python3 -m venv .venv
source .venv/bin/activate
python -V
pip install -U pip wheel setuptools >/dev/null
pip install -r requirements.txt >/dev/null
pip install pytest pytest-timeout >/dev/null

mkdir -p "$LOGDIR"
: > "$BE_LOG"; : > "$FR_LOG"

export AIAUDITOR_PASSWORD="${AIAUDITOR_PASSWORD:-TwojPIN123!}"
export AIAUDITOR_MAX_FILE_MB="${AIAUDITOR_MAX_FILE_MB:-100}"
export BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8000}"

say "Repo info"
BR=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
MOD=$(git status --porcelain | wc -l | tr -d ' ')
echo "Branch: $BR  Commit: $SHA  Modified files: $MOD"

say "Static checks"
AI_SERVER_HITS=$(grep -R --line-number "AI_SERVER_URL" . || true)
REQ_TOTAL=$(grep -R -nE "requests\.(get|post)\(.*(healthz|ready|analyze|analyze-file)" app pages 2>/dev/null | wc -l | tr -d ' ')
REQ_WITH_AUTH=$(grep -R -nE "requests\.(get|post)\(.*(healthz|ready|analyze|analyze-file).*auth=" app pages 2>/dev/null | wc -l | tr -d ' ')
GATE_HIT=$(grep -R -n "st\.stop()" streamlit_app.py 2>/dev/null || true)
CFG_BACKEND=$(grep -R -n "BACKEND_URL" src/config.py 2>/dev/null || true)
SRV_PASS=$(grep -R -n "AIAUDITOR_PASSWORD" local_test/server.py 2>/dev/null || true)
SRV_LIM=$(grep -R -n "AIAUDITOR_MAX_FILE_MB" local_test/server.py 2>/dev/null || true)

say "Start backend (background) -> $BE_LOG"
uvicorn local_test.server:app --host 127.0.0.1 --port 8000 --log-level warning >>"$BE_LOG" 2>&1 &
BEPID=$!
cleanup(){ kill $BEPID 2>/dev/null || true; deactivate || true; }
trap cleanup EXIT

say "Wait for /healthz (max 40s)"
python - <<'PY'
import time,requests,sys
for i in range(40):
    try:
        r=requests.get("http://127.0.0.1:8000/healthz",timeout=2)
        print("healthz:",r.status_code, flush=True)
        if r.ok: sys.exit(0)
    except Exception as e:
        print("wait",type(e).__name__, flush=True)
    time.sleep(1)
print("TIMEOUT"); sys.exit(1)
PY

say "Curl smoke"
set +e
H=$(curl -sS -m 5 -w "%{http_code}" -o /dev/null http://127.0.0.1:8000/healthz)
R=$(curl -sS -m 5 -w "%{http_code}" -o /dev/null http://127.0.0.1:8000/ready)
A_code=$(curl -sS -m 10 -u ai-auditor:$AIAUDITOR_PASSWORD \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Ping"}' \
  -w "%{http_code}" -o .logs/analyze.out http://127.0.0.1:8000/analyze)
set -e

say "Short Streamlit probe (30s) -> $FR_LOG"
python - <<'PY'
import os,subprocess,time,signal,sys
env=os.environ.copy()
env["BACKEND_URL"]=env.get("BACKEND_URL","http://127.0.0.1:8000")
env["APP_PIN"]=env.get("AIAUDITOR_PASSWORD","TwojPIN123!")
p=subprocess.Popen(["streamlit","run","streamlit_app.py","--server.headless","true","--server.port","8501"],
                   stdout=open(".logs/streamlit.log","w"), stderr=subprocess.STDOUT, env=env)
try:
    for i in range(30):
        if p.poll() is not None:
            print(f"streamlit exited early with {p.returncode}")
            break
        time.sleep(1)
    else:
        print("streamlit alive 30s")
finally:
    try:
        p.terminate(); p.wait(timeout=5)
    except Exception:
        p.kill()
PY

say "Optional E2E"
if [ -f tests/test_e2e.py ]; then
  pytest -q -x --maxfail=1 --timeout=90 tests/test_e2e.py || true
fi

say "Generate SELF_AUDIT.md"
{
  echo "# AI-Auditor – Self Audit"
  echo
  echo "Branch: $BR  |  Commit: $SHA"
  echo
  echo "## Checklist"
  echo "- Menu gate (st.stop): $([ -n "$GATE_HIT" ] && echo '[x]' || echo '[ ]')"
  echo "- Unification BACKEND_URL (no AI_SERVER_URL): $([ -z "$AI_SERVER_HITS" ] && echo '[x]' || echo '[ ]')"
  if [ "$REQ_TOTAL" -gt 0 ] && [ "$REQ_TOTAL" -eq "$REQ_WITH_AUTH" ]; then
    echo "- BasicAuth on all API calls: [x] ($REQ_WITH_AUTH/$REQ_TOTAL)"
  else
    echo "- BasicAuth on all API calls: [ ] ($REQ_WITH_AUTH/$REQ_TOTAL)"
  fi
  echo "- Upload limit 100MB in backend: $([[ "$SRV_LIM" == *"100"* ]] && echo '[x]' || echo '[ ]')"
  echo
  echo "## Smoke-test results"
  echo "- /healthz HTTP $H"
  echo "- /ready   HTTP $R"
  echo "- /analyze HTTP $A_code"
  echo
  echo "## Key findings"
  echo "BACKEND_URL in src/config.py:"
  echo '```'
  echo "$CFG_BACKEND"
  echo '```'
  if [ -n "$AI_SERVER_HITS" ]; then
    echo "Occurrences of AI_SERVER_URL (should be 0):"
    echo '```'
    echo "$AI_SERVER_HITS"
    echo '```'
  fi
  echo
  echo "## Logs (tails)"
  echo "### backend.log (last 80 lines)"
  echo '```'
  tail -n 80 "$BE_LOG" || true
  echo '```'
  echo "### streamlit.log (last 80 lines)"
  echo '```'
  tail -n 80 "$FR_LOG" || true
  echo '```'
} > "$AUDIT_MD"

say "Done. See $AUDIT_MD"
cat "$AUDIT_MD"
