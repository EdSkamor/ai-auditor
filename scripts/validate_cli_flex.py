import os, sys, json
from pathlib import Path
import pandas as pd

from services.extract_ai_donut import extract_fields
from services.compare import compare_row

def main(xlsx, faktury_dir, out_csv):
    df = pd.read_excel(xlsx)
    cols = {c.lower(): c for c in df.columns}
    need = ["data_dokumentu","numer_dokumentu","wartosc_netto_dokumentu","zalacznik"]
    for n in need:
        assert n in cols, f"Brak kolumny w arkuszu: {n}"
    df = df.rename(columns=cols)  # na wypadek wielkich liter

    root = Path(faktury_dir).resolve()
    out_rows = []
    for i, row in df.iterrows():
        attach = str(row.get("zalacznik") or "").strip()
        pdf_path = root/attach
        rec = {"wiersz": i+1, "plik": attach}

        if not pdf_path.is_file():
            rec["status"] = "missing_pdf"
            rec["mismatches"] = ""
            out_rows.append(rec); continue

        pdf_data = extract_fields(str(pdf_path))
        mism, cand = compare_row(row, pdf_data)

        if mism:
            rec["status"] = "mismatch"
            rec["mismatches"] = json.dumps(mism, ensure_ascii=False)
            # opcjonalnie podgląd co znalazł Donut
            rec["found_numer"] = cand.get("numer")
            rec["found_data"]  = str(cand.get("data") or "")
            rec["found_netto"] = cand.get("netto")
        else:
            rec["status"] = "ok"
            rec["mismatches"] = ""

        out_rows.append(rec)

    out = pd.DataFrame(out_rows)
    out.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"✅ Raport: {out_csv}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
