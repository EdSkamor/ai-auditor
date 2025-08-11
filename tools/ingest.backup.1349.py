from __future__ import annotations
from typing import Dict, Any, List
import io, re
import pandas as pd
import chardet
from unidecode import unidecode

def _norm(s: str) -> str:
    s = unidecode(str(s)).strip().lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "col"

def _dedupe(names: List[str]) -> List[str]:
    seen, out = {}, []
    for raw in names:
        n = _norm(raw)
        if n in seen:
            seen[n] += 1
            n = f"{n}__{seen[n]}"
        else:
            seen[n] = 0
        out.append(n)
    return out

def _flatten_columns(cols) -> list[str]:
    if isinstance(cols, pd.MultiIndex):
        flat = []
        for tup in cols.tolist():
            parts = [str(x) for x in tup if x is not None and str(x).lower() != "nan"]
            flat.append("_".join(parts).strip("_"))
        return _dedupe(flat)
    return _dedupe(list(cols))

def _find_header_row(df_head: pd.DataFrame, scan: int = 10) -> int:
    best_i, best = 0, -1.0
    for i in range(min(scan, len(df_head))):
        row = df_head.iloc[i]
        nonnull = row.notna().sum()
        uniq = row.dropna().astype(str).nunique()
        score = float(nonnull) + 0.5 * float(uniq)
        if score > best:
            best, best_i = score, i
    return best_i

def _extract_prompts_from_sniff(sniff: pd.DataFrame, hdr_idx: int) -> List[str]:
    prompts: List[str] = []
    top = sniff.iloc[:max(hdr_idx, 0)].fillna("")
    for _, r in top.iterrows():
        line = " ".join([str(x).strip() for x in r.tolist() if str(x).strip()])
        line = re.sub(r"\s{2,}", " ", line)
        if line:
            prompts.append(line)
    # heurystyka: tylko unikalne, bez powtórzeń
    uniq = []
    for p in prompts:
        if p not in uniq:
            uniq.append(p)
    return uniq

def _read_excel_bytes(data: bytes) -> Dict[str, Any]:
    b = io.BytesIO(data)
    sniff = pd.read_excel(b, header=None, dtype=str, engine="openpyxl")
    hdr = _find_header_row(sniff)
    prompts = _extract_prompts_from_sniff(sniff, hdr)
    b.seek(0)
    df = pd.read_excel(b, header=hdr, dtype=str, engine="openpyxl")
    df.columns = _flatten_columns(df.columns)
    return {"df": df, "prompts": prompts}

def _read_csv_bytes(data: bytes) -> Dict[str, Any]:
    enc = (chardet.detect(data).get("encoding") or "utf-8")
    txt = data.decode(enc, errors="replace")
    sniff = pd.read_csv(io.StringIO(txt), header=None, dtype=str, sep=None, engine="python")
    hdr = _find_header_row(sniff)
    prompts = _extract_prompts_from_sniff(sniff, hdr)
    df = pd.read_csv(io.StringIO(txt), header=hdr, dtype=str, sep=None, engine="python")
    df.columns = _flatten_columns(df.columns)
    return {"df": df, "prompts": prompts}

def read_table(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    name = (filename or "").lower()
    if name.endswith((".xlsx", ".xls")):
        out = _read_excel_bytes(file_bytes)
    elif name.endswith((".csv", ".tsv", ".txt")):
        out = _read_csv_bytes(file_bytes)
    else:
        raise ValueError(f"Nieobsługiwany format pliku: {filename}")

    df = out["df"]
    # parsowanie daty (jeśli jest kolumna 'data*')
    date_cols = [c for c in df.columns if c.startswith("data")]
    if date_cols:
        c = date_cols[0]
        df[c] = pd.to_datetime(df[c], errors="coerce", dayfirst=True)

    return {
        "df": df,
        "columns": list(df.columns),
        "shape": list(df.shape),
        "prompts": out.get("prompts", []),
    }
