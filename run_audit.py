from __future__ import annotations
import argparse, os, sys, json, subprocess, datetime as dt, shutil, pathlib

def sh(cmd:list[str]):
    print("$", " ".join(cmd))
    r = subprocess.run(cmd, text=True)
    if r.returncode != 0:
        sys.exit(r.returncode)

def main():
    ap = argparse.ArgumentParser(description="Asystent Audytora – orkiestracja (index -> match -> eksport)")
    ap.add_argument("--pdf-root", required=True, help="Katalog z PDF-ami (po rozpakowaniu)")
    ap.add_argument("--pop", required=True, help="Plik populacji XLSX")
    ap.add_argument("--overrides", default=None, help="CSV z ręcznymi przypisaniami (pozycja_id,sciezka_pdf)")
    ap.add_argument("--amount-tol", type=float, default=0.01, help="Tolerancja porównania netto")
    ap.add_argument("--outdir", default=None, help="Folder na wyniki; default runs/YYYYMMDD_HHMM")
    args = ap.parse_args()

    ts = dt.datetime.now().strftime("%Y%m%d_%H%M")
    outdir = args.outdir or f"runs/{ts}"
    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)

    index_csv = os.path.join(outdir, "All_invoices.csv")

    # 1) Indeks PDF (szybko, bez LLM)
    sh([sys.executable, "pdf_indexer.py", args.pdf_root, index_csv])

    # 2) Dopasowanie populacji
    matcher_cmd = [
        sys.executable, "pop_matcher.py",
        "--pop", args.pop,
        "--pdf-root", args.pdf_root,
        "--index-csv", index_csv,
        "--amount-tol", str(args.amount_tol),
    ]
    if args.overrides:
        matcher_cmd += ["--overrides", args.overrides]
    sh(matcher_cmd)

    # 3) Raport końcowy XLSX
    sh([sys.executable, "export_final_xlsx.py",
        "--summary", "verdicts_summary.json",
        "--verdicts", "verdicts.jsonl",
        "--out-xlsx", os.path.join(outdir, "Audyt_koncowy.xlsx")])

    # 4) Zbierz najważniejsze pliki do outdir (jeśli powstały w cwd)
    for f in ["verdicts.jsonl","verdicts_summary.json","verdicts_top50_mismatches.csv","populacja_enriched.xlsx"]:
        if os.path.exists(f):
            shutil.copy2(f, os.path.join(outdir, f))

    print(f"\nOK -> wyniki w {outdir}")
    for f in ["All_invoices.csv","Audyt_koncowy.xlsx","verdicts_summary.json","verdicts.jsonl","populacja_enriched.xlsx"]:
        p = os.path.join(outdir, f)
        if os.path.exists(p):
            print("  -", p)
    print("Gotowe.")
if __name__ == "__main__":
    main()
