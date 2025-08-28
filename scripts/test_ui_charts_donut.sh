#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p data/exports

python - <<'PY'
import os, pathlib
import pandas as pd
from app.ui_charts import donut_from_series, reset_filters_button

# 1) Donut z serii statusów i zapis do pliku
s = pd.Series(["ok", "needs_review", "ok", None, "needs_review", "ok"])
out = donut_from_series(s, title="Test Donut", labels_map={"ok":"OK","needs_review":"Do weryfikacji","":"Brak"}, show_in_streamlit=False, save_path="data/exports/test_donut.png")

p = pathlib.Path(out)
assert p.exists() and p.stat().st_size > 1000, f"PNG nie powstał lub jest za mały: {out}"

# 2) „Reset filtrów” – poza Streamlit funkcja zwraca False i nie rzuca wyjątków
assert reset_filters_button(label="Reset filtrów (test)") is False

# 3) Weryfikacja nagłówka PNG
with open(out, "rb") as fh:
    head = fh.read(8)
assert head == b'\x89PNG\r\n\x1a\n', "Nagłówek pliku nie wygląda na PNG"

print("[PASS] ui_charts: donut + reset_filters_button OK")
print(out)
PY
