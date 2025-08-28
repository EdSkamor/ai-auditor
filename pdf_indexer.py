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
            txt.append(t)
    body = _collapse("\n".join(txt))

    # numer (format demo: "FAKTURA / INVOICE XYZ")
    num = None
    m = re.search(r"FAKTURA\s*/\s*INVOICE\s+([A-Za-z0-9/_\-]+)", body, re.I)
    if m:
        num = m.group(1)

    # data (format demo: "Data wystawienia: ...")
    dat = None
    m = re.search(r"Data\s+wystawienia:\s*([0-9./-]{8,10})", body, re.I)
    if m:
        dat = m.group(1)

    # netto (format demo: "Suma netto: 1000,00 PLN")
    net = None
    m = re.search(r"Suma\s+netto:\s*([0-9\s.,]+)", body, re.I)
    if m:
        net = m.group(1)

    # waluta (PLN/EUR/USD lub symbol)
    curr = None
    if re.search(r"\bPLN\b", body): curr = "PLN"
    elif re.search(r"\bEUR\b|€", body): curr = "EUR"
    elif re.search(r"\bUSD\b|\$", body): curr = "USD"

    return {
        "source_path": path,
        "source_filename": os.path.basename(path),
        "invoice_id": norm_number(num),
        "issue_date": norm_date_iso(dat),
        "total_net": norm_amount(net),
        "currency": curr,
    }

def scan(root):
    for dirpath,_,files in os.walk(root):
        for f in files:
            if f.lower().endswith(".pdf"):
                yield os.path.join(dirpath,f)

def main():
    if len(sys.argv)<3:
        print("Użycie: python pdf_indexer.py <pdf_root> <out_csv>")
        sys.exit(2)
    root, out_csv = sys.argv[1], sys.argv[2]
    rows=[]
    for p in scan(root):
        try:
            rows.append(parse_pdf(p))
        except Exception as e:
            rows.append({"source_path":p,"source_filename":os.path.basename(p),"error":str(e)})
    with open(out_csv,"w",newline="",encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["source_path","source_filename","invoice_id","issue_date","total_net","currency","error"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"CSV -> {out_csv}  (rekordów: {len(rows)})")

if __name__=="__main__":
    main()
