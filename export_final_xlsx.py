from __future__ import annotations
import json, argparse, pandas as pd
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", default="verdicts_summary.json")
    ap.add_argument("--verdicts", default="verdicts.jsonl")
    ap.add_argument("--rename-map", default=None, help="opcjonalny CSV z mapą rename (src,dst)")
    ap.add_argument("--out-xlsx", default="Audyt_koncowy.xlsx")
    args = ap.parse_args()

    out_path = Path(args.out_xlsx)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Metryki
    S = json.load(open(args.summary, "r", encoding="utf-8"))
    df_m = pd.DataFrame([S.get("metryki", {})])

    # Uwagi
    uw = S.get("uwagi_globalne", [])
    df_u = pd.DataFrame({"uwagi_globalne": uw}) if uw else pd.DataFrame(columns=["uwagi_globalne"])

    # Niezgodności (lista)
    mis_rows=[]
    with open(args.verdicts, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            j = json.loads(line)
            if j.get("zgodnosc") == "NIE":
                mis_rows.append({
                    "sekcja": j.get("sekcja"),
                    "pozycja_id": j.get("pozycja_id"),
                    "kryterium": j.get("dopasowanie",{}).get("kryterium"),
                    "confidence": j.get("dopasowanie",{}).get("confidence"),
                    "numer_pop": j.get("numer_pop"),
                    "data_pop": j.get("data_pop"),
                    "netto_pop": j.get("netto_pop"),
                    "numer_pdf": j.get("wyciagniete",{}).get("numer_pdf"),
                    "data_pdf": j.get("wyciagniete",{}).get("data_pdf"),
                    "netto_pdf": j.get("wyciagniete",{}).get("netto_pdf"),
                    "por_numer": j.get("porownanie",{}).get("numer"),
                    "por_data": j.get("porownanie",{}).get("data"),
                    "por_netto": j.get("porownanie",{}).get("netto"),
                    "pdf_sciezka": j.get("pdf",{}).get("sciezka"),
                })
    df_mis = pd.DataFrame(mis_rows) if mis_rows else pd.DataFrame(columns=[
        "sekcja","pozycja_id","kryterium","confidence","numer_pop","data_pop","netto_pop",
        "numer_pdf","data_pdf","netto_pdf","por_numer","por_data","por_netto","pdf_sciezka"
    ])

    with pd.ExcelWriter(out_path, engine="openpyxl") as xl:
        df_m.to_excel(xl, sheet_name="Metryki", index=False)
        df_u.to_excel(xl, sheet_name="Uwagi", index=False)
        df_mis.to_excel(xl, sheet_name="Niezgodnosci", index=False)
        if args.rename_map and Path(args.rename_map).exists():
            pd.read_csv(args.rename_map).to_excel(xl, sheet_name="RenameMap", index=False)

    print(f"OK -> {out_path}")

if __name__ == "__main__":
    main()
