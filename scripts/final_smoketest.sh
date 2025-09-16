#!/usr/bin/env bash
set -Eeuo pipefail

LOGDIR=".logs"
mkdir -p "$LOGDIR"
BE_LOG="$LOGDIR/backend.log"
FR_LOG="$LOGDIR/streamlit.log"

say() { echo -e "\n=== [$(date '+%H:%M:%S')] $* ==="; }

say "Kill stale processes"
pkill -f "uvicorn" || true
pkill -f "streamlit run" || true
pkill -f "cloudflared" || true
pkill -f "pytest" || true

say "Free ports 8000/8501"
if command -v lsof >/dev/null 2>&1; then
  lsof -ti :8000 -sTCP:LISTEN | xargs -r kill -9 || true
  lsof -ti :8501 -sTCP:LISTEN | xargs -r kill -9 || true
else
  ss -ltnp 2>/dev/null | awk '$4 ~ /:8000$/ {print $7}' | sed -n 's/.*pid=\([0-9]\+\).*/\1/p' | xargs -r kill -9 || true
  ss -ltnp 2>/dev/null | awk '$4 ~ /:8501$/ {print $7}' | sed -n 's/.*pid=\([0-9]\+\).*/\1/p' | xargs -r kill -9 || true
fi

say "Prepare venv"
[ -d .venv ] && [ ! -x .venv/bin/python ] && rm -rf .venv || true
python3 -m venv .venv
source .venv/bin/activate
python -V
pip install -U pip wheel setuptools
pip install -r requirements.txt
pip install pytest pytest-timeout torch transformers

export AIAUDITOR_PASSWORD="TwojPIN123!"
export AIAUDITOR_MAX_FILE_MB=100
export BACKEND_URL="http://127.0.0.1:8000"

say "Start backend -> $BE_LOG"
: > "$BE_LOG"
uvicorn local_test.server:app --host 127.0.0.1 --port 8000 --log-level warning >>"$BE_LOG" 2>&1 &
BEPID=$!
trap 'kill $BEPID 2>/dev/null || true' EXIT

say "Wait for /healthz (max 40s)"
python - <<'PY'
import time,requests,sys
for i in range(40):
    try:
        r=requests.get("http://127.0.0.1:8000/healthz",timeout=2)
        print("healthz:",r.status_code, flush=True)
        if r.ok: sys.exit(0)
    except Exception as e:
        print("wait", type(e).__name__, flush=True)
    time.sleep(1)
print("TIMEOUT waiting for /healthz", flush=True); sys.exit(1)
PY

say "Curl smoke - basic endpoints"
set -x
curl -fsS -m 5 http://127.0.0.1:8000/healthz | head -c 300; echo
curl -fsS -m 5 http://127.0.0.1:8000/ready   | head -c 300; echo
set +x

say "Test analyze endpoint without waiting for model (expect 503)"
set -x
curl -fsS -m 10 -u ai-auditor:TwojPIN123! \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Ping"}' \
  http://127.0.0.1:8000/analyze | head -c 300; echo
set +x

say "Start Streamlit 30s probe -> $FR_LOG"
: > "$FR_LOG"
python - <<'PY'
import os,subprocess,time,sys,signal
env=os.environ.copy()
p=subprocess.Popen(["streamlit","run","streamlit_app.py","--server.headless","true","--server.port","8501"],
                   stdout=open(".logs/streamlit.log","w"), stderr=subprocess.STDOUT, env=env)
try:
    for i in range(30):
        time.sleep(1)
        if p.poll() is not None:
            raise SystemExit(f"streamlit exited with {p.returncode}")
    print("streamlit alive for 30s")
finally:
    try:
        p.terminate()
        p.wait(timeout=5)
    except Exception:
        p.kill()
PY

say "Run short E2E (skip if file missing)"
if [ -f tests/test_e2e.py ]; then
  export RUN_E2E=1
  export BASIC_AUTH_USER=ai-auditor
  export BASIC_AUTH_PASS=TwojPIN123!
  pytest -q -x --maxfail=1 --timeout=90 tests/test_e2e.py || echo "E2E tests failed (expected without model)"
else
  echo "No tests/test_e2e.py – skipping"
fi

say "SUMMARY"
echo "Backend log:   $BE_LOG (tail -n 80 $BE_LOG)"
echo "Streamlit log: $FR_LOG (tail -n 80 $FR_LOG)"
deactivate
