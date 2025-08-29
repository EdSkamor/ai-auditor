from __future__ import annotations
import os, re, csv, sys
import pdfplumber

def _collapse(s:str)->str:
    return re.sub(r"\s+"," ", s).strip()

def norm_number(t):
    if not t: return None
    t = _collapse(str(t))
    t = t.replace("_","/")
    looks_pos = bool(re.fullmatch(r"\d{1,4}[-/]\d{1,4}[-/]\d{2,4}", t))
    if "-" in t and ("/" in t or looks_pos):
        t = t.replace("-", "/")
    t = re.sub(r"[\/]+","/", t).upper()
    # usuń wiodące zera w segmentach
    segs = []
    for seg in t.split("/"):
        segs.append(str(int(seg)) if seg.isdigit() else seg)
    return "/".join(segs)

def norm_date_iso(s):
    if not s: return None
    s=str(s).strip()
    m = re.search(r"(\d{4})[./-](\d{2})[./-](\d{2})", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.search(r"(\d{2})[./-](\d{2})[./-](\d{4})", s)
    if m:
        # dayfirst
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    return None

def norm_amount(s):
    if not s: return None
    s = str(s).replace("\xa0","").replace(" ","").replace(",",".")
    m = re.findall(r"[-+]?\d+(?:\.\d+)?", s)
    return float(m[-1]) if m else None

def parse_pdf(path):
    txt = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            t = p.extract_text() or ""
            txt.append(_collapse(t))
    text = "\n".join(txt)

    inv = None
    date = None
    net = None
    curr = None
    seller = None

    # numer (szukamy ciągów z / i - oraz literami/cyframi)
    m = re.search(r"([A-Z0-9][A-Z0-9_\-\/]{2,})", text, re.I)
    if m:
        inv = norm_number(m.group(1))

    # data (ISO lub EU)
    date = norm_date_iso(text)

    # netto – spróbuj po etyketach, potem fallback
    for lab in [r"Suma\s*netto", r"Kwota\s*netto", r"Net(?:\s*amount)?", r"Netto"]:
        m = re.search(fr"{lab}\s*[:\-]?\s*([0-9\s\.,]+)", text, re.I)
        if m:
            net = norm_amount(m.group(1))
            break
    if net is None:
        # fallback: weź pierwszą większą kwotę w tekście
        m = re.findall(r"[-+]?\d{1,3}(?:[\s.,]\d{3})*(?:[.,]\d{2})", text)
        if m:
            net = norm_amount(m[0])

    # waluta – symbole i kody
    if re.search(r"\bPLN\b|zł", text, re.I):
        curr = "PLN"
    elif re.search(r"\bEUR\b|€", text, re.I):
        curr = "EUR"
    elif re.search(r"\bUSD\b|\$", text, re.I):
        curr = "USD"

    # sprzedawca – proste heurystyki
    for lab in [r"Sprzedawca", r"Seller", r"Supplier"]:
        m = re.search(fr"{lab}\s*:\s*(.+)", text, re.I)
        if m:
            seller = _collapse(m.group(1))
            break

    return inv, date, net, curr, seller

def main():
    if len(sys.argv)<3:
        print("Użycie: python pdf_indexer.py <pdf_root> <out_csv>", file=sys.stderr)
        sys.exit(2)
    root = sys.argv[1]
    out_csv = sys.argv[2]
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)

    rows=[]
    for dirpath,_,files in os.walk(root):
        for f in files:
            if f.lower().endswith(".pdf"):
                path = os.path.join(dirpath,f)
                try:
                    inv, date, net, curr, seller = parse_pdf(path)
                    rows.append([path, os.path.basename(path), inv, date, net, curr, seller or "", ""])
                except Exception as e:
                    rows.append([path, os.path.basename(path), None, None, None, None, "", f"{type(e).__name__}: {e}"])

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["source_path","source_filename","invoice_id","issue_date","total_net","currency","seller_guess","error"])
        w.writerows(rows)
    print(f"CSV -> {out_csv}  (rekordów: {len(rows)})")

if __name__=="__main__":
    main()
