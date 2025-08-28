#!/usr/bin/env bash
set -o pipefail; set +e
cd "$(dirname "$0")/.." || exit 1
source .venv/bin/activate
set -a; [ -f .env.local ] && source .env.local; set +a
mkdir -p data/uploads logs

echo "== KOSZTY_FACT: ${KOSZTY_FACT:-<nie ustawiono>} =="

python - <<'PY'
import os, pandas as pd, ast
from pathlib import Path

# 1) Znajdź istniejący PDF (jeśli KOSZTY_FACT ustawione), aby link 'otwórz' miał szansę zadziałać
K = os.getenv("KOSZTY_FACT","")
pick = None
if K and Path(K).is_dir():
    for p in Path(K).glob("*.pdf"):
        pick = p.name
        break
if not pick:
    pick = "FV_demo.pdf"  # placeholder, jeśli brak PDF-ów

# 2) Zbuduj demo CSV z trzema przypadkami
rows = [
    {"plik": pick,            "status":"ok",         "status_alt":"ok",           "best_mode":"anchor","best_value":60000,  "best_diff_pct":0.0, "best_page":1, "note_alt":""},
    {"plik": pick,            "status":"mismatch",   "status_alt":"needs_review", "best_mode":"any",   "best_value":150000, "best_diff_pct":0.0, "best_page":1, "note_alt":"RES: filename"},
    {"plik": "brak.pdf",      "status":"missing_pdf","status_alt":"missing_pdf",  "best_mode":"-",     "best_value":None,   "best_diff_pct":None,"best_page":None,"note_alt":"brak pliku"},
]
df = pd.DataFrame(rows)
out = Path("data/uploads/test_walidacja.csv")
df.to_csv(out, index=False)
print(f"[OK] Wygenerowano {out} ({len(df)} wiersze)")

# 3) Szybkie sanity-checki na danych
needs = int((df["status_alt"]=="needs_review").sum())
print(f"[TEST] needs_review w CSV: {needs} (oczekiwane: 1)")

flt = df[df["status_alt"].isin(["needs_review"])]
print(f"[TEST] Po filtrze status_alt=needs_review: {len(flt)} (oczekiwane: 1)")

# 4) Sprawdź składnię i import strony Walidacja
page = Path("app/pages/01_Walidacja.py")
try:
    ast.parse(page.read_text(encoding="utf-8"), filename=str(page))
    print("[TEST] Składnia 01_Walidacja.py: OK")
except SyntaxError as e:
    print(f"[TEST] Składnia 01_Walidacja.py: BŁĄD -> {e}")
PY

# 5) (Opcjonalnie) test 'uploader' w trybie konsolowym – zapis 1 pliku i wpis do logs/upload.log
python - <<'PY'
from io import BytesIO
from pathlib import Path
try:
    from app.ui_upload import save_uploads
except Exception as e:
    print(f"[TEST-UPLOADER] import ui_upload: BŁĄD -> {e}")
else:
    class FakeUpload:
        def __init__(self, name, data: bytes):
            self.name = name; self._b = BytesIO(data)
        def getbuffer(self): return self._b.getbuffer()

    Path("data/uploads").mkdir(parents=True, exist_ok=True)
    saved = save_uploads([FakeUpload("probe_from_test.txt", b"hello")], "data/uploads")
    print(f"[TEST-UPLOADER] Zapisane: {saved}")
    print("[TEST-UPLOADER] Ostatnie wpisy logu (jeśli istnieje):")
    p = Path("logs/upload.log")
    if p.is_file():
        print(p.read_text(encoding="utf-8").splitlines()[-1:])
    else:
        print("brak logs/upload.log (to OK, jeśli logowanie nie jest włączone)")
PY

echo
echo "== Co dalej? =="
echo "1) Otwórz UI → 🧾 Walidacja"
echo "2) W sidebarze wgraj plik: data/uploads/test_walidacja.csv"
echo "3) Przetestuj filtry (status/status_alt), licznik needs_review i eksport CSV."
