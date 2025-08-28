from __future__ import annotations

# == PYTHONPATH_INJECT ==
import sys
from pathlib import Path as _Path
_root = str(_Path(__file__).resolve().parents[1])
if _root not in sys.path:
    sys.path.insert(0, _root)
# == /PYTHONPATH_INJECT ==

import io
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List

import pandas as pd
import streamlit as st

from app import ui_nav
from app.ui_charts import st_donut_from_series, st_reset_filters_button

st.set_page_config(page_title="🧾 Walidacja – CSV + PDF", layout="wide")
ui_nav.back(target="Home.py")
st.title("🧾 Walidacja – CSV + PDF")

# ----------------- HELPERY -----------------
def _env_paths() -> List[Path]:
    out: List[Path] = []
    for k in ("KOSZTY_FACT", "PRZYCHODY_FACT"):
        p = (os.environ.get(k) or "").strip()
        if p:
            out.append(Path(p))
    return out

def _find_pdf_for_row(row: pd.Series) -> Optional[Path]:
    # Szukamy w typowych kolumnach nazwy pliku PDF
    cand_cols = ["pdf_hint", "nazwa_pliku", "file", "filename", "pdf", "plik"]
    name: Optional[str] = None
    for c in cand_cols:
        if c in row and str(row[c]).strip():
            name = str(row[c]).strip()
            break
    if not name:
        return None
    base = Path(name).name  # tylko nazwa
    # 1) Jeżeli pdf_hint wygląda na pełną ścieżkę i istnieje
    p = Path(name)
    if p.suffix.lower() == ".pdf" and p.exists():
        return p
    # 2) Przeszukaj katalogi ze zmiennych środowiskowych
    for root in _env_paths():
        candidate = root / base
        if candidate.exists():
            return candidate
    return None

def _filter_df(df: pd.DataFrame) -> pd.DataFrame:
    # Filtry: status (multi) + full-text
    f_status: List[str] = st.session_state.get("wal_status_filter", [])
    q: str = st.session_state.get("wal_q", "").strip().lower()

    out = df.copy()
    if "status" in out.columns and f_status:
        out = out[out["status"].astype(str).isin(f_status)]
    if q:
        mask = pd.Series([False] * len(out))
        for c in out.columns:
            mask |= out[c].astype(str).str.lower().str.contains(q, na=False)
        out = out[mask]
    return out

# ----------------- WEJŚCIA -----------------
st.sidebar.header("Źródło danych")
uploads_dir = Path("data/uploads"); uploads_dir.mkdir(parents=True, exist_ok=True)

existing_csv = sorted([p for p in uploads_dir.glob("*.csv")])
choice = st.sidebar.selectbox(
    "Wybierz istniejący CSV",
    ["— (brak/nie wybieram) —"] + [p.name for p in existing_csv],
    index=0,
    key="wal_choice",
)
uploaded = st.sidebar.file_uploader("…lub wgraj nowy CSV", type=["csv"], key="wal_upl")

df: Optional[pd.DataFrame] = None
src_path: Optional[Path] = None

if uploaded is not None:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = uploaded.name or f"walidacja_{ts}.csv"
    src_path = uploads_dir / fname
    src_path.write_bytes(uploaded.getvalue())
    try:
        df = pd.read_csv(io.BytesIO(uploaded.getValue()))
    except AttributeError:
        # niektóre przeglądarki/Streamlit dają file-like bez getValue()
        df = pd.read_csv(io.BytesIO(uploaded.getvalue()))
    st.success(f"Wgrano plik: `{src_path}`")
elif choice != "— (brak/nie wybieram) —":
    src_path = uploads_dir / choice
    try:
        df = pd.read_csv(src_path)
    except Exception as e:
        st.error(f"Nie udało się odczytać `{src_path}`: {e}")

if df is None:
    st.info("Wybierz CSV po lewej **albo** wgraj nowy. Minimalne kolumny: `id`, `status`, oraz kolumna z nazwą PDF (np. `nazwa_pliku`).")
    st.stop()

# ----------------- SANITY KOLUMN -----------------
missing = [c for c in ("id", "status") if c not in df.columns]
if missing:
    st.error(f"Brakuje kolumn: {', '.join(missing)}. Przegląd będzie ograniczony.")
    st.dataframe(df, use_container_width=True)
    st.stop()

# ----------------- PANELE GÓRNE -----------------
c1, c2, c3 = st.columns([2, 2, 3])

with c1:
    st.subheader("Filtry")
    uniq_status = sorted(df["status"].astype(str).dropna().unique().tolist())
    st.multiselect("Status", uniq_status, key="wal_status_filter")
    st.text_input("Szukaj (pełnotekstowo)", key="wal_q", placeholder="np. kontrahent, kwota…")
    st_reset_filters_button(["wal_status_filter", "wal_q"], "🔄 Reset filtrów")

with c2:
    st.subheader("Donut statusów")
    global_view = st.toggle("Pokaż globalnie (ignoruj filtry)", value=False, key="wal_global_donut")
    series = df["status"] if global_view else _filter_df(df)["status"]
    st_donut_from_series(series, title="Statusy" + (" – globalnie" if global_view else " – po filtrze"))

with c3:
    st.subheader("Licznik statusów")
    fdf_counts = _filter_df(df)["status"].astype(str).value_counts(dropna=False)
    ok = int(fdf_counts.get("ok", 0))
    nr = int(fdf_counts.get("needs_review", 0))
    err = int(fdf_counts.get("error", 0))
    ca, cb, cc = st.columns(3)
    ca.metric("OK", ok)
    cb.metric("Needs review", nr)
    cc.metric("Error", err)

st.divider()

# ----------------- TABELA + PDF LINK -----------------
st.subheader("Tabela (po filtrach)")
fdf = _filter_df(df)
if fdf.empty:
    st.warning("Brak rekordów po zastosowaniu filtrów.")
else:
    st.dataframe(fdf, use_container_width=True, hide_index=True)

    if len(fdf) == 1:
        row = fdf.iloc[0]
        pdf_path = _find_pdf_for_row(row)
        if pdf_path and pdf_path.exists():
            st.success("Znaleziono PDF powiązany z rekordem.")
            st.caption(str(pdf_path))
            try:
                st.markdown(f"[📄 Otwórz PDF]({pdf_path.as_uri()})")
            except ValueError:
                st.info("Nie mogę zbudować `file://` dla tej ścieżki — skopiuj ją ręcznie z podpisu powyżej.")
        else:
            st.info("Nie znaleziono PDF. Sprawdź kolumnę z nazwą pliku oraz zmienne `KOSZTY_FACT` / `PRZYCHODY_FACT`.")

# ----------------- EKSPORT CSV (po filtrach) -----------------
st.subheader("Eksport (po filtrach)")
today = datetime.now().strftime("%Y%m%d")
out = Path("data/exports") / f"walidacja_filtered_{today}.csv"
out.parent.mkdir(parents=True, exist_ok=True)
fdf.to_csv(out, index=False, encoding="utf-8")
st.success(f"Wygenerowano eksport z filtrów: `{out}`")
st.download_button("⬇️ Pobierz przefiltrowany CSV", data=out.read_bytes(), file_name=out.name, mime="text/csv")
