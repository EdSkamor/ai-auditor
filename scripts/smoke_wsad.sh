set -euo pipefail
cd ~/ai-audytor
source .venv/bin/activate

python gen_dummy_invoices.py
python gen_dummy_population.py
python run_audit.py --pdf-root demo_invoices --pop populacja.xlsx --amount-tol 0.01

last_run=$(ls -1 runs | sort | tail -n1)
echo "LAST RUN = runs/$last_run"

test -f "runs/$last_run/verdicts_summary.json"
test -f "runs/$last_run/Audyt_koncowy.xlsx"

python - <<'PY'
import json, glob, os, sys
d = sorted(glob.glob("runs/*"))[-1]
S = json.load(open(os.path.join(d,"verdicts_summary.json"), encoding="utf-8"))
m = S.get("metryki", {})
ok = bool(m.get("liczba_pozycji_koszty",0) + m.get("liczba_pozycji_przychody",0) > 0)
print(json.dumps(S, ensure_ascii=False, indent=2))
sys.exit(0 if ok else 2)
PY
