from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Optional
import re
import chardet
import pandas as pd
from unidecode import unidecode

def _normalize_col(col: str) -> str:
    c = unidecode(str(col)).strip().lower()
    c = re.sub(r"\s+", "_", c)
    c = re.sub(r"[^a-z0-9_]+", "_", c)
    c = re.sub(r"_+", "_", c).strip("_")
    return c

def _canon(col: str) -> str:
    # reguły kanoniczne (po normalizacji)
    if "data" in col: return "data"
    if any(k in col for k in ["kontrahent","nabyw","dostaw","klient"]): return "kontrahent"
    if "fakt" in col and ("nr" in col or "numer" in col): return "nr_faktury"
    if "brutto" in col: return "kwota_brutto"
    if "netto"  in col: return "kwota_netto"
    if col == "vat" or "kwota_vat" in col: return "kwota_vat"
    if col == "kwota": return "kwota_brutto"
    return col

def _find_header_row(raw: pd.DataFrame, scan: int = 10) -> int:
    best_idx, best_score = 0, -1.0
    for i in range(min(scan, len(raw))):
        row = raw.iloc[i]
        nonnull = row.notna().sum()
        uniq = row.dropna().nunique()
        score = float(nonnull) + 0.5*float(uniq)
        if score > best_score:
            best_score, best_idx = score, i
    return best_idx

def _to_number(s: pd.Series) -> pd.Series:
    return pd.to_numeric(
        s.astype(str)
         .str.replace(r"\s", "", regex=True)   # spacje
         .str.replace(".", "", regex=False)    # kropki tys.
         .str.replace(",", ".", regex=False),  # przecinek -> kropka
        errors="coerce"
    )

def read_table(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Nie ma pliku: {p}")

    ext = p.suffix.lower()
    raw: Optional[pd.DataFrame] = None

    if ext in {".csv", ".txt"}:
        with open(p, "rb") as fh:
            head = fh.read(64*1024)
            enc = chardet.detect(head).get("encoding") or "utf-8"
        try:
            raw = pd.read_csv(p, encoding=enc, engine="python", sep=None, on_bad_lines="skip")
        except Exception:
            raw = pd.read_csv(p, encoding=enc, engine="python", sep=";", on_bad_lines="skip")
    elif ext in {".xlsx", ".xls"}:
        raw = pd.read_excel(p, sheet_name=0, engine="openpyxl")
    else:
        raise ValueError(f"Nieobsługiwane rozszerzenie: {ext}")

    hdr = _find_header_row(raw)
    cols = [str(c) for c in raw.iloc[hdr].tolist()]
    df = raw.iloc[hdr+1:].copy()
    df.columns = cols
    df = df.reset_index(drop=True)

    # normalizacja nazw kolumn
    new_cols = []
    for c in df.columns:
        c2 = _normalize_col(c)
        c3 = _canon(c2)
        new_cols.append(c3)
    df.columns = new_cols

    # daty i kwoty
    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], errors="coerce", dayfirst=True, infer_datetime_format=True)
    for c in ("kwota_brutto","kwota_netto","kwota_vat"):
        if c in df.columns:
            df[c] = _to_number(df[c])

    meta = {"path": str(p), "rows": int(len(df)), "columns": list(df.columns)}
    return {"df": df, "meta": meta}
