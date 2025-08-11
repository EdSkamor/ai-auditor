from __future__ import annotations
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
import re

def _first_present(cands: List[str], cols: List[str]) -> Optional[str]:
    for c in cands:
        if c in cols:
            return c
    return None

def _num(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.replace(r"[^\d,.\-]", "", regex=True)
    # usuń nadmiarowe separatory tysięcy (prosto)
    s = s.str.replace(r"\.(?=.*\.)", "", regex=True)
    s = s.str.replace(",", ".")
    return pd.to_numeric(s, errors="coerce")

def analyze_table(df: pd.DataFrame) -> Dict[str, Any]:
    cols = [c for c in df.columns]
    date_col = _first_present([c for c in cols if c.startswith("data")], cols)
    amt_cands = [
        "wartosc_netto_dokumentu","wartosc_brutto_dokumentu",
        "kwota_netto","kwota_brutto","kwota","wartosc_netto","wartosc_brutto"
    ]
    amt_col = _first_present([c for c in amt_cands if c in cols], cols)
    cnt_cands = ["kontrahent","nabywca","dostawca","klient","sprzedawca","odbiorca"]
    cnt_col = _first_present([c for c in cnt_cands if c in cols], cols)

    result: Dict[str, Any] = {"date_col": date_col, "amount_col": amt_col, "counterparty_col": cnt_col}

    if amt_col is not None:
        amounts = _num(df[amt_col])
        result["amount_sum"] = float(np.nansum(amounts))
        result["amount_mean"] = float(np.nanmean(amounts))
    if date_col is not None and amt_col is not None:
        tmp = df[[date_col, amt_col]].copy()
        tmp[amt_col] = _num(tmp[amt_col])
        tmp = tmp.dropna()
        if not tmp.empty:
            s = tmp.set_index(date_col)[amt_col].resample("MS").sum().sort_index()
            result["monthly"] = [[d.strftime("%Y-%m"), float(v)] for d, v in s.items()]
            if len(s) >= 2:
                mom_abs = float(s.iloc[-1] - s.iloc[-2])
                mom_pct = float((s.iloc[-1] - s.iloc[-2]) / (s.iloc[-2] + 1e-9) * 100.0)
                result["mom_abs"] = mom_abs
                result["mom_pct"] = mom_pct
    if cnt_col is not None and amt_col is not None:
        g = df.copy()
        g[amt_col] = _num(g[amt_col])
        top = g.groupby(cnt_col, dropna=False)[amt_col].sum().sort_values(ascending=False).head(10)
        result["top_counterparties"] = [[str(k), float(v)] for k, v in top.items()]

    return result
