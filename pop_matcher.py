from __future__ import annotations
import os, re, json, argparse, shutil, unicodedata, math, sys, csv
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import pandas as pd
from rapidfuzz import fuzz

# ===================== Normalizacja =====================

def _strip_accents(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))

def _collapse_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def norm_date_iso(s: Any) -> Optional[str]:
    """ISO YYYY-MM-DD bez ostrzeżeń; dayfirst dla nie-ISO."""
    if s is None or (isinstance(s, float) and math.isnan(s)):
        return None
    t = str(s).strip()
    if not t:
        return None
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
    """Ujednolica numer:
    - trim, zbicie spacji
    - '_' → '/', '-' → '/' gdy wygląda na wzór 59-01-2023 lub gdy już występuje '/'
    - segmenty numeryczne bez wiodących zer
    - wielkość liter ignorowana (tu robimy upper)
    """
    if raw is None or (isinstance(raw,float) and math.isnan(raw)): return None
    t = _collapse_spaces(str(raw))
    if not t: return None
    t = t.replace("_","/")
    looks_pos = bool(re.fullmatch(r"\d{1,4}[-/]\d{1,4}[-/]\d{2,4}", t))
    if "-" in t and ("/" in t or looks_pos):
        t = t.replace("-", "/")
    t = re.sub(r"[\/]+","/", t).strip()
    segs = []
    for seg in t.split("/"):
        segs.append(_strip_leading_zeros(seg))
    t = "/".join(segs).upper()
    return t

def safe_equals(a: Any, b: Any) -> bool:
    return (a is None and b is None) or (a == b)

# ===================== Wejścia =====================

def load_population(xlsx_path: Path) -> List[Dict[str, Any]]:
    sheets = []
    try:
        x = pd.ExcelFile(xlsx_path)
        if "Koszty" in x.sheet_names: sheets.append("Koszty")
        if "Przychody" in x.sheet_names: sheets.append("Przychody")
    except Exception as e:
        raise SystemExit(f"Nie mogę odczytać {xlsx_path}: {e}")

    rows = []
    for sh in sheets:
        df = pd.read_excel(xlsx_path, sheet_name=sh, dtype=str)
        for i, r in df.iterrows():
            data = {
                "sekcja": sh,
                "pozycja_id": str(i),
                "numer_pop": norm_number(r.get("NUMER DOKUMENTU")),
                "data_pop": norm_date_iso(r.get("DATA DOKUMENTU")),
                "netto_pop": norm_amount(r.get("WARTOŚĆ NETTO DOKUMENTU")),
                "zalacznik_raw": r.get("ZAŁĄCZNIK"),
            }
            rows.append(data)
    return rows

def ensure_index_csv(pdf_root: Path, index_csv: Optional[Path]) -> Path:
    """Zwróć ścieżkę do All_invoices.csv; zbuduj jeśli brak."""
    if index_csv and index_csv.exists():
        return index_csv
    out = pdf_root.parent / "All_invoices.csv"
    # Użyj naszego pdf_indexer.py
    cmd = [sys.executable, "pdf_indexer.py", os.fspath(pdf_root), os.fspath(out)]
    import subprocess
    p = subprocess.run(cmd, text=True, capture_output=True)
    if p.returncode != 0:
        print(p.stdout); print(p.stderr, file=sys.stderr)
        raise SystemExit("pdf_indexer.py nie powiódł się.")
    return out

def load_index(index_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(index_csv)
    # Uzupełnij pola pomocnicze
    df["norm_num"]  = df["invoice_id"].apply(norm_number)
    df["issue_iso"] = df["issue_date"].apply(norm_date_iso)
    df["net_val"]   = df["total_net"].apply(norm_amount)
    return df

def load_overrides(path: Optional[Path]) -> Dict[str, str]:
    """CSV: pozycja_id, sciezka_pdf"""
    mapping = {}
    if not path: return mapping
    with open(path, "r", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for row in rd:
            pid = str(row.get("pozycja_id") or "").strip()
            fp  = str(row.get("sciezka_pdf") or "").strip()
            if pid and fp:
                mapping[pid] = fp
    return mapping

# ===================== Dopasowanie =====================

def find_by_number(df_idx: pd.DataFrame, num: Optional[str]) -> Optional[pd.Series]:
    if not num: return None
    hits = df_idx[df_idx["norm_num"] == num]
    if hits.empty: return None
    # Jeśli wiele – weź pierwszy, ale oznaczymy confidence < 1 przy wielu kandyd.
    return hits.iloc[0]

def find_by_date_net(df_idx: pd.DataFrame, date_iso: Optional[str], net: Optional[float], tol: float) -> Tuple[Optional[pd.Series], float, int]:
    if not date_iso or net is None:
        return (None, 0.0, 0)
    cand = df_idx[(df_idx["issue_iso"] == date_iso) & (df_idx["net_val"].notna())]
    cand = cand[ (cand["net_val"] - net).abs() <= tol ]
    if cand.empty: return (None, 0.0, 0)
    if len(cand)==1:
        return (cand.iloc[0], 0.6, 1)
    # wiele – wybór heurystyczny (najbliższe netto)
    cand = cand.assign(diff=(cand["net_val"]-net).abs()).sort_values("diff")
    return (cand.iloc[0], 0.55, len(cand))

def resolve_override(pdf_root: Path, hint: str) -> Optional[Path]:
    p = Path(hint)
    if p.exists(): return p
    # spróbuj względnie od pdf_root
    cand = pdf_root / hint
    if cand.exists(): return cand
    # spróbuj po nazwie
    for f in pdf_root.rglob("*.pdf"):
        if f.name == hint:
            return f
    return None

# ===================== Rename =====================

def build_target_name(zal: Any, num: Optional[str], date_iso: Optional[str], net: Optional[float]) -> str:
    nr = str(zal) if zal is not None else "brak"
    nnum = (num or "").replace("/", "_")
    d = date_iso or "0000-00-00"
    if net is None:
        kw = "0,00"
    else:
        kw = f"{net:.2f}".replace(".", ",")
    return f"zal {nr} – {nnum} – {d} – {kw}.pdf"

def unique_copy(src: Path, dst_dir: Path, name: str) -> Path:
    dst_dir.mkdir(parents=True, exist_ok=True)
    base = name
    target = dst_dir / base
    k=1
    while target.exists():
        stem, ext = os.path.splitext(base)
        target = dst_dir / f"{stem} ({k}){ext}"
        k+=1
    shutil.copy2(src, target)
    return target

# ===================== Główny bieg =====================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pop", required=True, help="populacja.xlsx")
    ap.add_argument("--pdf-root", required=True, help="katalog z PDF")
    ap.add_argument("--index-csv", default=None, help="All_invoices.csv (opcjonalnie)")
    ap.add_argument("--overrides", default=None, help="CSV: pozycja_id,sciezka_pdf (względne lub pełne)")
    ap.add_argument("--amount-tol", type=float, default=0.01, help="tolerancja porównania netto (default 0.01)")
    ap.add_argument("--out-jsonl", default="verdicts.jsonl")
    ap.add_argument("--out-xlsx", default="populacja_enriched.xlsx")
    ap.add_argument("--rename", action="store_true", help="proponuj nazwy i wpisuj do kolumny ZAŁĄCZNIK")
    ap.add_argument("--apply", action="store_true", help="wykonaj fizyczne kopiowanie do --rename-dir")
    ap.add_argument("--rename-dir", default="renamed", help="katalog docelowy dla rename (z --apply)")
    ap.add_argument("--attach-col", default="ZAŁĄCZNIK", help="nazwa kolumny w XLSX do uzupełnienia")
    args = ap.parse_args()

    pop_path = Path(args.pop)
    pdf_root = Path(args.pdf_root)
    index_csv = Path(args.index_csv) if args.index_csv else None
    out_jsonl = Path(args.out_jsonl)
    out_xlsx  = Path(args.out_xlsx)
    ren_dir   = Path(args.rename_dir)
    attach_col= args.attach_col

    # 1) wejścia
    pop = load_population(pop_path)
    idx_csv = ensure_index_csv(pdf_root, index_csv)
    idx_df  = load_index(idx_csv)
    overrides = load_overrides(Path(args.overrides) if args.overrides else None)

    # 2) wynikowe struktury
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    enriched_rows = []  # do xlsx
    mismatches = []
    miss_pdf = {"Koszty":0, "Przychody":0}
    mis_num = mis_date = mis_net = 0
    rename_map = []

    # 3) pętla pozycji
    with open(out_jsonl, "w", encoding="utf-8") as fj:
        for row in pop:
            pid = row["pozycja_id"]
            sek = row["sekcja"]
            num = row["numer_pop"]
            dat = row["data_pop"]
            net = row["netto_pop"]
            attach_raw = row["zalacznik_raw"]

            picked = None
            status = "brak"
            kryt = None
            conf = 0.0
            pdf_path = None

            # a) overrides
            if pid in overrides:
                p = resolve_override(pdf_root, overrides[pid])
                if p and p.exists():
                    pdf_path = p
                    # ustal rekord z indeksu po ścieżce
                    recs = idx_df[idx_df["source_path"]==os.fspath(p)]
                    picked = recs.iloc[0] if not recs.empty else None
                    status, kryt, conf = "znaleziono", "override", 1.0

            # b) dopasowanie numeru
            if picked is None:
                hit = find_by_number(idx_df, num)
                if hit is not None:
                    picked = hit
                    status, kryt, conf = "znaleziono", "numer", 1.0
                    # jeżeli w indeksie są duplikaty numeru, obniż confidence
                    ndup = (idx_df["norm_num"] == num).sum()
                    if ndup > 1:
                        conf = 0.8

            # c) dopasowanie data+netto
            if picked is None:
                hit, c, cnt = find_by_date_net(idx_df, dat, net, args.amount_tol)
                if hit is not None:
                    picked = hit
                    status, kryt, conf = "znaleziono", "data+netto", c
                    if cnt>1: conf = 0.6

            # d) ustalenie wartości PDF
            num_pdf = dat_pdf = None
            net_pdf = None
            orig_name = None

            if picked is not None:
                num_pdf = picked["norm_num"]
                dat_pdf = picked["issue_iso"]
                net_pdf = picked["net_val"]
                pdf_path = Path(picked["source_path"])
                orig_name = picked.get("source_filename", None)
            else:
                # brak dopasowania
                miss_pdf[sek] = miss_pdf.get(sek,0) + 1

            # e) porównania
            def yesno(cond, have):
                if not have: return "BRAK_DANYCH"
                return "TAK" if cond else "NIE"

            cmp_num  = yesno(safe_equals(num_pdf, num), num_pdf and num)
            cmp_date = yesno(safe_equals(dat_pdf, dat), dat_pdf and dat)
            cmp_net  = "BRAK_DANYCH"
            if (net is not None) and (net_pdf is not None):
                cmp_net = "TAK" if abs(float(net_pdf) - float(net)) <= args.amount_tol else "NIE"

            zgod = "TAK" if (cmp_num=="TAK" and cmp_date=="TAK" and cmp_net=="TAK") else "NIE"
            if cmp_num=="NIE":  mis_num += 1
            if cmp_date=="NIE": mis_date+= 1
            if cmp_net=="NIE":  mis_net += 1

            # f) rename (propozycja + opcjonalne wykonanie)
            proposed_name = None
            applied_name  = None
            if args.rename and picked is not None:
                proposed_name = build_target_name(attach_raw, num, dat, net)
                if args.apply and pdf_path and pdf_path.exists():
                    dst = unique_copy(pdf_path, ren_dir, proposed_name)
                    applied_name = dst.name
                    rename_map.append({
                        "pozycja_id": pid,
                        "src": os.fspath(pdf_path),
                        "dst": os.fspath(dst)
                    })

            # g) JSONL
            rec = {
              "sekcja": sek,
              "pozycja_id": pid,
              "numer_pop": num,
              "data_pop": dat,
              "netto_pop": net,
              "dopasowanie": {
                "status": status if picked is not None else "brak",
                "kryterium": kryt,
                "confidence": conf
              },
              "pdf": {
                "plik_oryg": orig_name if orig_name else (pdf_path.name if pdf_path else None),
                "plik_po_zmianie": applied_name if applied_name else proposed_name,
                "sciezka": os.fspath(pdf_path) if pdf_path else None
              },
              "wyciagniete": {
                "numer_pdf": num_pdf,
                "data_pdf": dat_pdf,
                "netto_pdf": net_pdf
              },
              "porownanie": {
                "numer": cmp_num,
                "data":  cmp_date,
                "netto": cmp_net
              },
              "zgodnosc": zgod,
              "uwagi": None if picked is not None else "BRAK ZAŁĄCZNIKA"
            }
            fj.write(json.dumps(rec, ensure_ascii=False) + "\n")

            # do XLSX / top-mismatch
            row_x = {
                "SEKCJA": sek,
                "POZYCJA_ID": pid,
                "NUMER_POP": num,
                "DATA_POP": dat,
                "NETTO_POP": net,
                "NUMER_PDF": num_pdf,
                "DATA_PDF": dat_pdf,
                "NETTO_PDF": net_pdf,
                "STATUS": rec["dopasowanie"]["status"],
                "KRYTERIUM": rec["dopasowanie"]["kryterium"],
                "CONFIDENCE": rec["dopasowanie"]["confidence"],
                attach_col: applied_name or proposed_name or None
            }
            enriched_rows.append(row_x)

            if zgod=="NIE":
                mismatches.append({
                    "pozycja_id": pid,
                    "sekcja": sek,
                    "numer_pop": num,
                    "data_pop": dat,
                    "netto_pop": net,
                    "numer_pdf": num_pdf,
                    "data_pdf": dat_pdf,
                    "netto_pdf": net_pdf,
                    "porownanie": rec["porownanie"],
                    "kryterium": kryt,
                    "confidence": conf,
                })

    # 4) zapis XLSX + CSV top50
    df_enr = pd.DataFrame(enriched_rows)
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as xl:
        df_enr.to_excel(xl, sheet_name="Enriched", index=False)
    top_mis = pd.DataFrame(mismatches).head(50)
    top_mis.to_csv("verdicts_top50_mismatches.csv", index=False, encoding="utf-8")

    # 5) summary.json
    # policz liczbę PDF w indeksie per sekcja (tu całościowo: nie rozbijamy po sekcjach w indeksie)
    sek_k = sum(1 for r in pop if r["sekcja"]=="Koszty")
    sek_p = sum(1 for r in pop if r["sekcja"]=="Przychody")
    summary = {
      "metryki": {
        "liczba_pozycji_koszty": sek_k,
        "liczba_pdf_koszty": int(idx_df.shape[0]) if sek_k else 0,
        "liczba_pozycji_przychody": sek_p,
        "liczba_pdf_przychody": int(idx_df.shape[0]) if sek_p else 0,
        "braki_pdf": { "Koszty": miss_pdf.get("Koszty",0), "Przychody": miss_pdf.get("Przychody",0) },
        "niezgodnosci": { "numer": mis_num, "data": mis_date, "netto": mis_net }
      },
      "uwagi_globalne": []
    }
    if sek_p == 0:
        summary["uwagi_globalne"].append("Arkusz 'Przychody' jest pusty lub nie znaleziony.")
    json.dump(summary, open("verdicts_summary.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)

    print("JSON-lines:", out_jsonl.name)
    print("Podsumowanie: verdicts_summary.json")
    print("CSV (top niezgodności): verdicts_top50_mismatches.csv")
    if args.apply:
        print(f"Przeniesienia -> {ren_dir}")

if __name__ == "__main__":
    main()
