# == PYTHONPATH_INJECT ==
import sys
from pathlib import Path as _P
_here = _P(__file__).resolve()
_repo = None
for p in _here.parents:
    if (p / 'app').is_dir():
        _repo = p; break
if _repo and str(_repo) not in sys.path:
    sys.path.insert(0, str(_repo))
# == /PYTHONPATH_INJECT ==

import streamlit as st

st.set_page_config(page_title="AI-Audytor – Home", layout="wide")
st.title("🏠 AI-Audytor – Strona główna")

st.subheader("Nawigacja")
st.page_link("pages/00_Chat_Audytor.py", label="💬 Chat – Audytor")
st.page_link("pages/01_Walidacja.py", label="🧾 Walidacja")
st.page_link("pages/02_Przeglad.py", label="🧐 Przegląd")
st.page_link("pages/03_Instrukcja.py", label="📘 Instrukcja")
