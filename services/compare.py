import os, re, json
from datetime import datetime
from dateutil import parser as dparser
from difflib import SequenceMatcher

# ----------------- formatowanie i parsowanie -----------------
def parse_date(s):
    if s is None or str(s).strip()=="":
        return None
    try:
        return dparser.parse(str(s), dayfirst=True, fuzzy=True).date()
    except Exception:
        m = re.search(r"\b(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})\b", str(s))
        if m:
            y,mn,d = map(int, m.groups())
            try: return datetime(y,mn,d).date()
            except: return None
    return None

def _strip_seps(s:str)->str:
    return re.sub(r"[^A-Z0-9]", "", (s or "")).upper()

def _drop_leading_alpha_prefix(s:str)->str:
    s = (s or "")
    i = 0
    while i < len(s) and not s[i].isdigit():
        i += 1
    return s[i:]

def norm_num(s:str)->str:
    s = (s or "").strip().upper().replace("\\","/")
    s = re.sub(r"\s+", "", s)
    return re.sub(r"[^A-Z0-9/_-]", "", s)

def parse_amount_str(s:str):
    if s is None: return None
    t = str(s).replace("\u00A0","").replace(" ","").upper()
    t = t.replace("PLN","").replace("ZŁ","").replace("ZL","")
    if "." in t and "," in t:
        if t.rfind(",") > t.rfind("."):
            t = t.replace(".","").replace(",",".")
        else:
            t = t.replace(",","")
    else:
        if "," in t: t = t.replace(",",".")
    try:
        return float(t)
    except Exception:
        return None

def norm_amt(x):
    if isinstance(x,(int,float)): return float(x)
    s = str(x)
    m = re.findall(r"(?<!\d)(-?(?:\d{1,3}(?:[ .\u00A0]\d{3})+|\d+)(?:[.,]\d{2})?)(?!\d)", s)
    if m:
        return parse_amount_str(m[0])
    return parse_amount_str(s)

def _flatten(d, prefix=""):
    out={}
    if isinstance(d, dict):
        for k,v in d.items(): out.update(_flatten(v, f"{prefix}{k}."))
    elif isinstance(d, list):
        for i,v in enumerate(d): out.update(_flatten(v, f"{prefix}{i}."))
    else:
        out[prefix[:-1] or "value"] = d
    return out

# ----------------- dopasowania bezpośrednie -----------------
def _build_expected_num_regex(expected:str):
    if not expected: return None
    e = norm_num(expected)
    tokens = re.findall(r"[A-Z]+|\d+", e)
    if not tokens: return None
    sep = r"[\s._/-]*"
    base = r"\b" + sep.join(map(re.escape, tokens)) + r"\b"
    if tokens and tokens[0].isalpha():
        no_pref = r"\b" + sep.join(map(re.escape, tokens[1:])) + r"\b" if len(tokens)>1 else base
        pat = f"(?:{base}|{no_pref})"
    else:
        pat = base
    return re.compile(pat, re.I)

def _expected_amt_present(text:str, expected):
    ae = norm_amt(expected)
    if ae is None: return None
    s = f"{ae:.2f}"
    intp, dec = s.split(".")
    def group3(x):
        g=[];
        while x: g.append(x[-3:]); x=x[:-3]
        return ".".join(reversed(g))
    variants = {
        f"{group3(intp)},{dec}",
        f"{intp},{dec}",
        f"{intp}.{dec}",
        f"{group3(intp)}.{dec}",
        f"{intp[:-3]} {intp[-3:]},{dec}" if len(intp)>3 else f"{intp},{dec}",
        f"{intp}{dec}",
    }
    T = text.replace("\u00A0","")
    for v in variants:
        if v in T:
            return ae
    return None

def _expected_date_present(text:str, expected):
    de = parse_date(expected)
    if not de: return None
    for v in (de.strftime("%d.%m.%Y"), de.strftime("%d-%m-%Y"), de.strftime("%d/%m/%Y"), de.strftime("%Y-%m-%d")):
        if v in text:
            return de
    return None

# ----------------- ekstrakcja kandydatów -----------------
def _cand_num_from_text(text, expected=None):
    T = text.upper()
    cands = set()
    for m in re.finditer(r"(FAKTUR[AA]?|INVOICE)[^\n]{0,50}?(NR|NO|NUMBER|NUMER)\s*[:\-]?\s*([A-Z0-9/_-]{3,})", T):
        cands.add(m.group(3))
    for m in re.finditer(r"(NR|NO|NUMBER|NUMER)\s*[:\-]?\s*([A-Z0-9/_-]{3,})[^\n]{0,50}?(FAKTUR[AA]?|INVOICE)", T):
        cands.add(m.group(2))
    for m in re.finditer(r"\b[A-Z]{0,5}\s?\d{1,4}(?:[/_-]\d{1,4}){1,4}\b", T):
        cands.add(m.group(0).strip())
    for m in re.finditer(r"\b\d{6,12}\b", T):
        cands.add(m.group(0).strip())

    if expected:
        if any(sep in expected for sep in "/-_"):
            cands = {c for c in cands if any(sep in c for sep in "/-_")} or cands
        e_digits = _strip_seps(expected)
        scored=[]
        for c in cands:
            c_digits = _strip_seps(c)
            ratio = SequenceMatcher(a=e_digits, b=c_digits).ratio()
            contains = int(e_digits in c_digits)
            seg_bonus = int(any(sep in c for c in "/-_"))
            scored.append((contains, seg_bonus, ratio, len(c_digits), c))
        scored.sort(reverse=True)
        if scored and scored[0][2] >= (0.90 if any(sep in expected for sep in "/-_") else 0.75):
            return scored[0][4]
    return sorted(cands, key=lambda s: len(_strip_seps(s)), reverse=True)[0] if cands else None

def _amount_candidates(text):
    # vendor tweak: INTER CARS -> prefer NETTO vs BRUTTO if both present

    T = text.upper().replace("\u00A0","")
    out=[]
    # label=3 (najwyższy priorytet): wyraźne "RAZEM/SUMA/TOTAL ... NETTO"
    for pat in [
        r"(RAZEM|SUMA|TOTAL)[^\n]{0,40}?(NETTO|N\.?)\D{0,20}(-?(?:\d{1,3}(?:[ .\u00A0]\d{3})+|\d+)(?:[.,]\d{2})?)",
        r"(NETTO\s*RAZEM|RAZEM\s*NETTO)\D{0,20}(-?(?:\d{1,3}(?:[ .\u00A0]\d{3})+|\d+)(?:[.,]\d{2})?)",
        r"(WARTOŚĆ|WARTOSC)[^\n]{0,40}?NETTO\D{0,20}(-?(?:\d{1,3}(?:[ .\u00A0]\d{3})+|\d+)(?:[.,]\d{2})?)",
    ]:
        for m in re.finditer(pat, T):
            out.append((3, m.groups()[-1]))
    # label=2: "NETTO ... liczba"
    for m in re.finditer(r"NETTO[^\n]{0,40}?(-?(?:\d{1,3}(?:[ .\u00A0]\d{3})+|\d+)(?:[.,]\d{2})?)", T):
        out.append((2, m.group(1)))
    # label=1: jakiekolwiek liczby z groszami
    for m in re.finditer(r"(?<!\d)(-?(?:\d{1,3}(?:[ .\u00A0]\d{3})+|\d+)(?:[.,]\d{2})?)(?!\d)", T):
        out.append((1, m.group(1)))
    # deduplikacja wg wartości parsowanej
    seen=set(); uniq=[]
    for label, raw in out:
        val = parse_amount_str(raw)
        if val is None: continue
        key = (label, f"{val:.2f}")
        if key in seen: continue
        seen.add(key); uniq.append((label, val))
    return uniq

def _all_dates(text):
    pats = [r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b", r"\b\d{4}[./-]\d{1,2}[./-]\d{1,2}\b"]
    out=[]
    for p in pats:
        for m in re.finditer(p, text):
            dt = parse_date(m.group(0))
            if dt: out.append(dt)
    return out

# ----------------- główne: ekstrakcja + porównania -----------------
def extract_candidates(pdf_payload:dict, expected_num=None, expected_amt=None, expected_date=None):
    txt = str(pdf_payload.get("text",""))
    js  = pdf_payload.get("json") or {}
    flat = _flatten(js) if isinstance(js,(dict,list)) else {}

    # numer z JSON jeśli sensowny
    num = None
    for k,v in flat.items():
        lk=k.lower()
        if any(t in lk for t in ("invoice","fakt","nr","number","no")) and str(v).strip():
            num = str(v).strip(); break
    if not num and expected_num:
        pat = _build_expected_num_regex(expected_num)
        if pat:
            m = pat.search(txt)
            if m: num = m.group(0)
    if not num:
        num = _cand_num_from_text(txt, expected=expected_num)

    # kwota
    net = _expected_amt_present(txt, expected_amt)
    if net is None:
        cands = _amount_candidates(txt)
        if expected_amt is not None:
            ae = norm_amt(expected_amt)
            if ae is not None and cands:
                best = None
                for priority in (3,2,1):
                    group = [v for (lab,v) in cands if lab==priority]
                    if group:
                        best = min(group, key=lambda x: abs(x-ae))
                        break
                net = best if best is not None else cands[0][1]
        if net is None:
            net = cands[0][1] if cands else None

    # data
    dt = _expected_date_present(txt, expected_date)
    if dt is None:
        dates = _all_dates(txt)
        if expected_date:
            de = parse_date(expected_date)
            if de and dates:
                dt = min(dates, key=lambda d: abs((d-de).days))
        if dt is None:
            dt = dates[0] if dates else None

    return {"numer": num, "data": dt, "netto": net}

def cmp_number(expected, found):
    e_raw = norm_num(expected)
    f_raw = norm_num(found)
    if not f_raw:
        return False, {"expected": expected, "found": found, "why":"not_found"}
    if e_raw == f_raw or _strip_seps(e_raw) == _strip_seps(f_raw):
        return True, None
    e_tail = _strip_seps(_drop_leading_alpha_prefix(e_raw))
    f_tail = _strip_seps(_drop_leading_alpha_prefix(f_raw))
    if e_tail and e_tail == f_tail:
        return True, None
    return False, {"expected": expected, "found": found, "why": "diff"}

def cmp_date(expected, found, days_tol=None):
    if days_tol is None:
        days_tol = int(os.environ.get("DATE_TOL_DAYS","5"))
    de = parse_date(expected)
    df = found if hasattr(found,"year") else parse_date(found)
    if not df: return False, {"expected": str(de), "found": str(found), "why":"not_found"}
    if not de: return True, None
    if abs((df - de).days) <= days_tol: return True, None
    return False, {"expected": str(de), "found": str(df), "why": f"delta_days={abs((df-de).days)}"}

def cmp_amount(expected, found, rel_tol=None, abs_tol=None):
    if rel_tol is None:
        rel_tol = float(os.environ.get("AMT_REL_TOL","0.01"))
    if abs_tol is None:
        abs_tol = float(os.environ.get("AMT_ABS_TOL","5.0"))
    ae = norm_amt(expected)
    af = found if isinstance(found,(int,float)) else norm_amt(found)
    if af is None: return False, {"expected": ae, "found": found, "why":"not_found"}
    if ae is None: return True, None
    if abs(ae - af) <= max(abs_tol, rel_tol*ae): return True, None
    return False, {"expected": ae, "found": af, "why": f"abs_diff={abs(ae-af):.2f}"}

def compare_row(row, pdf_payload):
    cand = extract_candidates(
        pdf_payload,
        expected_num=row.get("numer_dokumentu"),
        expected_amt=row.get("wartosc_netto_dokumentu"),
        expected_date=row.get("data_dokumentu"),
    )
    mism=[]
    ok,why = cmp_number(row.get("numer_dokumentu"), cand.get("numer"));         (ok or mism.append({"pole":"numer_dokumentu", **why}))
    ok,why = cmp_date(row.get("data_dokumentu"),   cand.get("data"));           (ok or mism.append({"pole":"data_dokumentu", **why}))
    ok,why = cmp_amount(row.get("wartosc_netto_dokumentu"), cand.get("netto")); (ok or mism.append({"pole":"wartosc_netto_dokumentu", **why}))
    return mism, cand
