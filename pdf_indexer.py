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
    segs=[]
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
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    return None

def norm_amount(s):
    if not s: return None
    s = str(s).replace("\xa0","").replace(" ","").replace(",",".")
    m = re.findall(r"[-+]?\d+(?:\.\d+)?", s)
    return float(m[-1]) if m else None

def _find_inv_near_header(text:str)->str|None:
    """
    Szukamy numeru tuż po nagłówku 'FAKTURA / INVOICE'.
    Wymuszamy obecność cyfry lub '/' żeby nie złapać samego słowa INVOICE.
    """
    header = re.search(r"(?:FAKTURA\s*(?:/|–|-)\s*INVOICE|FAKTURA|INVOICE)", text, re.I)
    if not header:
        return None
    tail = text[header.end(): header.end()+160]  # krótki wycinek za nagłówkiem
    m = re.search(r"\b([A-Z0-9][A-Z0-9_\-/]*[0-9/][A-Z0-9_\-/]*)\b", tail)  # musi mieć cyfrę lub '/'
    if m:
        return norm_number(m.group(1))
    return None

def _fallback_inv_anywhere(text:str)->str|None:
    # preferuj wzorce ze slashem (np. FV/001/12/2024)
    cands = re.findall(r"\b([A-Z0-9][A-Z0-9_\-/]*\/[A-Z0-9_\-/]+)\b", text)
    if cands:
        # wybierz taki z największą liczbą '/'
        cands.sort(key=lambda x: x.count('/'), reverse=True)
        return norm_number(cands[0])
    # w ostateczności: alfanum ze znakami -_/ ale z cyfrą, żeby nie wziąć INVOICE
    m = re.search(r"\b([A-Z0-9][A-Z0-9_\-/]*[0-9][A-Z0-9_\-/]*)\b", text)
    if m:
        return norm_number(m.group(1))
    return None

def parse_pdf(path):
    txt=[]
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            t = p.extract_text() or ""
            txt.append(_collapse(t))
    text = "\n".join(txt)

    # numer faktury
    inv = _find_inv_near_header(text) or _fallback_inv_anywhere(text)

    # data
    date = norm_date_iso(text)

    # kwota netto (etykiety)
    net=None
    for lab in [r"Suma\s*netto", r"Kwota\s*netto", r"Net(?:\s*amount)?", r"Netto"]:
        m = re.search(fr"{lab}\s*[:\-]?\s*([0-9\s\.,]+)", text, re.I)
        if m:
            net = norm_amount(m.group(1))
            break
    if net is None:
        m = re.findall(r"[-+]?\d{1,3}(?:[\s.,]\d{3})*(?:[.,]\d{2})", text)
        if m: net = norm_amount(m[0])

    # waluta (prosta heurystyka)
    curr=None
    if re.search(r"\bPLN\b|zł", text, re.I): curr="PLN"
    elif re.search(r"\bEUR\b|€", text, re.I): curr="EUR"
    elif re.search(r"\bUSD\b|\$", text, re.I): curr="USD"

    # sprzedawca (heurystyka)
    seller=None
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
