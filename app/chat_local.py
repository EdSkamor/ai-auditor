import os, io, time, json, pandas as pd, streamlit as st
from pathlib import Path
from llama_cpp import Llama

st.set_page_config(page_title="AI-Audytor — Chat (lokalny GGUF)", layout="wide")
st.title("AI-Audytor — Chat (lokalny GGUF)")

MODEL_PATH = os.environ.get("LLM_GGUF","")
if not MODEL_PATH or not Path(MODEL_PATH).is_file():
    st.error("Nie znaleziono modelu GGUF. Ustaw zmienną LLM_GGUF na pełną ścieżkę do .gguf.")
    st.stop()

with st.sidebar:
    st.subheader("Ustawienia")
    st.caption("Model:")
    st.code(MODEL_PATH, language="bash")
    n_ctx = st.number_input("Kontekst (tok.)", 2048, 8192, value=4096, step=512)
    n_threads = st.number_input("CPU threads", 1, 32, value=int(os.environ.get("OMP_NUM_THREADS","4")))
    n_gpu_layers = st.number_input("GPU layers (0=CPU)", 0, 60, value=int(os.environ.get("N_GPU_LAYERS","0")))
    temp = st.slider("Temperature", 0.0, 1.0, 0.2, 0.05)
    max_new = st.slider("Max tokens na odpowiedź", 128, 2048, 512, 64)
    if st.button("Wyczyść czat"):
        st.session_state.messages = []
        st.session_state.context = ""
        st.experimental_rerun()

# Inicjalizacja modelu 1x (cache w sesji)
if "llm" not in st.session_state:
    st.session_state.llm = Llama(
        model_path=MODEL_PATH, n_ctx=n_ctx, n_threads=int(n_threads),
        n_gpu_layers=int(n_gpu_layers), verbose=False
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

if "context" not in st.session_state:
    st.session_state.context = ""

st.markdown("### Pliki (opcjonalnie)")
files = st.file_uploader("PDF/XLSX (max kilka na próbę)", type=["pdf","xlsx"], accept_multiple_files=True)
summaries = []
if files:
    for f in files:
        name = f.name
        if name.lower().endswith(".xlsx"):
            try:
                xls = pd.ExcelFile(f)
                sheet = xls.sheet_names[0]
                df = xls.parse(sheet)
                info = {"plik": name, "typ": "xlsx", "wierszy": len(df), "kolumny": list(df.columns)}
                # Podsumowanie prostych kolumn finansowych (jeśli są)
                for col in ["netto","vat","brutto","kwota","kwota_netto","kwota_vat","kwota_brutto"]:
                    if col in df.columns:
                        info[f"suma_{col}"] = float(pd.to_numeric(df[col], errors="coerce").fillna(0).sum())
                summaries.append(info)
            except Exception as e:
                summaries.append({"plik": name, "typ":"xlsx", "błąd": str(e)})
        else:
            # bardzo skrótowy tekst z PDF (do kontekstu)
            try:
                import pdfplumber, re
                import io as _io
                with pdfplumber.open(_io.BytesIO(f.read())) as pdf:
                    text = []
                    for i, p in enumerate(pdf.pages[:3], start=1):
                        t = p.extract_text() or ""
                        t = re.sub(r"\s+"," ", t)
                        text.append(f"[p.{i}] {t[:1500]}")
                    summaries.append({"plik": name, "typ":"pdf", "preview":" ".join(text)})
            except Exception as e:
                summaries.append({"plik": name, "typ":"pdf", "błąd": str(e)})
    # zapis do kontekstu systemowego
    st.session_state.context = "Kontekst z plików: " + json.dumps(summaries, ensure_ascii=False)[:4000]

if summaries:
    with st.expander("Zebrany kontekst z plików", expanded=False):
        st.json(summaries, expanded=False)

# Wyświetl historię
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

SYSTEM_PROMPT = (
    "Jesteś polskojęzycznym asystentem-audytorem. Odpowiadaj krótko, rzeczowo, z listami punktów, "
    "cytuj liczby z kontekstu jeśli dostępny. Jeśli czegoś brakuje – poproś o doprecyzowanie.\n"
)

if st.session_state.context:
    SYSTEM_PROMPT += "\n" + st.session_state.context + "\n"

user_msg = st.chat_input("Napisz, co zrobić… (np. 'sprawdź spójność', 'wylistuj duplikaty numerów', 'anomalia kwot')")
if user_msg:
    st.session_state.messages.append({"role":"user","content":user_msg})
    with st.chat_message("user"):
        st.markdown(user_msg)

    # Wywołanie modelu z historią (wieloturowo)
    llm = st.session_state.llm
    chat_messages = [{"role":"system","content": SYSTEM_PROMPT}] + st.session_state.messages

    try:
        # streaming
        stream = llm.create_chat_completion(
            messages=chat_messages, temperature=float(temp), max_tokens=max_new, stream=True
        )
        assistant_text = ""
        with st.chat_message("assistant"):
            placeholder = st.empty()
            for chunk in stream:
                delta = chunk["choices"][0]["delta"]
                token = delta.get("content","")
                if token:
                    assistant_text += token
                    placeholder.markdown(assistant_text)
        st.session_state.messages.append({"role":"assistant","content":assistant_text})
    except Exception as e:
        st.error(f"Błąd podczas generowania: {e}")
