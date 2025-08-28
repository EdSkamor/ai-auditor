#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p data/uploads data/decisions data/exports logs
rm -f data/decisions/test_przeglad_ui__decisions.csv data/exports/test_przeglad_ui__with_decisions.csv || true

# Demo CSV
cat > data/uploads/test_przeglad_ui.csv <<'CSV'
id,kwota,status
A1,100,needs_review
A2,200,ok
A3,300,needs_review
CSV

python - <<'PY'
import os, pathlib, importlib.util
import pandas as pd

base = pathlib.Path.cwd()
os.environ["AIAUDYTOR_NO_UI"] = "1"

page_path = base / "app/pages/02_Przeglad.py"
spec = importlib.util.spec_from_file_location("przeglad_page", str(page_path))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

csv_name = "test_przeglad_ui.csv"

# 1) Na czysto: 3 nierozstrzygnięte
counts = mod.summarize_current(csv_name, 3)
assert counts.get("", 0) == 3 and counts.get("Zatwierdź", 0) == 0 and counts.get("Odrzuć", 0) == 0, counts

# 2) Dwie decyzje 'Zatwierdź' dla 0 i 2
mod.save_decisions(csv_name, [0, 2], "Zatwierdź")
counts = mod.summarize_current(csv_name, 3)
assert counts.get("Zatwierdź", 0) == 2 and counts.get("", 0) == 1, counts

# 3) Nadpisz jedną decyzję: 2 -> 'Odrzuć'
mod.save_decisions(csv_name, [2], "Odrzuć")
counts = mod.summarize_current(csv_name, 3)
assert counts.get("Zatwierdź", 0) == 1 and counts.get("Odrzuć", 0) == 1 and counts.get("", 0) == 1, counts

print("[PASS] summarize_current działa poprawnie.")
PY
