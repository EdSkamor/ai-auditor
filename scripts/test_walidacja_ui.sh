#!/usr/bin/env bash
set -o pipefail; set +e
cd "$(dirname "$0")/.." || exit 1
source .venv/bin/activate
set -a; [ -f .env.local ] && source .env.local; set +a
mkdir -p data/uploads

python - <<'PY'
import os, csv, random
from pathlib import Path

def pick_pdfs(root):
    if not root or not Path(root).is_dir():
        return []
    return [str(p) for p in Path(root).glob("*.pdf")][:10]

k = os.getenv("KOSZTY_FACT","")
p = os.getenv("PRZYCHODY_FACT","")
pdfs = pick_pdfs(k) or pick_pdfs(p)
out = Path("data/uploads/test_walidacja_ui.csv")
rows = []
for i, full in enumerate(pdfs[:3], start=1):
    name = Path(full).name
    status = random.choice(["ok","needs_review","ok"])
    status_alt = status
    rows.append({"id": i, "plik": name, "status": status, "status_alt": status_alt})

if not rows:
    print("[WARN] Nie znaleziono PDF-ów w KOSZTY_FACT/PRZYCHODY_FACT — link PDF może nie działać.")
    rows = [
        {"id": 1, "plik": "przyklad1.pdf", "status": "ok", "status_alt": "ok"},
        {"id": 2, "plik": "przyklad2.pdf", "status": "needs_review", "status_alt": "needs_review"},
        {"id": 3, "plik": "przyklad3.pdf", "status": "ok", "status_alt": "ok"},
    ]

out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["id","plik","status","status_alt"])
    w.writeheader()
    w.writerows(rows)
print(f"[OK] Wygenerowano: {out}  ({len(rows)} wierszy)")
PY

echo
echo "== Instrukcja =="
echo "1) Otwórz UI → 🧾 Walidacja"
echo "2) Wgraj: data/uploads/test_walidacja_ui.csv"
echo "3) Przetestuj: liczniki, filtr statusu, eksport CSV."
echo "4) Zostaw 1 wiersz po filtrach → pojawi się przycisk '📄 Otwórz PDF'."
