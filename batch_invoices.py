import os, sys, argparse, pandas as pd
from rapidfuzz import fuzz
from collections import defaultdict
from extract_invoice import extract_invoice
import fx_utils as fx

def find_pdfs(root:str):
    if not os.path.isdir(root):
        return
    for dirpath,_,files in os.walk(root):
        for f in files:
            if f.lower().endswith(".pdf"):
                yield os.path.join(dirpath,f)

def detect_duplicates(df:pd.DataFrame):
    df = df.copy()
    for col in ["seller_name","invoice_id","issue_date"]:
        if col not in df: df[col] = ""
    df["dup_key"] = (df["seller_name"].fillna("")+"|"+df["invoice_id"].fillna("")+"|"+df["issue_date"].fillna(""))
    exact = df[df.duplicated("dup_key", keep=False)]
    fuzzy_pairs=[]
    rows = df[["seller_name","invoice_id","issue_date"]].fillna("").values.tolist()
    for i in range(len(rows)):
        for j in range(i+1,len(rows)):
            s1=(rows[i][0]+" "+rows[i][1]).strip()
            s2=(rows[j][0]+" "+rows[j][1]).strip()
            if s1 and s2 and rows[i][2]==rows[j][2] and fuzz.token_set_ratio(s1,s2)>=95:
                fuzzy_pairs.append((i,j))
    return exact, fuzzy_pairs

def summarize(df:pd.DataFrame):
    df = df.copy()
    for c in ["total_net","total_vat","total_gross","pln_gross"]:
        if c not in df: df[c] = None
    if "currency" not in df: df["currency"] = None
    if "seller_name" not in df: df["seller_name"] = None
    by_curr = df.groupby("currency", dropna=False)[["total_net","total_vat","total_gross","pln_gross"]]\
                .sum(numeric_only=True).reset_index()
    by_seller = df.groupby("seller_name", dropna=False)[["total_gross","pln_gross"]]\
                  .sum(numeric_only=True).sort_values("pln_gross",ascending=False)\
                  .head(15).reset_index()
    if "issue_date" in df:
        df["_month"] = pd.to_datetime(df["issue_date"], errors="coerce").dt.to_period("M").astype(str)
        by_month_pln = df.groupby("_month", dropna=False)["pln_gross"].sum(numeric_only=True).reset_index().rename(columns={"_month":"month"})
    else:
        by_month_pln = pd.DataFrame(columns=["month","pln_gross"])
    return by_curr, by_seller, by_month_pln

def _norm_curr(x):
    if x is None: return None
    try:
        if pd.isna(x): return None
    except Exception:
        pass
    s = str(x).strip().upper()
    if s in ("", "NONE", "NAN"): return None
    if s in ("$", "USD"): return "USD"
    if s in ("€", "EUR"): return "EUR"
    if s in ("PLN","ZŁ","ZL","PLN."): return "PLN"
    return s

def add_pln(df:pd.DataFrame, fx_source:str, asof:str|None):
    df = df.copy()
    rates_used = {}
    def rate_for(row):
        val = row.get("currency")
        code = _norm_curr(val) or "PLN"
        if code=="PLN":
            return 1.0
        d_raw = asof or row.get("issue_date")
        if not d_raw:
            return None
        try:
            d_iso = pd.to_datetime(d_raw, dayfirst=True, errors="coerce")
            d_str = d_iso.date().isoformat() if pd.notna(d_iso) else str(d_raw)
        except Exception:
            d_str = str(d_raw)
        r = fx.get_rate(code, d_str, source=fx_source)
        if r: rates_used[(code, d_str)] = r
        return r
    df["fx_rate_to_PLN"] = df.apply(rate_for, axis=1)
    df["pln_gross"] = (pd.to_numeric(df["total_gross"], errors="coerce") * df["fx_rate_to_PLN"]).where(df["fx_rate_to_PLN"].notnull())
    return df, rates_used

def sanity_checks(df:pd.DataFrame):
    df = df.copy()
    tol = 0.01
    for c in ["total_net","total_vat","total_gross","vat_rate"]:
        df[c] = pd.to_numeric(df.get(c), errors="coerce")
    mask = df[["total_net","total_vat","total_gross"]].notnull().all(axis=1)
    df["sum_ok"] = None
    df.loc[mask, "sum_ok"] = ((df.loc[mask,"total_net"] + df.loc[mask,"total_vat"] - df.loc[mask,"total_gross"]).abs()
                               <= (df.loc[mask,"total_gross"].abs() * tol))
    for c in ["total_net","total_vat","total_gross"]:
        df[f"neg_{c}"] = df[c] < 0
    return df

def generate_pdf(df_all:pd.DataFrame, by_curr_all:pd.DataFrame, by_seller_all:pd.DataFrame,
                 by_month_all:pd.DataFrame, fx_map:dict, out_pdf:str):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm
    except Exception:
        print("PDF pominięty (brak reportlab).")
        return
    c = canvas.Canvas(out_pdf, pagesize=A4)
    W,H = A4
    x, y = 20*mm, H-20*mm
    def line(t, dy=8*mm, bold=False):
        nonlocal y
        if bold: c.setFont("Helvetica-Bold", 11)
        else: c.setFont("Helvetica", 10)
        c.drawString(x, y, str(t)); y -= dy
        if y < 25*mm:
            c.showPage(); y = H-20*mm

    c.setFont("Helvetica-Bold", 14); line("Executive Summary – faktury", dy=10*mm)
    total_rows = len(df_all)
    err_rows = int(df_all["error"].notnull().sum()) if "error" in df_all else 0
    dup_exact, dup_fuzzy = detect_duplicates(df_all.fillna(""))
    line(f"Liczba dokumentów: {total_rows}")
    line(f"Błędy ekstrakcji: {err_rows}")
    line(f"Duplikaty exact: {len(dup_exact)} | fuzzy: {len(dup_fuzzy)}")

    line("", dy=5*mm); line("Suma wg walut (brutto i PLN):", bold=True)
    for _,r in by_curr_all.fillna(0).iterrows():
        cur = r["currency"] if pd.notna(r["currency"]) else "UNKNOWN"
        line(f" - {cur}: gross={r['total_gross']:.2f} | PLN={r.get('pln_gross',0):.2f}", dy=6*mm)

    line("", dy=5*mm); line("Top sprzedawcy (po PLN):", bold=True)
    for i,(_,r) in enumerate(by_seller_all.fillna(0).head(10).iterrows(), start=1):
        seller = str(r["seller_name"])[:60]
        line(f" {i}. {seller} – PLN {r['pln_gross']:.2f}", dy=6*mm)

    if len(by_month_all):
        line("", dy=5*mm); line("Suma miesięczna (PLN):", bold=True)
        for _,r in by_month_all.fillna(0).iterrows():
            line(f" {r['month']}: PLN {r['pln_gross']:.2f}", dy=6*mm)

    if fx_map:
        line("", dy=5*mm); line("Kursy wykorzystane:", bold=True)
        for (code, d), rate in fx_map.items():
            line(f" {code} @ {d}: {rate}", dy=6*mm)

    c.showPage(); c.save()
    print(f"PDF -> {out_pdf}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="katalog z PDF")
    ap.add_argument("out", nargs="?", default="invoices_report.xlsx")
    ap.add_argument("--date-from", dest="dfrom")
    ap.add_argument("--date-to", dest="dto")
    ap.add_argument("--seller-like")
    ap.add_argument("--fx", choices=["nbp","frankfurter","none"], default="nbp")
    ap.add_argument("--asof", help="data dla kursów (YYYY-MM-DD); domyślnie data faktury")
    ap.add_argument("--no-pdf", action="store_true", help="nie generuj PDF")
    ap.add_argument("--out-csv", action="store_true", help="zapisz All_invoices.csv")
    ap.add_argument("--out-parquet", action="store_true", help="zapisz All_invoices.parquet")
    args = ap.parse_args()

    recs=[]
    any_pdf=False
    for p in find_pdfs(args.root) or []:
        any_pdf=True
        try:
            recs.append(extract_invoice(p))
        except Exception as e:
            recs.append({"source_path":p, "error":str(e)})
    df = pd.DataFrame(recs)

    if not any_pdf:
        with pd.ExcelWriter(args.out, engine="openpyxl") as xl:
            pd.DataFrame([{"info":"Brak plików PDF w katalogu", "folder":args.root}]).to_excel(
                xl, sheet_name="Info", index=False)
        print(f"OK (pusto) -> {args.out}")
        return

    # sanity kolumny + typy
    for col in ["currency","seller_name","invoice_id","issue_date","total_net","total_vat","total_gross","buyer_name","po_number"]:
        if col not in df.columns: df[col] = None
    df["currency"] = df["currency"].apply(_norm_curr)
    for c in ["total_net","total_vat","total_gross","vat_rate"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # filtry
    if args.dfrom or args.dto:
        df["_date"] = pd.to_datetime(df["issue_date"], errors="coerce")
        if args.dfrom:
            df = df[df["_date"] >= pd.to_datetime(args.dfrom)]
        if args.dto:
            df = df[df["_date"] <= pd.to_datetime(args.dto)]
    if args.seller_like:
        s = args.seller_like.lower()
        df = df[df["seller_name"].fillna("").str.lower().str.contains(s)]

    # FX -> PLN
    rates_used = {}
    if args.fx != "none":
        df, rates_used = add_pln(df, fx_source=args.fx, asof=args.asof)
    else:
        df["fx_rate_to_PLN"] = df["currency"].apply(lambda c: 1.0 if (_norm_curr(c)=="PLN") else None)
        df["pln_gross"] = df["total_gross"].where(df["currency"].apply(_norm_curr)=="PLN")

    # sanity checks
    df = sanity_checks(df)

    # grupowania
    by_curr_all, by_seller_all, by_month_all = summarize(df)

    # podział per waluta
    books = defaultdict(pd.DataFrame)
    for curr, sub in df.groupby("currency", dropna=False):
        books[str(curr) if pd.notna(curr) else "UNKNOWN"] = sub

    # zapis XLSX
    with pd.ExcelWriter(args.out, engine="openpyxl") as xl:
        df.to_excel(xl, sheet_name="All_invoices", index=False)
        by_curr_all.to_excel(xl, sheet_name="Summary_ALL", index=False)
        by_seller_all.to_excel(xl, sheet_name="TopSellers_ALL", index=False)
        by_month_all.to_excel(xl, sheet_name="Monthly_PLN", index=False)
        if rates_used:
            pd.DataFrame([{"code":k[0], "date":k[1], "rate_to_PLN":v} for k,v in rates_used.items()])\
              .to_excel(xl, sheet_name="FX", index=False)

        for curr, sub in books.items():
            safe = str(curr) if pd.notna(curr) else "UNKNOWN"
            sub.to_excel(xl, sheet_name=f"Invoices_{safe[:20]}", index=False)
            by_curr, by_seller, by_month = summarize(sub)
            by_curr.to_excel(xl, sheet_name=f"Summary_{safe[:20]}", index=False)
            by_seller.to_excel(xl, sheet_name=f"TopSellers_{safe[:20]}", index=False)

        exact, fuzzy_pairs = detect_duplicates(df.fillna(""))
        exact.to_excel(xl, sheet_name="Duplicates_exact", index=False)
        fuzzy_rows = []
        for i,j in fuzzy_pairs:
            fuzzy_rows.append({
                "i": i, "j": j,
                "path_i": df.iloc[i].get("source_path",""),
                "path_j": df.iloc[j].get("source_path","")
            })
        pd.DataFrame(fuzzy_rows).to_excel(xl, sheet_name="Duplicates_fuzzy", index=False)
        if "error" in df.columns:
            df[df["error"].notnull()].to_excel(xl, sheet_name="Errors", index=False)

    if args.out_csv:
        df.to_csv("All_invoices.csv", index=False)
        print("CSV -> All_invoices.csv")
    if args.out_parquet:
        try:
            df.to_parquet("All_invoices.parquet", index=False)
            print("Parquet -> All_invoices.parquet")
        except Exception as e:
            print("Parquet pominięty:", e)

    print(f"OK -> {args.out}")

    # opcjonalny PDF
    if not args.no_pdf:
        out_pdf = os.path.splitext(args.out)[0] + "_ExecutiveSummary.pdf"
        generate_pdf(df, by_curr_all, by_seller_all, by_month_all, rates_used, out_pdf)

if __name__=="__main__":
    main()
