import sys, os, zipfile, csv
import pandas as pd
from dateutil import parser
from rapidfuzz import fuzz
from services.extract_ai_donut import extract_fields

def norm_num(x:str)->str:
    import re
    return re.sub(r"[^A-Z0-9]","", (x or "").upper())

def parse_date(s):
    try: return parser.parse(str(s), dayfirst=True).date()
    except: return None

def main(xlsx:str, zip_or_dir:str, out_csv:str):
    # 1) czytaj arkusz
    df = pd.read_excel(xlsx)
    cols = {c.strip().lower(): c for c in df.columns}
    need = ["data_dokumentu","numer_dokumentu","wartosc_netto_dokumentu","zalacznik"]
    for n in need:
        assert n in (k for k in cols), f"Brak kolumny w arkuszu: {n}"

    # 2) rozpakuj ZIP jeśli trzeba
    tmp_dir = None
    if os.path.isdir(zip_or_dir):
        base_dir = zip_or_dir
    else:
        import tempfile
        tmp_dir = tempfile.mkdtemp(prefix="aiauditor_zip_")
        with zipfile.ZipFile(zip_or_dir, 'r') as z: z.extractall(tmp_dir)
        base_dir = tmp_dir

    rows=[]
    for i, r in df.iterrows():
        attach = str(r[cols["zalacznik"]])
        # znajdź plik w base_dir (rekurencyjnie)
        target=None
        for root,_,files in os.walk(base_dir):
            for f in files:
                if attach in f:
                    target=os.path.join(root,f); break
            if target: break

        if not target:
            rows.append({"wiersz":i, "status":"missing_pdf", "uwagi":"nie znaleziono załącznika", "plik":attach})
            continue

        pdf = extract_fields(target)
        # porównanie
        status="ok"; mism=[]
        # numer
        rnum = norm_num(str(r[cols["numer_dokumentu"]]))
        pnum = norm_num(str(pdf.get("invoice_number") or ""))
        if rnum and pnum and fuzz.ratio(rnum,pnum) < 95:
            status="mismatch"; mism.append(("numer_dokumentu", r[cols["numer_dokumentu"]], pdf.get("invoice_number")))
        # data
        rd = parse_date(r[cols["data_dokumentu"]]); pd_ = parse_date(pdf.get("invoice_date"))
        if rd and pd_ and abs((rd-pd_).days) > 3:
            status="mismatch"; mism.append(("data_dokumentu", str(rd), str(pd_)))
        # kwota
        try: ra = float(r[cols["wartosc_netto_dokumentu"]])
        except: ra = None
        pa = None
        try: pa = float(str(pdf.get("net_amount")).replace(",",".")) if pdf.get("net_amount") is not None else None
        except: pass
        if ra is not None and pa is not None and abs(ra-pa) > 0.05:
            status="mismatch"; mism.append(("wartosc_netto_dokumentu", ra, pa))

        rows.append({
            "wiersz": i,
            "status": status,
            "mismatches": "; ".join([f"{f}:{a}->{b}" for f,a,b in mism]) if mism else "",
            "plik": os.path.basename(target),
            "invoice_number": pdf.get("invoice_number"),
            "invoice_date": pdf.get("invoice_date"),
            "net_amount": pdf.get("net_amount")
        })

    # 3) zapis CSV
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print("✅ Raport zapisany ->", out_csv)

if __name__ == "__main__":
    if len(sys.argv)<4:
        print("Użycie: python scripts/validate_cli.py <populacja.xlsx> <zip_lub_folder_z_pdf> <raport.csv>")
        sys.exit(2)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
