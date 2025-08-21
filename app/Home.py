import os, streamlit as st
from pathlib import Path

st.set_page_config(page_title="AI-Audytor", layout="wide")
st.title("AI-Audytor – start")
st.page_link("pages/03_Instrukcja.py", label="📘 Instrukcja", icon="📘")


llm = os.getenv("LLM_GGUF","")
if not llm or not Path(llm).is_file():
    st.error("Brak lokalnego modelu .gguf. Ustaw zmienną `LLM_GGUF` na pełną ścieżkę.")
    st.code('export LLM_GGUF="/pełna/ścieżka/do/modelu.gguf"', language="bash")
    st.stop()
else:
    st.success(f"Model lokalny OK: {llm}")

st.subheader("Nawigacja")
# Ścieżki MUSZĄ być względne do pliku wejściowego (app/Home.py) → 'pages/...'
st.page_link("pages/00_Chat_Audytor.py", label="💬 Chat – Audytor", icon="💬")
st.page_link("pages/01_Walidacja.py",   label="🧾 Walidacja",      icon="🧾")
