#!/usr/bin/env bash
cd "$(dirname "$0")/.." || exit 1
source .venv/bin/activate
set -o pipefail; set +e
set -a; [ -f .env.local ] && source .env.local; set +a
export PYTHONPATH="$PWD:$PYTHONPATH"
pkill -f -TERM "streamlit run app/Home.py" 2>/dev/null || true
nohup env PYTHONPATH="$PWD" streamlit run app/Home.py --server.port 8501 --server.headless=true \
  > logs/ui_home.txt 2>&1 &
echo "PID: $!  | URL: http://localhost:8501"
