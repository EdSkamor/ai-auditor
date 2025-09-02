from __future__ import annotations
import argparse, os, sys, subprocess, datetime as dt, shutil, pathlib

def sh(cmd: list[str]):
    print("$", " ".join(cmd))
    r = subprocess.run(cmd, text=True)
    if r.returncode != 0:
        sys.exit(r.returncode)

def main():
    ap = argparse.ArgumentParser(
        description="Asystent Audytora – index -> match -> export (outdir/runs)"
    )
    ap.add_argument("--pdf-root", required=True, help="Katalog z PDF-ami")
    ap.add_argument("--pop", required=True, help="Plik populacji XLSX")
    ap.add_argument("--overrides", default=None, help="CSV z ręcznymi przypisaniami")
    ap.add_argument("--amount-tol", type=float, default=0.01, help="Tolerancja netto")
    ap.add_argument("--outdir", default=None, help="Folder na wyniki (domyślnie runs/...)")

    # Tie-breaker – przekazujemy dalej do pop_matcher.py
    ap.add_argument("--tiebreak-weight-fname", type=float, default=0.3,
                    help="Waga dopasowania nazwy pliku w tie-breakerze")
    ap.add_argument("--tiebreak-min-seller", type=int, default=0,
                    help="Minimalny % podobieństwa kontrahenta w tie-breakerze")

    args = ap.parse_args()

    outdir = args.outdir or f"runs/{dt.datetime.now():%Y%m%d_%H%M}"
    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)

    # 1) Index
    index_csv = os.path.join(outdir, "All_invoices.csv")
    sh([sys.executable, "pdf_indexer.py", args.pdf_root, index_csv])

    # 2) Match (przekazujemy flagi TB)
    cmd = [
        sys.executable, "pop_matcher.py",
        "--pop", args.pop,
        "--pdf-root", args.pdf_root,
        "--index-csv", index_csv,
        "--amount-tol", str(args.amount_tol),
        "--tiebreak-weight-fname", str(args.tiebreak_weight_fname),
        "--tiebreak-min-seller", str(args.tiebreak_min_seller),
    ]
    if args.overrides:
        cmd += ["--overrides", args.overrides]
    sh(cmd)

    # 3) Przenieś artefakty matchera do outdir
    for f in ("verdicts.jsonl", "verdicts_summary.json",
              "verdicts_top50_mismatches.csv", "populacja_enriched.xlsx"):
        if os.path.isfile(f):
            shutil.move(f, os.path.join(outdir, f))

    # 4) XLSX końcowy (używa plików z outdir)
    sh([
        sys.executable, "export_final_xlsx.py",
        "--summary", os.path.join(outdir, "verdicts_summary.json"),
        "--verdicts", os.path.join(outdir, "verdicts.jsonl"),
        "--out-xlsx", os.path.join(outdir, "Audyt_koncowy.xlsx"),
    ])

    print("\nOK -> wyniki w", outdir)
    for f in ("All_invoices.csv", "Audyt_koncowy.xlsx",
              "verdicts_summary.json", "verdicts.jsonl",
              "populacja_enriched.xlsx"):
        p = os.path.join(outdir, f)
        if os.path.exists(p):
            print("  -", p)
    print("Gotowe.")

if __name__ == "__main__":
    main()
