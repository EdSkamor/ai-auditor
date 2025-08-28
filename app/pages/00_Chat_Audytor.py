# == PYTHONPATH_INJECT ==
import sys, os, re
from pathlib import Path as _P
_here = _P(__file__).resolve()
_repo = None
for p in _here.parents:
    if (p / 'app').is_dir():
        _repo = p
        break
if _repo and str(_repo) not in sys.path:
    sys.path.insert(0, str(_repo))
# == /PYTHONPATH_INJECT ==

import streamlit as st
from app.ui_nav import back as _back
from app.ui_upload import save_uploads

st.set_page_config(page_title="AI-Audytor – Chat", layout="wide")
st.title("💬 Chat – Audytor")
_back()

# ---------- Sidebar: język, model, tryb odpowiedzi ----------
with st.sidebar:
    st.header("⚙️ Ustawienia")

    # język
    lang = st.radio("Język odpowiedzi", ["Polski", "English"], index=0, key="chat_lang")

    # skan .gguf
    roots = [os.path.expanduser("~/models"), os.path.expanduser("~/Downloads"), os.path.join(os.getcwd(),"models")]
    cand = []
    for r in roots:
        if os.path.isdir(r):
            for p in _P(r).rglob("*.gguf"):
                cand.append(str(p.resolve()))
    env_default = os.getenv("LLM_GGUF","")
    if env_default and _P(env_default).is_file() and env_default not in cand:
        cand.insert(0, env_default)

    if not cand:
        st.error("Nie znaleziono żadnych plików .gguf. Dodaj modele do ~/models lub ustaw LLM_GGUF.")
        selected_model = ""
    else:
        labels = [f"{_P(p).name}  —  {p}" for p in cand]
        idx_default = 0
        if "llm_model_path" in st.session_state and st.session_state["llm_model_path"] in cand:
            idx_default = cand.index(st.session_state["llm_model_path"])
        selected_model = st.selectbox("Model (.gguf)", options=range(len(cand)), format_func=lambda i: labels[i], index=idx_default if cand else 0)
        selected_model = cand[selected_model] if cand else ""

    short_mode = st.checkbox("Tylko krótka odpowiedź", value=True, help="Dodaje stop-sekwencje i niski limit tokenów.")

    # ładowanie LLM on change
    from llama_cpp import Llama
    llm_status = st.empty()

    need_reload = (
        ("llm" not in st.session_state) or
        (st.session_state.get("llm_model_path") != selected_model)
    )

    if selected_model and need_reload:
        try:
            n_threads = int(os.getenv("LLAMA_THREADS","4"))
            st.session_state["llm"] = Llama(model_path=selected_model, n_ctx=2048, n_threads=n_threads, verbose=False)
            st.session_state["llm_model_path"] = selected_model
            llm_status.success(f"LLM załadowany: {_P(selected_model).name}")
        except Exception as e:
            st.session_state.pop("llm", None)
            st.session_state["llm_model_path"] = None
            llm_status.error(f"Nie udało się załadować LLM: {e}")
    elif selected_model and ("llm" in st.session_state):
        llm_status.info(f"LLM aktywny: {_P(st.session_state['llm_model_path']).name}")
    else:
        llm_status.warning("Brak wybranego modelu.")

# ---------- Historia ----------
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for role, msg in st.session_state["chat_history"]:
    with st.chat_message(role):
        st.write(msg)

# ---------- Input ----------
prompt = st.chat_input("Napisz wiadomość…")
if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state["chat_history"].append(("user", prompt))

    # brak modelu?
    llm = st.session_state.get("llm")
    if not llm:
        with st.chat_message("assistant"):
            st.error("Model lokalny nie jest gotowy. Wybierz .gguf po lewej.")
    else:
        # budowa promptu zgodnie z językiem + trybem
        if lang == "Polski":
            head = "Instrukcja: Odpowiadaj po polsku."
            q = f"Pytanie: {prompt}\nOdpowiedź:"
            stop = ["\n","Question:","Pytanie:"] if short_mode else None
        else:
            head = "Instruction: Answer in English."
            q = f"Question: {prompt}\nAnswer:"
            stop = ["\n","Question:","Pytanie:"] if short_mode else None

        full = head + "\n" + q
        kwargs = dict(max_tokens=64, temperature=0.2)
        if short_mode:
            kwargs.update(max_tokens=16, stop=stop)

        try:
            out = llm.create_completion(full, **kwargs)
            txt = (out.get("choices",[{}])[0] or {}).get("text","").strip()
        except Exception as e:
            txt = f"(błąd inferencji: {e})"

        with st.chat_message("assistant"):
            st.write(txt or "(pusto)")

        st.session_state["chat_history"].append(("assistant", txt or ""))
