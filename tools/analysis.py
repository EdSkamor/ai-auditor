from __future__ import annotations
from typing import Dict, Any, Optional, List
import pandas as pd

def _first(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    return None

def analyze_table(df: pd.DataFrame) -> Dict[str, Any]:
    out: Dict[str, Any] = {"metrics": {}, "output_md": ""}

    date_col = _first(df, [c for c in df.columns if "data" in c])
    amt_col  = _first(df, ["kwota_brutto","kwota_netto","kwota_vat","kwota"])
    ctr_col  = _first(df, ["kontrahent","klient","nabywca","dostawca"])
    inv_col  = _first(df, ["nr_faktury","faktura","numer_faktury"])

    out["metrics"]["rows"] = int(len(df))
    out["metrics"]["columns"] = list(df.columns)

    # daty
    if date_col and pd.api.types.is_datetime64_any_dtype(df[date_col]):
        out["metrics"]["date_min"] = str(df[date_col].min().date())
        out["metrics"]["date_max"] = str(df[date_col].max().date())
        s = df[[date_col]].dropna().set_index(date_col).sort_index()
        out["metrics"]["rows_by_month"] = {str(k.date()): int(v) for k,v in s.resample("MS").size().items()}

    # kwoty
    if amt_col:
        total = pd.to_numeric(df[amt_col], errors="coerce").sum()
        out["metrics"]["amount_total"] = float(total)
        if date_col and pd.api.types.is_datetime64_any_dtype(df[date_col]):
            s = df[[date_col, amt_col]].dropna().set_index(date_col).sort_index()
            m = s[amt_col].resample("MS").sum()
            out["metrics"]["amount_by_month"] = {str(k.date()): float(v) for k,v in m.items()}
            if len(m) >= 2:
                last, prev = m.iloc[-1], m.iloc[-2]
                out["metrics"]["mom_change_pct"] = (float((last-prev)/prev*100.0) if prev != 0 else None)

    # top kontrahenci
    if ctr_col and amt_col:
        top = df[[ctr_col, amt_col]].dropna().groupby(ctr_col)[amt_col].sum().sort_values(ascending=False).head(10)
        out["metrics"]["top_counterparties"] = [(str(k), float(v)) for k,v in top.items()]

    # markdown
    lines = []
    lines.append("### Podsumowanie tabeli")
    lines.append(f"- Wierszy: **{out['metrics']['rows']}**")
    if "date_min" in out["metrics"]:
        lines.append(f"- Zakres dat: **{out['metrics']['date_min']} → {out['metrics']['date_max']}**")
    if "amount_total" in out["metrics"]:
        lines.append(f"- Suma kwot: **{out['metrics']['amount_total']:.2f}**")
    if out["metrics"].get("mom_change_pct") is not None:
        lines.append(f"- Zmiana m/m: **{out['metrics']['mom_change_pct']:.1f}%**")
    if "top_counterparties" in out["metrics"]:
        lines.append("\n**Top kontrahenci (wg kwoty):**")
        for k,v in out["metrics"]["top_counterparties"]:
            lines.append(f"- {k}: {v:.2f}")
    out["output_md"] = "\n".join(lines)
    return out
