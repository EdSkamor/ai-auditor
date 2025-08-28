from __future__ import annotations

# == PYTHONPATH_INJECT ==
import sys
from pathlib import Path as _Path
_root = str(_Path(__file__).resolve().parents[1])
if _root not in sys.path:
    sys.path.insert(0, _root)
# == /PYTHONPATH_INJECT ==

import io
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd
import streamlit as st

from app import ui_nav  # przycisk "← Wróć"
from app.decisions import save_decisions, merge_decisions_into_csv, decisions_csv_path

st.set_page_config(page_title="📋 Przegląd – masowe decyzje", layout="wide")
ui_nav.back(target="Home.py")

st.title("📋 Przegląd – masowe decyzje")

# ---------- ŹRÓDŁO DANYCH ----------
st.sidebar.header("Źródło danych")
uploads_dir = Path("data/uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)

existing_csv = sorted([p for p in uploads_dir.glob("*.csv")])
choice = st.sidebar.selectbox(
    "Wybierz istniejący CSV z uploadów",
    ["— (brak/nie wybieram) —"] + [p.name for p in existing_csv],
    index=0,
)

uploaded: Optional[io.BytesIO] = st.sidebar.file_uploader("…lub wgraj nowy CSV", type=["csv"])
df: Optional[pd.DataFrame] = None
src_path: Optional[Path] = None

if uploaded is not None:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = uploaded.name or f"przeglad_{ts}.csv"
    src_path = uploads_dir / fname
    src_path.write_bytes(uploaded.getvalue())
    df = pd.read_csv(io.BytesIO(uploaded.getvalue()))
    st.success(f"Wgrano plik: `{src_path}`")
elif choice != "— (brak/nie wybieram) —":
    src_path = uploads_dir / choice
    try:
        df = pd.read_csv(src_path)
    except Exception as e:
        st.error(f"Nie udało się odczytać `{src_path}`: {e}")

if df is None:
    st.info("Wybierz plik z listy po lewej **albo** wgraj nowy CSV. Minimalnie wymagana kolumna: **`id`**.")
    st.stop()

if "id" not in df.columns:
    st.error("Brakuje kolumny **id**. Upewnij się, że CSV zawiera jednoznaczny identyfikator rekordu.")
    st.stop()

# ---------- Sekcja: Wybór rekordów ----------
st.subheader("Zestaw do przeglądu")

with st.expander("Podgląd danych", expanded=True):
    # dodaj kolumnę checkbox, jeśli nie istnieje
    if "select" not in df.columns:
        df.insert(0, "select", False)

    c1, _ = st.columns(2)
    with c1:
        select_all = st.checkbox("Zaznacz wszystko", value=False, help="Zaznaczy/odznaczy wszystkie wiersze")
    if select_all:
        df["select"] = True

    disabled_cols = [c for c in df.columns if c != "select"]

    edited = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        disabled=disabled_cols,
        column_config={"select": st.column_config.CheckboxColumn("✔", help="Zaznacz do decyzji")},
        key="przeglad_editor",
    )

selected_ids: List[str] = [str(r["id"]) for _, r in edited.iterrows() if bool(r.get("select"))]
st.sidebar.metric("Zaznaczone", len(selected_ids))

# ---------- Sekcja: Akcje masowe ----------
st.subheader("Masowe akcje")
reason = st.text_input("Powód (opcjonalnie, trafi do logu decyzji)", value="")
c_ok, c_rej, _, c_export = st.columns([1, 1, 1, 2])

def _save_and_toast(decision: str) -> None:
    if not selected_ids:
        st.warning("Nie zaznaczono żadnych wierszy.")
        return
    p = save_decisions(
        selected_ids,
        decision=decision,
        reason=reason,
        user=st.session_state.get("user", "local"),
    )
    st.success(f"Zapisano decyzje: **{decision}** dla {len(selected_ids)} pozycji → `{p}`")

with c_ok:
    if st.button("✅ Zatwierdź zaznaczone", type="primary"):
        _save_and_toast("approved")
with c_rej:
    if st.button("⛔ Odrzuć zaznaczone"):
        _save_and_toast("rejected")

# ---------- Sekcja: Eksport po decyzjach ----------
with c_export:
    st.write("")
    if st.button("📤 Eksport CSV (po decyzjach)", help="Łączy dane źródłowe z decyzjami z bieżącego dnia"):
        today = datetime.now().strftime("%Y%m%d")
        out = Path("data/exports") / f"with_decisions_{today}.csv"
        out.parent.mkdir(parents=True, exist_ok=True)
        assert src_path is not None
        merge_decisions_into_csv(src_path, out, for_date=today)
        st.success(f"Wygenerowano eksport: `{out}`")
        st.download_button("⬇️ Pobierz eksport", data=out.read_bytes(), file_name=out.name, mime="text/csv")

# ---------- Podgląd logu decyzji dzisiaj ----------
st.subheader("Log decyzji (dzisiaj)")
dec_path = decisions_csv_path()
if dec_path.exists():
    st.caption(str(dec_path))
    st.dataframe(pd.read_csv(dec_path), use_container_width=True)
else:
    st.info("Brak decyzji z dzisiejszej daty.")
