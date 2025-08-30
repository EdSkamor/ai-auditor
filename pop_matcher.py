from __future__ import annotations
import os, re, json, argparse, csv, math, unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from rapidfuzz import fuzz

def parse_amount(x):
    """Zwróć float z tekstu typu '1 234,56', '1,234.56', '1000,00', itp."""
    if x is None:
        return 0.0
    if isinstance(x, (int, float)):
        return float(x)
    t = str(x).strip().replace('\u00A0',' ').replace(' ', '')
    if not t:
        return 0.0
    # Jeżeli ma i kropkę i przecinek, usuń separator tysięcy heurystycznie
    if ',' in t and '.' in t:
        if t.rfind(',') > t.rfind('.'):
            # przecinek później -> przecinek dziesiętny, kropki usuń
            t = t.replace('.', '').replace(',', '.')
        else:
            # kropka później -> kropka dziesiętna, przecinki usuń
            t = t.replace(',', '')
    else:
        # tylko przecinek? zamień na kropkę
        if ',' in t and '.' not in t:
            t = t.replace(',', '.')
        # tylko kropka? zostaw
    try:
        return float(t)
    except Exception:
        return 0.0

# ===================== utils / normalizacja =====================

def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s or "") if not unicodedata.combining(c))

def _collapse_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()

def _norm_txt(s: str) -> str:
    return _collapse_spaces(_strip_accents((s or "").lower()))

def norm_invoice_id(s: str) -> str:
    t = _norm_txt(s)
    t = t.replace("-", "/").replace("_", "/")
    t = re.sub(r"[^a-z0-9/]", "", t)
    return t

def fname_has_id(fname: str, invoice_id: str) -> int:
    f = _norm_txt(Path(fname).stem)
    iid = norm_invoice_id(invoice_id)
    return 1 if iid and (iid in f or iid.replace("/", "_") in f or iid.replace("/", "-") in f) else 0

def seller_sim(a: str, b: str) -> int:
    a, b = _norm_txt(a), _norm_txt(b)
    if not a or not b:
        return 0
    # token_set_ratio dobrze radzi sobie z przestawionymi fragmentami
    return int(fuzz.token_set_ratio(a, b))

# ===================== I/O =====================

def load_index_csv(p: str) -> List[Dict[str, Any]]:
    rows = []
    with open(p, encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append({
                "source_path": row.get("source_path") or row.get("path") or row.get("sciezka"),
                "source_filename": row.get("source_filename") or Path(row.get("source_path","")).name,
                "invoice_id": row.get("invoice_id") or row.get("numer") or row.get("nr"),
                "issue_date": row.get("issue_date") or row.get("data"),
                "total_net": float(row.get("total_net") or row.get("netto") or 0.0),
                "seller_text": row.get("seller_guess") or row.get("seller") or row.get("sprzedawca") or "",
            })
    return rows

def load_pop_xlsx(p: str) -> pd.DataFrame:
    xl = pd.ExcelFile(p)
    # wspieramy: "Koszty" lub pierwszy niepusty arkusz
    sheet = "Koszty" if "Koszty" in xl.sheet_names else xl.sheet_names[0]
    df = xl.parse(sheet)
    # unifikacja nazw kolumn do potrzeb matchera
    # numer / data / netto / kontrahent
    colmap = {}
    for c in df.columns:
        n = _norm_txt(str(c)).replace("_"," ")
        if ("numer" in n) or (n in ("nr","invoice","faktura","invoice id")):
            colmap[c] = "NUMER"
        elif ("data" in n) or (n in ("date","issue date","data wystawienia")):
            colmap[c] = "DATA"
        elif "netto" in n or n in ("total net","kwota netto"):
            colmap[c] = "NETTO"
        elif any(k in n for k in ("kontrahent","sprzedawca","dostawca","seller","vendor","supplier")):
            colmap[c] = "KONTRAHENT"
        elif any(k in n for k in ("pozycja","lp")) or n in ("id",):
            colmap[c] = "POZYCJA_ID"
    df = df.rename(columns=colmap)
    # fallbacki
    for need in ("NUMER","DATA","NETTO"):
        if need not in df.columns:
            df[need] = None
    if "POZYCJA_ID" not in df.columns:
        df["POZYCJA_ID"] = df.index.astype(str)
    if "KONTRAHENT" not in df.columns:
        df["KONTRAHENT"] = ""
    return df

# ===================== dopasowanie =====================

TB_WEIGHT_FNAME = 0.3
TB_MIN_SELLER = 0

def pick_by_tiebreak(cands: List[Dict[str,Any]], invoice_id: str, seller_pop: str) -> tuple[int,str,float]:
    """Zwraca: (idx, suffix, score_float)
       suffix: '+seller' lub '+fname' w zależności który czynnik rozstrzygnął.
    """
    if not cands:
        return -1, "", 0.0
    scores = []
    best = -1; best_score = -1.0; best_suffix = ""
    for i, c in enumerate(cands):
        s_sim = seller_sim(seller_pop, c.get("seller_text",""))
        s_eff = (s_sim/100.0) if s_sim >= TB_MIN_SELLER else 0.0
        f_hit = fname_has_id(c.get("source_filename",""), invoice_id)
        score = (1.0 - TB_WEIGHT_FNAME) * s_eff + TB_WEIGHT_FNAME * f_hit
        suffix = "+seller" if s_eff > (TB_WEIGHT_FNAME * f_hit) else "+fname"
        if score > best_score:
            best_score, best, best_suffix = score, i, suffix
        scores.append((i,score,s_sim,f_hit))
    return best, best_suffix, float(best_score)

def find_best_match(pop_row: Dict[str,Any], index_rows: List[Dict[str,Any]]) -> Dict[str,Any]:
    numer_pop = str(pop_row.get("NUMER") or "")
    data_pop  = str(pop_row.get("DATA") or "")
    try:
        netto_pop = parse_amount(pop_row.get("NETTO") or 0.0)
    except Exception:
        netto_pop = 0.0
    kontr_pop = str(pop_row.get("KONTRAHENT") or "")

    iid_norm = norm_invoice_id(numer_pop)

    # 1) kandydaci po numerze
    cands_num = [r for r in index_rows if norm_invoice_id(r.get("invoice_id","")) == iid_norm and iid_norm]
    if len(cands_num) == 1:
        c = cands_num[0]
        return {
            "status":"znaleziono","kryterium":"numer","confidence":1.0,"rec":c,"suffix":""
        }
    if len(cands_num) > 1:
        idx, suffix, score = pick_by_tiebreak(cands_num, numer_pop, kontr_pop)
        if idx >= 0:
            c = cands_num[idx]
            return {
                "status":"znaleziono","kryterium":"numer"+suffix,"confidence":round(score,3),"rec":c,"suffix":suffix
            }

    # 2) kandydaci po data+netto (łagodne porównanie netto)
    cands_dn = []
    for r in index_rows:
        ok_date = (str(r.get("issue_date") or "") == data_pop and data_pop)
        try:
            ok_net = (abs(float(r.get("total_net") or 0.0) - netto_pop) <= 0.01 + 1e-9)
        except Exception:
            ok_net = False
        if ok_date and ok_net:
            cands_dn.append(r)
    if len(cands_dn) == 1:
        c = cands_dn[0]
        return {
            "status":"znaleziono","kryterium":"data+netto","confidence":1.0,"rec":c,"suffix":""
        }
    if len(cands_dn) > 1:
        idx, suffix, score = pick_by_tiebreak(cands_dn, numer_pop, kontr_pop)
        if idx >= 0:
            c = cands_dn[idx]
            return {
                "status":"znaleziono","kryterium":"data+netto"+suffix,"confidence":round(score,3),"rec":c,"suffix":suffix
            }

    return {"status":"brak","kryterium":"numer","confidence":0.0,"rec":None,"suffix":""}

# ===================== CLI / main =====================

def main():
    global TB_WEIGHT_FNAME, TB_MIN_SELLER
    ap = argparse.ArgumentParser(description="POP matcher (tie-break: fname vs seller)")
    ap.add_argument("--pop", required=True)
    ap.add_argument("--pdf-root", required=True)
    ap.add_argument("--index-csv", required=True)
    ap.add_argument("--amount-tol", type=float, default=0.01)
    ap.add_argument("--out-jsonl", default="verdicts.jsonl")
    ap.add_argument("--summary", default="verdicts_summary.json")
    ap.add_argument("--top-mismatches-csv", default="verdicts_top50_mismatches.csv")
    ap.add_argument("--out-xlsx", default=None)  # nie wymagane tutaj
    # tie-breaker
    ap.add_argument("--tiebreak-weight-fname", type=float, default=0.3,
        help="waga nazwy pliku w TB (0..1)")
    ap.add_argument("--tiebreak-min-seller", type=int, default=0,
        help="minimalny % podobieństwa kontrahenta, żeby liczyć jego wkład")
    args = ap.parse_args()

    TB_WEIGHT_FNAME = max(0.0, min(1.0, float(args.tiebreak_weight_fname)))
    TB_MIN_SELLER = max(0, min(100, int(args.tiebreak_min_seller)))

    df_pop = load_pop_xlsx(args.pop)
    idx_rows = load_index_csv(args.index_csv)

    out_jsonl_path = args.out_jsonl
    fw = open(out_jsonl_path, "w", encoding="utf-8")

    met = {
        "liczba_pozycji_koszty": int(len(df_pop)),
        "liczba_pdf_koszty": int(len(idx_rows)),
        "liczba_pozycji_przychody": 0,
        "liczba_pdf_przychody": 0,
        "braki_pdf": {"Koszty":0, "Przychody":0},
        "niezgodnosci": {"numer":0, "data":0, "netto":0},
    }

    for _, row in df_pop.iterrows():
        r = {k: row.get(k) for k in df_pop.columns}
        res = find_best_match(r, idx_rows)
        rec = res.get("rec")
        if rec:
            por_num = "TAK" if norm_invoice_id(rec["invoice_id"]) == norm_invoice_id(r["NUMER"]) and r["NUMER"] else "NIE"
            por_dat = "TAK" if (str(rec["issue_date"] or "") == str(r["DATA"] or "")) and r["DATA"] else "NIE"
            try:
                por_net = "TAK" if abs(float(rec["total_net"] or 0.0) - parse_amount(r["NETTO"] or 0.0)) <= args.amount_tol + 1e-9 else "NIE"
            except Exception:
                por_net = "NIE"
            zg = "TAK" if (por_num=="TAK" and por_dat=="TAK" and por_net=="TAK") else "NIE"
            if por_num=="NIE": met["niezgodnosci"]["numer"] += 1
            if por_dat=="NIE": met["niezgodnosci"]["data"]  += 1
            if por_net=="NIE": met["niezgodnosci"]["netto"] += 1

            out = {
                "sekcja":"Koszty",
                "pozycja_id": str(r.get("POZYCJA_ID")),
                "numer_pop": r.get("NUMER"),
                "data_pop": r.get("DATA"),
                "netto_pop": parse_amount(r.get("NETTO") or 0.0),
                "dopasowanie":{
                    "status": res["status"],
                    "kryterium": res["kryterium"],
                    "confidence": float(res["confidence"])
                },
                "pdf":{
                    "plik_oryg": rec.get("source_filename"),
                    "plik_po_zmianie": None,
                    "sciezka": rec.get("source_path")
                },
                "wyciagniete":{
                    "numer_pdf": rec.get("invoice_id"),
                    "data_pdf": rec.get("issue_date"),
                    "netto_pdf": rec.get("total_net")
                },
                "porownanie":{"numer":por_num,"data":por_dat,"netto":por_net},
                "zgodnosc": zg,
                "uwagi": None
            }
        else:
            out = {
                "sekcja":"Koszty",
                "pozycja_id": str(r.get("POZYCJA_ID")),
                "numer_pop": r.get("NUMER"),
                "data_pop": r.get("DATA"),
                "netto_pop": parse_amount(r.get("NETTO") or 0.0),
                "dopasowanie":{"status":"brak","kryterium":res["kryterium"],"confidence":0.0},
                "pdf":{"plik_oryg":None,"plik_po_zmianie":None,"sciezka":None},
                "wyciagniete":{"numer_pdf":None,"data_pdf":None,"netto_pdf":None},
                "porownanie":{"numer":"NIE","data":"NIE","netto":"NIE"},
                "zgodnosc":"NIE",
                "uwagi":None
            }

        fw.write(json.dumps(out, ensure_ascii=False) + "\n")

    fw.close()
    print("JSON-lines: {}".format(Path(out_jsonl_path).name))
    # proste podsumowanie
    sumj = {"metryki":met, "uwagi_globalne":[]}
    with open(args.summary, "w", encoding="utf-8") as fsum:
        json.dump(sumj, fsum, ensure_ascii=False, indent=2)
    print("Podsumowanie: {}".format(Path(args.summary).name))

    # pro forma CSV top mismatch (tu: tylko nagłówek + brak realnego rankingu)
    with open(args.top_mismatches_csv, "w", encoding="utf-8", newline="") as fcsv:
        w = csv.writer(fcsv)
        w.writerow(["pozycja_id","kryterium","uwaga"])
    print("CSV (top niezgodności): {}".format(Path(args.top_mismatches_csv).name))

if __name__ == "__main__":
    main()
