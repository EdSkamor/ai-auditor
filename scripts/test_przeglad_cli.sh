#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p data/uploads data/decisions data/exports logs

# Demo CSV
cat > data/uploads/test_przeglad_ui.csv <<'CSV'
id,kwota,status
A1,100,needs_review
A2,200,ok
A3,300,needs_review
CSV

python - <<'PY'
import os, pathlib, importlib.util, pandas as pd
base = pathlib.Path.cwd()
os.environ["AIAUDYTOR_NO_UI"] = "1"

page_path = base / "app/pages/02_Przeglad.py"
spec = importlib.util.spec_from_file_location("przeglad_page", str(page_path))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

csv_name = "test_przeglad_ui.csv"
mod.save_decisions(csv_name, [0, 2], "Zatwierdź")
out_path, n, counts = mod.export_with_decisions(csv_name)

df = pd.read_csv(out_path)
got = df["decision"].fillna("").tolist()
expected = ["Zatwierdź", "", "Zatwierdź"]

assert n == 3, f"Spodziewane 3 wiersze, otrzymano {n}"
assert got == expected, f"Kolumna 'decision' różni się: {got} != {expected}"

print("[PASS] Przegląd: zapis i eksport decyzji działa.")
print(out_path)
PY
