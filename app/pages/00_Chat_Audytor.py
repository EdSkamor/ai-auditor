import os, io, re, streamlit as st, pandas as pd
from pathlib import Path
from app.local_llm import get_llm
try:
    import pdfplumber
except Exception:
    pdfplumber = None

st.set_page_config(page_title="💬 Chat – Audytor", layout="wide")

# == [AUDYTOR-DEMO-BLOCK] ==
import os
from pathlib import Path as _Path
import streamlit as st

with st.sidebar:
    st.subheader("🔧 Status modelu")
    _llm_path = os.getenv("LLM_GGUF","")
    if _llm_path and _Path(_llm_path).is_file():
        st.caption(f"Model: {_Path(_llm_path).name}")
    else:
        st.error("Brak `LLM_GGUF` — ustaw w shellu i odśwież.")
    st.divider()
    st.subheader("📄 Dane demo")
    if st.button("Załaduj arkusz demo (audyt_demo.xlsx)"):
        demo = _Path("data/samples/audyt_demo.xlsx")
        if demo.exists():
            st.session_state.setdefault("chat_demo_files", {})
            st.session_state["chat_demo_files"]["xlsx"] = str(demo)
            st.success("Dołączono: data/samples/audyt_demo.xlsx")
            st.toast("Wpisz: „Policz sumaryczny VAT i top-3 kontrahentów wg brutto”")
        else:
            st.warning("Brak pliku data/samples/audyt_demo.xlsx (użyj generatora próbek).")
    st.divider()
    st.subheader("💡 Podpowiedzi")
    st.caption("• Policz sumaryczny VAT i pokaż top-3 kontrahentów wg brutto z krótką interpretacją.")
    st.caption("• Porównaj dane z arkusza z fakturą „441200251 INTER CARS.pdf”.")
    st.caption("• Wygeneruj wykres udziału kontrahentów w brutto (Top 5).")
# == [/AUDYTOR-DEMO-BLOCK] ==


st.title("💬 Chat – Audytor")


from app.ui_nav import back as _back
_back()
# Model info
llm_path = os.getenv("LLM_GGUF","")
if not llm_path or not Path(llm_path).is_file():
    st.error("Brak lokalnego modelu .gguf. Ustaw zmienną `LLM_GGUF` na pełną ścieżkę.")
    st.stop()
st.sidebar.success(f"Model: {llm_path}")

# Persona (system prompt)
persona_path = Path("prompts/audytor_system.txt")
system_prompt = persona_path.read_text(encoding="utf-8") if persona_path.exists() else \
    "Jesteś AI-Audytor – odpowiadasz rzetelnie i z liczbami."

# Init session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role":"system","content":system_prompt}]

# Historia (bez system)
for m in st.session_state["messages"]:
    if m["role"] == "system": continue
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Uploader plików
uploads = st.file_uploader(
    "Dodaj pliki (PDF / XLSX / CSV / TXT) – opcjonalnie",
    type=["pdf","xlsx","csv","txt"], accept_multiple_files=True
)

def summarize_uploads(files):
    """Lekki, lokalny skrót treści do wstrzyknięcia w prompt."""
    chunks = []
    for up in files or []:
        try:
            name = up.name
            lower = name.lower()
            if lower.endswith(".xlsx"):
                xls = pd.read_excel(up, sheet_name=None)
                parts = []
                for sheet, df in xls.items():
                    sums = []
                    for col in ["netto","vat","brutto","kwota","amount","value"]:
                        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                            sums.append(f"{col}={df[col].sum():,.2f}")
                    parts.append(f"[{sheet}] rows={len(df)}; " + ("; ".join(sums) if sums else ""))
                chunks.append(f"XLSX: {name}\n" + "\n".join(parts))
            elif lower.endswith(".csv"):
                df = pd.read_csv(up)
                sums = []
                for col in ["netto","vat","brutto","kwota","amount","value"]:
                    if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                        sums.append(f"{col}={df[col].sum():,.2f}")
                chunks.append(f"CSV: {name}\nrows={len(df)}; " + ("; ".join(sums) if sums else ""))
            elif lower.endswith(".pdf") and pdfplumber:
                with pdfplumber.open(up) as pdf:
                    text = []
                    for p in pdf.pages[:3]:
                        t = p.extract_text() or ""
                        text.append(t)
                txt = ("\n".join(text)).strip()[:4000]
                chunks.append(f"PDF: {name}\n{txt}")
            else:
                # TXT
                txt = up.read().decode("utf-8","ignore")[:2000]
                chunks.append(f"FILE: {name}\n{txt}")
        except Exception as e:
            chunks.append(f"[BŁĄD przy {getattr(up,'name','?')}: {e}]")
    return chunks

context_chunks = summarize_uploads(uploads)
if context_chunks:
    st.info("Dodano kontekst z plików – zostanie uwzględniony w odpowiedzi.")

# Wejście użytkownika
user_input = st.chat_input("Zadaj pytanie…")
if user_input:
    # pokaż wiadomość usera
    with st.chat_message("user"):
        st.markdown(user_input)

    # zbuduj wiadomość z kontekstem
    context_block = ("\n\n### Kontekst z plików:\n" + "\n\n".join(context_chunks)) if context_chunks else ""
    user_msg = user_input + context_block + "\n\nPodaj jasno kroki obliczeń i liczby z jednostkami."
    st.session_state["messages"].append({"role":"user","content":user_msg})

    # LLM
    llm = get_llm()
    try:
        out = llm.create_chat_completion(
            messages=[m for m in st.session_state["messages"] if m["role"] in ("system","user","assistant")],
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "768")),
            stream=False,
        )
        reply = out["choices"][0]["message"]["content"]
    except Exception as e:
        reply = f"⚠️ Błąd inferencji: {e}"

    st.session_state["messages"].append({"role":"assistant","content":reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

col1, col2 = st.columns(2)
with col1:
    if st.button("🔁 Reset rozmowy", use_container_width=True):
        st.session_state["messages"] = [{"role":"system","content":system_prompt}]
        st.experimental_rerun()
with col2:
    if st.button("📝 Pokaż prompt systemowy", use_container_width=True):
        st.code(system_prompt)
