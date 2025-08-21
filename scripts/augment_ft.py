from pathlib import Path
import pandas as pd, json, random, re

IN_ROOT = Path("data/incoming")
OUT = Path("data/ft/train_aug.jsonl")
OUT.parent.mkdir(parents=True, exist_ok=True)

def coerce_float(x):
    try: return float(str(x).replace(",",".")) if x is not None else None
    except: return None

def rows_from_file(p: Path):
    try:
        if p.suffix.lower()==".xlsx":
            df = pd.read_excel(p)
        elif p.suffix.lower()==".csv":
            df = pd.read_csv(p)
        else:
            return []
    except Exception:
        return []
    cols = [c.strip().lower() for c in df.columns]
    need = {"data_dokumentu","numer_dokumentu","wartosc_netto_dokumentu","zalacznik"}
    if not need.issubset(set(cols)):
        return []
    # normalizuj kolumny do nazw docelowych
    df.columns = cols
    out=[]
    for _,r in df.iterrows():
        out.append({
            "data_dokumentu": str(r.get("data_dokumentu", "")),
            "numer_dokumentu": str(r.get("numer_dokumentu", "")),
            "wartosc_netto_dokumentu": coerce_float(r.get("wartosc_netto_dokumentu")),
            "zalacznik": str(r.get("zalacznik",""))
        })
    return out

def qa_cases(row):
    base_prefix = "Populacja zal 621"  # sam wzorzec, bez uzależniania od danych klienta
    cases = []
    # 1) OK
    q = "Zwaliduj rekord (data/numer/kwota) względem PDF i zaproponuj nazwę pliku wg wzorca."
    a = (
        "- status=ok; brak rozbieżności.\n"
        f"- nazwa: '{base_prefix}, faktura - zal 621-01'.\n"
        "- loguj mapowanie stara->nowa (bez nadpisywania)."
    )
    cases.append((q,a))
    # 2) brak PDF
    q = "Załącznik z fakturą nie istnieje. Jak to ująć w raporcie?"
    a = "- status='missing_pdf'; nie porównuj pól; dodaj do listy uzupełnień; ostrzeż w raporcie zbiorczym."
    cases.append((q,a))
    # 3) data przesunięta
    shift = random.randint(2,5)
    q = f"Data w PDF różni się o {shift} dni od arkusza."
    a = f"- tolerancja ±1–3 dni; przy {shift}d zgłoś mismatch pola 'data_dokumentu' (arkusz vs PDF)."
    cases.append((q,a))
    # 4) drobna różnica kwoty
    q = "Kwota netto w PDF różni się o 0.12."
    a = "- mismatch w 'wartosc_netto_dokumentu'; wskaż obie wartości; dodaj uwagę o zaokrągleniach."
    cases.append((q,a))
    # 5) inny format numeru (separatory)
    q = "Numer w PDF ma inny format (np. separatory / i -)."
    a = "- użyj fuzzy match na znormalizowanych numerach; jeśli score<95 → mismatch; pokaż arkusz vs PDF."
    cases.append((q,a))
    return cases

records=[]
files = list(IN_ROOT.rglob("*.xlsx")) + list(IN_ROOT.rglob("*.csv"))
for p in files:
    for row in rows_from_file(p):
        for q,a in qa_cases(row):
            records.append({
              "messages":[
                {"role":"system","content":"Jesteś ekspertem ds. audytu finansowego. Odpowiadasz zwięźle po polsku; wypunktowania mile widziane."},
                {"role":"user","content":q},
                {"role":"assistant","content":a}
              ],
              "meta":{"source":str(p)}
            })

# fallback: jeśli nie znaleziono arkuszy, wygeneruj 200 neutralnych przykładów
if not records:
    for i in range(200):
        q = "Zwaliduj data/numer/kwota vs PDF i nadaj nazwę wg 'Populacja zal 621, faktura - zal 621-x'."
        a = "- sprawdź trzy pola; raportuj 'missing_pdf' lub 'mismatch:{pole}'; nazwę nadaj z indeksem x i loguj mapowanie."
        records.append({"messages":[
            {"role":"system","content":"Jesteś ekspertem ds. audytu finansowego. Odpowiadasz zwięźle po polsku; wypunktowania mile widziane."},
            {"role":"user","content":q},
            {"role":"assistant","content":a}
        ]})

with OUT.open("w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False)+"\n")

print(f"aug examples: {len(records)} -> {OUT}")
