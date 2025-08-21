import os, time, subprocess, io
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="AI-Audytor — Chat", layout="wide")

# ==== LEWA KOLUMNA: ustawienia ====
with st.sidebar:
    st.header("Ustawienia")
    donut = st.text_input("DONUT_MODEL", os.environ.get("DONUT_MODEL","SKamor/ai-audytor-donut-local"))
    anywhere = st.toggle("ANYWHERE ≤1%", value=False, help="Po walidacji złagodź rozjazdy do 1% (tryb 'anywhere1p').")
    zbior = st.selectbox("Zbiór do walidacji", ["koszty","przychody"])
    st.caption("Pliki przetwarzane lokalnie. Wyniki do pobrania jako CSV.")

# ==== PASEK TYTUŁU ====
st.markdown("## AI-Audytor — Chat (wrzuć pliki i zadaj pytanie)")
st.markdown("**Tu dodaj pliki** ⬇️ (PDF, XLSX) — potem wciśnij **Uruchom walidację**.")

# ==== UPLOAD ====
up = st.file_uploader("Drag & drop lub wybierz pliki", type=["pdf","xlsx"], accept_multiple_files=True, label_visibility="collapsed")

# gdzie zapisać
UPLOADS = Path("uploads")
session_dir = UPLOADS / f"sess_{int(time.time())}"
session_dir.mkdir(parents=True, exist_ok=True)
fact_dir = session_dir / "Faktury"; fact_dir.mkdir(exist_ok=True)

xlsx_path = None
if up:
    for f in up:
        buf = io.BytesIO(f.getvalue())
        if f.name.lower().endswith((".xlsx",".xls")):
            xlsx_path = session_dir / f.name
            xlsx_path.write_bytes(buf.getbuffer())
        elif f.name.lower().endswith(".pdf"):
            (fact_dir / f.name).write_bytes(buf.getbuffer())

# auto-detekcja ścieżek, jeśli nic nie wrzucono
def find_resolved(which):
    base = Path("data/incoming")
    a = "koszty" if which=="koszty" else "przychody"
    for p in base.rglob("*.xlsx"):
        n = p.name.lower()
        if a in n and "populacja_normalized_resolved" in n:
            return p
    return None

if not xlsx_path:
    auto = find_resolved(zbior)
else:
    auto = None

res_path = str(xlsx_path or auto or "")
fact_path = str(fact_dir if list(fact_dir.glob("*.pdf")) else (Path(res_path).resolve().parent.parent / "Faktury" if res_path else ""))

# pokaz wejścia (prosto)
st.code(f"RES={res_path or '—'}\nFACT={fact_path or '—'}")

# ==== PRZYCISK WALIDACJI ====
col1, col2 = st.columns([1,3])
with col1:
    run = st.button("▶ Uruchom walidację", use_container_width=True)
with col2:
    tryb = "anywhere1p" if anywhere else "strict"
    st.write(f"Tryb: **{tryb}**  |  Model: `{donut}`")

def show_csv(path: str, label: str):
    p = Path(path)
    if not p.is_file():
        st.warning(f"Brak pliku: {p}")
        return
    df = pd.read_csv(p)
    st.subheader(label)
    if "status" in df.columns:
        st.write(df["status"].value_counts(dropna=False))
    st.dataframe(df.head(50), use_container_width=True)
    st.download_button("Pobierz CSV", p.read_bytes(), file_name=p.name, mime="text/csv")

def run_validation():
    if not res_path or not fact_path:
        st.error("Uzupełnij wejścia: potrzebny arkusz XLSX (RES) i katalog/plik(i) PDF (FACT).")
        return
    env = os.environ.copy()
    env["DONUT_MODEL"] = donut
    env["USE_DONUT"] = "1"
    if zbior=="koszty":
        env["KOSZTY_RES"] = res_path
        env["KOSZTY_FACT"] = fact_path
    else:
        env["PRZYCHODY_RES"] = res_path
        env["PRZYCHODY_FACT"] = fact_path

    cmd = ["bash","scripts/validate2.sh", zbior, "anywhere1p" if anywhere else "strict"]
    st.code(" ".join(cmd))
    t0 = time.time()
    proc = subprocess.run(cmd, env=env, text=True, capture_output=True)
    st.text(proc.stdout[-8000:] or "(brak stdout)")
    if proc.returncode != 0:
        st.error(f"Błąd (exit={proc.returncode}).")
        st.code(proc.stderr[-4000:])
    else:
        st.success(f"Gotowe w {time.time()-t0:.1f}s")

    out_main = f"out_{zbior}_hf.csv"
    out_any  = f"out_{zbior}_hf_anywhere.csv"
    show_csv(out_main, f"Wyniki — {zbior.upper()} (strict)")
    if Path(out_any).is_file():
        show_csv(out_any, f"Wyniki — {zbior.upper()} (ANYWHERE)")

if run:
    run_validation()

st.divider()

# ==== CHAT (serce interfejsu) ====
st.markdown("### Chat")
if "chat" not in st.session_state:
    st.session_state.chat = []
for role, msg in st.session_state.chat:
    st.chat_message(role).write(msg)

prompt = st.chat_input("Napisz pytanie/audytowe (tu rozmawiasz z AI)")
if prompt:
    st.session_state.chat.append(("user", prompt))
    st.chat_message("user").write(prompt)

    # prosty router: jeśli padło słowo "walidacja" → kliknij przycisk powyżej
    if "walidac" in prompt.lower():
        st.session_state.chat.append(("assistant", "Jasne — użyj przycisku **Uruchom walidację** powyżej."))
        st.chat_message("assistant").write("Jasne — użyj przycisku **Uruchom walidację** powyżej.")
    else:
        # placeholder do czasu podpięcia lokalnej LLM
        st.session_state.chat.append(("assistant", "Dzięki! W tej wersji jestem notatnikiem. Analizy i odpowiedzi eksperckie włączymy tu po spięciu LLM."))
        st.chat_message("assistant").write("Dzięki! W tej wersji jestem notatnikiem. Analizy i odpowiedzi eksperckie włączymy tu po spięciu LLM.")
