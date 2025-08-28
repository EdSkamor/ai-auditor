from __future__ import annotations
import os, re, json, argparse, shutil, unicodedata, math, sys
from typing import Optional, Dict, Any, List, Tuple
import pandas as pd

# (Opcjonalny indeks/ekstrakcja z PDF)
# - jeśli jest All_invoices.csv (z batch_invoices.py), użyjemy go
# - w przeciwnym razie spróbujemy importu extract_invoice.extract_invoice
try:
    from extract_invoice import extract_invoice as _extract_invoice  # może nie być potrzebne, gdy mamy CSV
except Exception:
    _extract_invoice = None


# ---------------------------
# Normalizacja / parsowanie
# ---------------------------

def _strip_accents(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))

def _collapse_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def norm_date_iso(s: Any) -> Optional[str]:
    """Konwersja do ISO YYYY-MM-DD bez ostrzeżeń."""
    if s is None or (isinstance(s, float) and math.isnan(s)):
        return None
    t = str(s).strip()
    if not t:
        return None
    # ISO lub YYYY/MM/DD – parsuj bez dayfirst (eliminuje Warningi)
    if re.fullmatch(r"\d{4}[-/]\d{2}[-/]\d{2}", t):
        d = pd.to_datetime(t.replace("/", "-"), format="%Y-%m-%d", errors="coerce")
    else:
        d = pd.to_datetime(t, dayfirst=True, errors="coerce")
    return d.date().isoformat() if pd.notna(d) else None

def norm_amount(s: Any) -> Optional[float]:
    if s is None or (isinstance(s, float) and math.isnan(s)):
        return None
    t = str(s).replace("\xa0","")
    t = t.replace(" ", "").replace(",", ".")
    m = re.findall(r"[-+]?\d+(?:\.\d+)?", t)
    try:
        return float(m[-1]) if m else None
    except Exception:
        return None

def _strip_leading_zeros(seg: str) -> str:
    if seg.isdigit():
        return str(int(seg))
    return seg

def norm_number(raw: Any) -> Optional[str]:
    """Ujednolica NUMER DOKUMENTU:
    - trim + zbij spacje
    - '_' → '/'
    - '-' → '/' gdy wygląda na układ pozycyjny (NN-NN-NNNN) lub gdy już zawiera '/'
    - usuń wiodące zera w segmentach numerycznych
    - ignoruj wielkość liter
    """
    if raw is None or (isinstance(raw, float) and math.isnan(raw)):
        return None
    t = _collapse_spaces(str(raw))
    if not t:
        return None

    t = _strip_accents(t)
    t = t.replace("_", "/")

    looks_positional = bool(re.fullmatch(r"\d{1,4}[-/]\d{1,4}[-/]\d{2,4}", t))
    if "-" in t and ("/" in t or looks_positional):
        t = t.replace("-", "/")

    # usuń podwójne separatory
    t = re.sub(r"[\/]+", "/", t)

    # usuń wiodące zera w segmentach numerycznych
    segs = [ _strip_leading_zeros(seg) for seg in t.split("/") ]
    t = "/".join(segs)

    # usuń ewentualne podwójne spacje ponownie
    t = _collapse_spaces(t).upper()
    return t or None


# ----------------------------------
# Odczyt populacji (Koszty/Przychody)
# ----------------------------------

POP_REQ_COLS = {
    "DATA DOKUMENTU": ("DATA DOKUMENTU","DATA","DATE","DOC DATE","DATA DOK."),
    "NUMER DOKUMENTU": ("NUMER DOKUMENTU","NUMER","NR","NUMBER","NR DOK."),
    "WARTOŚĆ NETTO DOKUMENTU": ("WARTOŚĆ NETTO DOKUMENTU","NETTO","NET","KWOTA NETTO","WART.NETTO"),
}

SELLER_COL_CANDIDATES = ("SPRZEDAWCA","DOSTAWCA","KONTRAHENT","NAZWA KONTRAHENTA","SELLER","VENDOR")

def _find_col(df: pd.DataFrame, *cands: str) -> Optional[str]:
    cols = {c.lower(): c for c in df.columns}
    for want in cands:
        w = want.lower()
        if w in cols:
            return cols[w]
    # trochę fuzzy po uproszczeniu
    for c in df.columns:
        lc = c.lower()
        for want in cands:
            w = want.lower()
            if w in lc:
                return c
    return None

def _read_sheet(xls_path: str, sheet_name: str) -> Optional[pd.DataFrame]:
    try:
        df = pd.read_excel(xls_path, sheet_name=sheet_name, engine="openpyxl")
        return df
    except Exception:
        return None

def _read_population(xls_path: str) -> Dict[str, pd.DataFrame]:
    out: Dict[str, pd.DataFrame] = {}
    for sec in ("Koszty","Przychody"):
        df = _read_sheet(xls_path, sec)
        if df is None:
            continue
        out[sec] = df
    return out


# ------------------------
# Indeks PDF / ekstrakcja
# ------------------------

def _load_index_csv(csv_path: str) -> Optional[pd.DataFrame]:
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception:
        return None

def _index_from_csv_or_extract(pdf_root: str, index_csv: Optional[str]) -> List[Dict[str, Any]]:
    """Zwraca listę rekordów PDF: {path, filename, number_norm, date_iso, net_amount, seller_norm}"""
    recs: List[Dict[str,Any]] = []

    # 1) Spróbuj gotowego indeksu (All_invoices.csv)
    if index_csv and os.path.isfile(index_csv):
        df = _load_index_csv(index_csv)
        if isinstance(df, pd.DataFrame) and not df.empty:
            for _,row in df.iterrows():
                path = row.get("source_path") or row.get("path") or row.get("file")
                if not path or not os.path.isfile(path):
                    continue
                number = row.get("invoice_id") or row.get("number") or row.get("invoice_number")
                date = row.get("issue_date") or row.get("date")
                net = row.get("total_net") or row.get("net")
                seller = row.get("seller_name") or row.get("seller")
                recs.append({
                    "path": path,
                    "filename": os.path.basename(path),
                    "number_norm": norm_number(number),
                    "date_iso": norm_date_iso(date),
                    "net_amount": norm_amount(net),
                    "seller_norm": _collapse_spaces(str(seller)).upper() if pd.notna(seller) and str(seller).strip() else None
                })
            return recs

    # 2) Jeśli nie było CSV lub było puste – skanuj folder i ew. ekstrakcja
    pdfs = []
    for dirpath,_,files in os.walk(pdf_root or "."):
        for f in files:
            if f.lower().endswith(".pdf"):
                pdfs.append(os.path.join(dirpath,f))

    for p in sorted(pdfs):
        number_norm = date_iso = seller_norm = None
        net_amount = None
        if _extract_invoice is not None:
            try:
                d = _extract_invoice(p)
                number_norm = norm_number(d.get("invoice_id"))
                date_iso = norm_date_iso(d.get("issue_date"))
                net_amount = norm_amount(d.get("total_net"))
                seller_norm = _collapse_spaces(str(d.get("seller_name"))).upper() if d.get("seller_name") else None
            except Exception:
                pass
        recs.append({
            "path": p,
            "filename": os.path.basename(p),
            "number_norm": number_norm,
            "date_iso": date_iso,
            "net_amount": net_amount,
            "seller_norm": seller_norm
        })
    return recs


# ------------------------
# Dopasowanie PDF ↔ pozycja
# ------------------------

def _eq_num(a: Optional[str], b: Optional[str]) -> bool:
    return a is not None and b is not None and a == b

def _eq_date(a: Optional[str], b: Optional[str]) -> bool:
    return a is not None and b is not None and a == b

def _eq_amount(a: Optional[float], b: Optional[float], tol: float = 0.01) -> bool:
    if a is None or b is None:
        return False
    return abs(a - b) <= tol

def _seller_match_score(s_pop: Optional[str], s_pdf: Optional[str]) -> float:
    if not s_pop or not s_pdf:
        return 0.0
    sp = _collapse_spaces(str(s_pop)).upper()
    sd = _collapse_spaces(str(s_pdf)).upper()
    if not sp or not sd:
        return 0.0
    # Prosta heurystyka: pełny substring -> 1.0, słowo-w-słowo 0.8, inaczej 0.0
    if sp in sd or sd in sp:
        return 1.0
    sp_words = set(sp.split())
    sd_words = set(sd.split())
    inter = len(sp_words & sd_words)
    if inter >= max(1, min(len(sp_words), len(sd_words)) - 0):
        return 0.8
    return 0.0

def choose_best(cands: List[Dict[str,Any]]) -> Tuple[str, Optional[Dict[str,Any]]]:
    """Zwraca (status, best_or_none) z rozstrzygnięciem remisu."""
    if not cands:
        return "brak", None
    if len(cands) == 1:
        return "znaleziono", cands[0]
    # remis między najlepszymi?
    cands_sorted = sorted(cands, key=lambda x: (-x["score"], x["filename"]))
    best = cands_sorted[0]
    second = cands_sorted[1]
    if abs(best["score"] - second["score"]) < 1e-9:
        return "wiele", None
    return "znaleziono", best

def match_row(pop: Dict[str,Any], pdf_index: List[Dict[str,Any]]) -> Tuple[Dict[str,Any], List[Dict[str,Any]]]:
    """Zwraca (dopasowanie, kandydaci_z_score)."""
    numer_pop = pop.get("numer_norm")
    data_pop = pop.get("data_iso")
    netto_pop = pop.get("netto")
    seller_pop = pop.get("seller")

    scored: List[Dict[str,Any]] = []

    # 1) kryterium: numer
    if numer_pop:
        for r in pdf_index:
            if _eq_num(numer_pop, r["number_norm"]):
                score = 0.70
                if _eq_date(data_pop, r["date_iso"]): score += 0.20
                if _eq_amount(netto_pop, r["net_amount"]): score += 0.10
                score += 0.05 * _seller_match_score(seller_pop, r["seller_norm"])
                scored.append({**r, "score": round(min(score, 1.0), 4), "kryterium": "numer"})

    # 2) kryterium: data + netto (gdy nic po numerze)
    if not scored and (data_pop and netto_pop is not None):
        for r in pdf_index:
            if _eq_date(data_pop, r["date_iso"]) and _eq_amount(netto_pop, r["net_amount"]):
                score = 0.60
                if _eq_num(numer_pop, r["number_norm"]): score += 0.20
                score += 0.05 * _seller_match_score(seller_pop, r["seller_norm"])
                scored.append({**r, "score": round(min(score, 1.0), 4), "kryterium": "data+netto"})

    # 3) heurystyka sprzedawcy (ostateczność)
    if not scored and seller_pop:
        for r in pdf_index:
            sm = _seller_match_score(seller_pop, r["seller_norm"])
            if sm >= 0.8 and (_eq_date(data_pop, r["date_iso"]) or _eq_amount(netto_pop, r["net_amount"])):
                score = 0.50 + 0.05 * sm
                scored.append({**r, "score": round(min(score, 1.0), 4), "kryterium": "heurystyka"})

    status, best = choose_best(scored)
    conf = round((best["score"] if best else 0.0), 2)
    return {"status": status, "confidence": conf, "kryterium": (best["kryterium"] if best else None), "best": best}, scored


# ------------------------
# Renamer / nazwy docelowe
# ------------------------

def build_target_name(attach_val: Any, num_norm: Optional[str], date_iso: Optional[str], net: Optional[float],
                      client_literal: Optional[str], pattern: Optional[str]) -> str:
    """
    Domyślny wzorzec:
      "zal {ATT} – {NUM} – {DATE} – {NETTO}.pdf"
    Zasady:
      - jeśli w arkuszu jest literalny format klienta z "zal {NR}", trzymaj się prefiksu 1:1
      - {NETTO} zapisujemy z przecinkiem jako separator dziesiętny
    """
    # ustal prefiks "zal XXX" jeżeli klient ma literal
    att_str = None
    if attach_val is not None and str(attach_val).strip():
        att_str = _collapse_spaces(str(attach_val))
    prefix = None
    if client_literal:
        m = re.search(r"(zal\s*[0-9A-Za-z\-_/]+)", client_literal, flags=re.IGNORECASE)
        if m:
            prefix = m.group(1)

    if prefix is None and att_str and re.search(r"^zal\s", att_str, flags=re.IGNORECASE):
        prefix = att_str

    if prefix is None and att_str:
        prefix = f"zal {att_str}"
    if prefix is None:
        prefix = "zal"

    num_txt = (num_norm or "").replace("/", "_")
    date_txt = date_iso or ""
    if net is None:
        netto_txt = ""
    else:
        netto_txt = f"{net:.2f}".replace(".", ",")

    if not pattern:
        pattern = "{PREFIX} – {NUM} – {DATE} – {NETTO}.pdf"

    name = pattern
    name = name.replace("{PREFIX}", prefix)
    name = name.replace("{NUM}", num_txt)
    name = name.replace("{DATE}", date_txt)
    name = name.replace("{NETTO}", netto_txt)
    name = name.replace("{ATT}", att_str or "")
    name = _collapse_spaces(name)
    return name


# ------------------------
# Główna procedura
# ------------------------

def run(pop_path: str, pdf_root: str, out_jsonl: Optional[str], out_xlsx: Optional[str],
        do_rename: bool, apply: bool, move: bool, rename_dir: Optional[str],
        attach_col: Optional[str], pattern: Optional[str], index_csv: Optional[str]) -> None:

    # 1) Indeks PDF
    pdf_index = _index_from_csv_or_extract(pdf_root, index_csv)
    # mapa po ścieżce dla szybkiego lookupu
    path_to_rec = {r["path"]: r for r in pdf_index}

    # 2) Populacje
    pops = _read_population(pop_path)
    if not pops:
        print("Brak arkuszy 'Koszty' / 'Przychody' w populacji.", file=sys.stderr)
        sys.exit(2)

    results: List[Dict[str,Any]] = []
    mismatches: List[Dict[str,Any]] = []
    ambiguities: List[Dict[str,Any]] = []
    missing_pdf: List[Dict[str,Any]] = []

    # Metryki
    metryki = {
        "liczba_pozycji_koszty": 0,
        "liczba_pdf_koszty": 0,
        "liczba_pozycji_przychody": 0,
        "liczba_pdf_przychody": 0,
        "braki_pdf": {"Koszty": 0, "Przychody": 0},
        "niezgodnosci": {"numer": 0, "data": 0, "netto": 0}
    }
    uwagi_globalne: List[str] = []

    # 3) Przetwarzanie per sekcja
    for sekcja, df in pops.items():
        if not isinstance(df, pd.DataFrame) or df.empty:
            uwagi_globalne.append(f"Arkusz '{sekcja}' jest pusty lub nie znaleziony.")
            continue

        col_date = _find_col(df, *POP_REQ_COLS["DATA DOKUMENTU"])
        col_num  = _find_col(df, *POP_REQ_COLS["NUMER DOKUMENTU"])
        col_net  = _find_col(df, *POP_REQ_COLS["WARTOŚĆ NETTO DOKUMENTU"])
        col_att  = attach_col or _find_col(df, "ZAŁĄCZNIK", "ZALACZNIK", "ATTACHMENT")
        col_sell = _find_col(df, *SELLER_COL_CANDIDATES)

        if not (col_date and col_num and col_net):
            uwagi_globalne.append(f"Arkusz '{sekcja}': brak wymaganych kolumn (DATA/NUMER/NETTO).")
            continue

        # dtypes – upewnij się, że kolumna załącznika jest string (eliminuje FutureWarning)
        if col_att:
            df[col_att] = df[col_att].astype("string")

        # liczniki
        if sekcja == "Koszty":
            metryki["liczba_pozycji_koszty"] = len(df)
        else:
            metryki["liczba_pozycji_przychody"] = len(df)

        for ridx, row in df.iterrows():
            numer_pop_raw = row.get(col_num)
            data_pop_raw  = row.get(col_date)
            netto_pop_raw = row.get(col_net)
            seller_val    = row.get(col_sell) if col_sell else None
            attach_val    = row.get(col_att)  if col_att else None

            numer_pop = norm_number(numer_pop_raw)
            data_pop  = norm_date_iso(data_pop_raw)
            netto_pop = norm_amount(netto_pop_raw)

            match_info, _cands = match_row(
                {"numer_norm": numer_pop, "data_iso": data_pop, "netto": netto_pop, "seller": seller_val},
                pdf_index
            )

            # pdf info
            pdf_best = match_info["best"]
            if pdf_best:
                metryki["liczba_pdf_koszty" if sekcja=="Koszty" else "liczba_pdf_przychody"] += 1
                plik_oryg = pdf_best["filename"]
                rel_sciezka = os.path.relpath(pdf_best["path"], start=os.getcwd())
                # porównania
                num_ok = "BRAK_DANYCH"
                dat_ok = "BRAK_DANYCH"
                net_ok = "BRAK_DANYCH"

                if numer_pop and pdf_best["number_norm"]:
                    num_ok = "TAK" if _eq_num(numer_pop, pdf_best["number_norm"]) else "NIE"
                if data_pop and pdf_best["date_iso"]:
                    dat_ok = "TAK" if _eq_date(data_pop, pdf_best["date_iso"]) else "NIE"
                if netto_pop is not None and pdf_best["net_amount"] is not None:
                    net_ok = "TAK" if _eq_amount(netto_pop, pdf_best["net_amount"]) else "NIE"

                if num_ok == "NIE":  metryki["niezgodnosci"]["numer"] += 1
                if dat_ok == "NIE":  metryki["niezgodnosci"]["data"]  += 1
                if net_ok == "NIE":  metryki["niezgodnosci"]["netto"] += 1

                zgodnosc = "TAK" if (num_ok=="TAK" and dat_ok=="TAK" and net_ok=="TAK") else "NIE"

                # renamer (propozycja lub real)
                plik_po_zmianie = None
                if do_rename:
                    client_literal = str(attach_val) if attach_val is not None else None
                    new_name = build_target_name(attach_val, numer_pop, data_pop, netto_pop, client_literal, pattern)
                    plik_po_zmianie = new_name
                    if apply:
                        target_dir = rename_dir or os.path.join(os.getcwd(), "renamed")
                        os.makedirs(target_dir, exist_ok=True)
                        src = pdf_best["path"]
                        tgt = os.path.join(target_dir, new_name)
                        if os.path.abspath(src) != os.path.abspath(tgt):
                            if os.path.exists(tgt):
                                base, ext = os.path.splitext(tgt)
                                k = 1
                                while os.path.exists(f"{base} ({k}){ext}"):
                                    k += 1
                                tgt = f"{base} ({k}){ext}"
                            if move:
                                shutil.move(src, tgt)
                            else:
                                shutil.copy2(src, tgt)

                        # uzupełnij w df kolumnę „ZAŁĄCZNIK”
                        if col_att:
                            df.at[row.name, col_att] = new_name

                rec = {
                    "sekcja": sekcja,
                    "pozycja_id": str(ridx),
                    "numer_pop": numer_pop,
                    "data_pop": data_pop,
                    "netto_pop": netto_pop,
                    "dopasowanie": {
                        "status": match_info["status"],
                        "kryterium": match_info.get("kryterium"),
                        "confidence": match_info["confidence"]
                    },
                    "pdf": {
                        "plik_oryg": plik_oryg,
                        "plik_po_zmianie": plik_po_zmianie,
                        "sciezka": rel_sciezka
                    },
                    "wyciagniete": {
                        "numer_pdf": pdf_best["number_norm"],
                        "data_pdf": pdf_best["date_iso"],
                        "netto_pdf": pdf_best["net_amount"]
                    },
                    "porownanie": {
                        "numer": num_ok,
                        "data":  dat_ok,
                        "netto": net_ok
                    },
                    "zgodnosc": "TAK" if (num_ok=="TAK" and dat_ok=="TAK" and net_ok=="TAK") else "NIE",
                    "uwagi": None
                }
                results.append(rec)
                if rec["dopasowanie"]["status"] == "wiele":
                    ambiguities.append(rec)
                if rec["zgodnosc"] == "NIE":
                    mismatches.append(rec)

            else:
                metryki["braki_pdf"][sekcja] += 1
                rec = {
                    "sekcja": sekcja,
                    "pozycja_id": str(ridx),
                    "numer_pop": numer_pop,
                    "data_pop": data_pop,
                    "netto_pop": netto_pop,
                    "dopasowanie": {
                        "status": "brak",
                        "kryterium": None,
                        "confidence": 0.0
                    },
                    "pdf": {"plik_oryg": None, "plik_po_zmianie": None, "sciezka": None},
                    "wyciagniete": {"numer_pdf": None, "data_pdf": None, "netto_pdf": None},
                    "porownanie": {"numer": "BRAK_DANYCH", "data": "BRAK_DANYCH", "netto": "BRAK_DANYCH"},
                    "zgodnosc": "NIE",
                    "uwagi": "BRAK ZAŁĄCZNIKA"
                }
                results.append(rec)
                missing_pdf.append(rec)

        # Po uzupełnieniu kolumn — zapisz do wzbogaconego XLSX
        if out_xlsx:
            with pd.ExcelWriter(out_xlsx, engine="openpyxl", mode=("w" if sekcja=="Koszty" else "a")) as xl:
                df.to_excel(xl, sheet_name=sekcja, index=False)

    # 4) Raport zbiorczy
    summary = {
        "metryki": metryki,
        "uwagi_globalne": uwagi_globalne
    }

    # 5) Zapis JSON-lines
    if out_jsonl:
        with open(out_jsonl, "w", encoding="utf-8") as f:
            for rec in results:
                f.write(json.dumps(rec, ensure_ascii=False)+"\n")
        print(f"JSON-lines: {out_jsonl}")

    # 6) Zapis metryk
    with open("verdicts_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("Podsumowanie: verdicts_summary.json")

    # 7) CSV: top 50 niezgodności + wieloznaczności
    mism_top = mismatches[:50]
    if mism_top:
        pd.DataFrame(mism_top).to_csv("verdicts_top50_mismatches.csv", index=False)
        print("CSV (top niezgodności): verdicts_top50_mismatches.csv")
    if ambiguities:
        pd.DataFrame(ambiguities).to_csv("verdicts_ambiguities.csv", index=False)
        print("CSV (wiele kandydatów): verdicts_ambiguities.csv")

    # 8) Krótkie echo dla rozmowy z klientem
    print(json.dumps(summary, ensure_ascii=False, indent=2))


# ------------------------
# CLI
# ------------------------

def main():
    ap = argparse.ArgumentParser(description="Asystent Audytora – Testy Wiarygodności (Koszty/Przychody)")
    ap.add_argument("--pop", required=True, help="Ścieżka do populacja.xlsx")
    ap.add_argument("--pdf-root", required=True, help="Folder z PDF")
    ap.add_argument("--out-jsonl", default="verdicts.jsonl", help="Plik wyjściowy JSON-lines")
    ap.add_argument("--out-xlsx", default="populacja_enriched.xlsx", help="Wzbogacony XLSX (uzupełnione ZAŁĄCZNIK itd.)")
    ap.add_argument("--rename", action="store_true", help="Generuj nazwy wg wzorca")
    ap.add_argument("--apply", action="store_true", help="Zastosuj rename (kopia/przeniesienie plików)")
    ap.add_argument("--move", action="store_true", help="W trybie --apply przenoś (zamiast kopiować)")
    ap.add_argument("--rename-dir", default="renamed", help="Katalog docelowy dla zrenamowanych plików (domyślnie ./renamed)")
    ap.add_argument("--attach-col", default=None, help='Nazwa kolumny załącznika (domyślnie autodetekcja "ZAŁĄCZNIK")')
    ap.add_argument("--pattern", default=None, help='Własny wzorzec, np. "{PREFIX} – {NUM} – {DATE} – {NETTO}.pdf"')
    ap.add_argument("--index-csv", default="All_invoices.csv", help="Indeks PDF z batch_invoices.py (przyspiesza dopasowanie)")

    args = ap.parse_args()
    run(pop_path=args.pop,
        pdf_root=args.pdf_root,
        out_jsonl=args.out_jsonl,
        out_xlsx=args.out_xlsx,
        do_rename=args.rename,
        apply=args.apply,
        move=args.move,
        rename_dir=args.rename_dir,
        attach_col=args.attach_col,
        pattern=args.pattern,
        index_csv=args.index_csv)

if __name__ == "__main__":
    main()
