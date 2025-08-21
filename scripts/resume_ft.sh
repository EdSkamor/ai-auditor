#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
source .venv/bin/activate
if ! ps -p $(cat donut_ft.pid 2>/dev/null) >/dev/null 2>&1; then
  nohup python -u scripts/train_donut_safe.py >> logs_donut_ft.txt 2>&1 & echo $! > donut_ft.pid
  echo "🔁 wznowiono: $(cat donut_ft.pid)"
else
  echo "✅ FT działa: $(cat donut_ft.pid)"
fi
tail -n 50 logs_donut_ft.txt
