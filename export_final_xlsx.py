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

    # Metryki
    S = json.load(open(args.summary, "r", encoding="utf-8"))
    df_m = pd.DataFrame([S.get("metryki", {})])

    # Niezgodności
    rows=[]
    with open(args.verdicts, "r", encoding="utf-8") as f:
        for line in f:
            j = json.loads(line)
            if j.get("zgodnosc") == "NIE":
                rows.append({
                  "sekcja": j.get("sekcja"),
                  "pozycja_id": j.get("pozycja_id"),
                  "numer_pop": j.get("numer_pop"),
                  "data_pop": j.get("data_pop"),
                  "netto_pop": j.get("netto_pop"),
                  "numer_pdf": (j.get("wyciagniete") or {}).get("numer_pdf"),
                  "data_pdf": (j.get("wyciagniete") or {}).get("data_pdf"),
                  "netto_pdf": (j.get("wyciagniete") or {}).get("netto_pdf"),
                  "porownanie": (j.get("porownanie") or {}),
                  "dopasowanie": (j.get("dopasowanie") or {}),
                  "plik": (j.get("pdf") or {}).get("sciezka"),
                })
    df_n = pd.DataFrame(rows)

    # Braki
    df_b = df_n[df_n["plik"].isna()].copy()

    # Rename map (opcjonalnie)
    df_r = None
    if args.rename_map and Path(args.rename_map).exists():
        df_r = pd.read_csv(args.rename_map)

    with pd.ExcelWriter(args.out_xlsx, engine="openpyxl") as xl:
        df_m.to_excel(xl, sheet_name="Metryki", index=False)
        (df_n.head(500)).to_excel(xl, sheet_name="Niezgodności_top500", index=False)
        df_b.to_excel(xl, sheet_name="Braki", index=False)
        if df_r is not None:
            df_r.to_excel(xl, sheet_name="RenameMap", index=False)

    print(f"OK -> {args.out_xlsx}")

if __name__ == "__main__":
    main()
