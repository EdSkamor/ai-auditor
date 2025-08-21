#!/usr/bin/env python3
import argparse, math, re, sys
from pathlib import Path
import pandas as pd
import pdfplumber

def norm_name(s: str) -> str:
    s = str(s or "").strip().replace("\\", "/").split("/")[-1]
    return re.sub(r"\s+", " ", s.replace("\u00A0"," ")).upper()

def to_float(x):
    if x is None: return math.nan
    if isinstance(x,(int,float)): return float(x)
    s = str(x).strip().replace("\u00A0"," ").replace(" ","")
    # usuń kropki tysięcy, przecinek -> kropka
    s = s.replace(".","").replace(",",".")
    try: return float(s)
    except: return math.nan

def find_col(cols, *cands):
    U = [c.upper() for c in cols]
    for wanted in cands:
        for i,c in enumerate(U):
            if c == wanted.upper(): return list(cols)[i]
    # contains (fallback)
    for wanted in cands:
        for i,c in enumerate(U):
            if wanted.upper() in c: return list(cols)[i]
    return None

def extract_best_anywhere(pdf_path: Path, expected: float, max_pct: float):
    if not pdf_path.is_file() or math.isnan(expected):
        return (math.nan, math.inf, None)
    pattern = r"(?<!\d)(-?(?:\d{1,3}(?:[ \.\u00A0]\d{3})+|\d+)(?:[.,]\d{2})?)(?!\d)"
    best_val, best_pct, best_page = math.nan, math.inf, None
    with pdfplumber.open(str(pdf_path)) as pdf:
        for pno, page in enumerate(pdf.pages, start=1):
            try:
                txt = page.extract_text() or ""
            except Exception:
                txt = ""
            for m in re.findall(pattern, txt):
                v = to_float(m)
                if math.isnan(v): continue
                if expected == 0: continue
                pct = abs(v-expected)/abs(expected)*100.0
                if pct < best_pct:
                    best_val, best_pct, best_page = v, pct, pno
    ok = best_pct <= max_pct
    return (best_val, best_pct, best_page, ok)

def main():
    ap = argparse.ArgumentParser(description="Recheck mismatches: find expected amount anywhere in PDF within tolerance.")
    ap.add_argument("xlsx", help="ścieżka do arkusza (resolved XLSX)")
    ap.add_argument("pdf_dir", help="katalog z PDF (Faktury)")
    ap.add_argument("in_csv", help="wynik validate_cli_flex (CSV)")
    ap.add_argument("out_csv", help="ścieżka wyjściowa z kolumnami status_alt/note_alt")
    ap.add_argument("--pct", type=float, default=1.0, help="tolerancja procentowa (domyślnie 1.0)")
    args = ap.parse_args()

    xlsx = Path(args.xlsx); pdf_dir = Path(args.pdf_dir)
    incsv = Path(args.in_csv); outcsv = Path(args.out_csv)

    if not xlsx.is_file(): sys.exit(f"❌ Brak pliku: {xlsx}")
    if not pdf_dir.is_dir(): sys.exit(f"❌ Brak katalogu: {pdf_dir}")
    if not incsv.is_file(): sys.exit(f"❌ Brak pliku: {incsv}")

    df = pd.read_csv(incsv)
    if "plik" not in df.columns:
        # spróbuj kolumn 'zalacznik' itp. i zmapuj na 'plik'
        alt = None
        for c in df.columns:
            if norm_name(c) in ("ZALACZNIK","ZALĄCZNIK","ZALACZNIK/PLIK","PLIK","FILENAME"):
                alt = c; break
        if not alt:
            sys.exit("❌ CSV nie zawiera kolumny 'plik' (ani ekwiwalentu).")
        df = df.rename(columns={alt: "plik"})

    # wczytaj XLSX i znajdź kolumny: nazwa pliku + oczekiwana kwota (preferuj NETTO)
    xdf = pd.read_excel(xlsx)
    file_col = None
    for cand in ("ZALACZNIK","ZALĄCZNIK","PLIK","FILENAME","ZALACZNIK/PLIK"):
        c = find_col(xdf.columns, cand)
        if c: file_col = c; break
    if not file_col:
        sys.exit("❌ W arkuszu nie znaleziono kolumny z nazwą pliku (np. 'zalacznik'/'plik').")

    # preferencja kolumn kwoty (najpierw NETTO), potem inne
    amount_cols_pref = [
        ("NETTO",), ("KWOTA NETTO",), ("WARTOSC NETTO","WARTOŚĆ NETTO"),
        ("RAZEM NETTO",), ("WARTOSC","WARTOŚĆ"), ("RAZEM",), ("DO ZAPLATY","DO ZAPŁATY")
    ]
    amount_col = None
    for group in amount_cols_pref:
        c = find_col(xdf.columns, *group)
        if c: amount_col = c; break
    if not amount_col:
        sys.exit("❌ W arkuszu nie znaleziono kolumny z kwotą (np. 'netto').")

    xdf["_plik_norm"] = xdf[file_col].map(norm_name)
    df["_plik_norm"]  = df["plik"].map(norm_name)

    # zbij do słownika oczekiwań
    exp_map = {row["_plik_norm"]: to_float(row[amount_col]) for _,row in xdf.iterrows()}

    # policz fallback tylko dla mismatch
    out = df.copy()
    if "status" not in out.columns:
        sys.exit("❌ CSV nie posiada kolumny 'status'.")

    out["status_alt"] = out["status"]
    out["note_alt"]   = ""

    best_vals, best_pcts, pages = [], [], []
    flips = 0

    for i,row in out.iterrows():
        if row.get("status") != "mismatch":
            best_vals.append(math.nan); best_pcts.append(math.nan); pages.append(None)
            continue
        plik = row["plik"]; key = norm_name(plik)
        exp  = exp_map.get(key, math.nan)
        pdf_path = pdf_dir / plik
        if not pdf_path.is_file():
            best_vals.append(math.nan); best_pcts.append(math.nan); pages.append(None)
            continue
        best_val, best_pct, page, ok = extract_best_anywhere(pdf_path, exp, args.pct)
        best_vals.append(best_val); best_pcts.append(best_pct); pages.append(page)
        if ok:
            out.at[i, "status_alt"] = f"ok_anywhere{str(args.pct).rstrip('0').rstrip('.')}p"
            out.at[i, "note_alt"] = f"ANYWHERE match p.{page}: {best_val} (Δ {round(best_pct,3)}%% vs exp {exp})"
            flips += 1

    out["best_value"] = best_vals
    out["best_diff_pct"] = best_pcts
    out["best_page"] = pages

    orig_mm = int((out["status"]=="mismatch").sum())
    new_mm  = int((out["status_alt"]=="mismatch").sum())

    out.to_csv(outcsv, index=False)
    print(f"=== ANYWHERE recheck ({args.pct}%%) ===")
    print(f"mismatch (oryg): {orig_mm}")
    print(f"poprawione:      {flips}")
    print(f"mismatch (po):   {new_mm}")
    print(f"📄 Zapisano: {outcsv}")

if __name__ == "__main__":
    main()
