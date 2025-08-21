import os, subprocess, tempfile, time, pathlib, json
from dotenv import load_dotenv
import streamlit as st

# === Auth (proste) ===
load_dotenv(".env.chat-local")
APP_PASSWORD = os.getenv("APP_PASSWORD", "")
if "auth" not in st.session_state:
    st.session_state.auth = False

def login_box():
    st.title("AI-Audytor — logowanie")
    pw = st.text_input("Hasło", type="password")
    if st.button("Zaloguj"):
        if APP_PASSWORD and pw == APP_PASSWORD:
            st.session_state.auth = True
        else:
            st.error("Błędne hasło")

if not st.session_state.auth:
    login_box()
    st.stop()

st.set_page_config(page_title="AI-Audytor — Chat", layout="wide")
st.title("AI-Audytor — Chat")

# Szybkie ustawienia (model Donut + tryb)
with st.sidebar:
    st.header("Ustawienia")
    donut = st.text_input("DONUT_MODEL", os.environ.get("DONUT_MODEL","SKamor/ai-audytor-donut-local"))
    use_anywhere = st.checkbox("ANYWHERE ≤1%", value=False)
    st.caption("Pliki pozostają lokalnie. Wyniki możesz pobrać jako CSV/XLSX.")

# Historia czatu
if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"assistant", "content":"Cześć! Wrzuć pliki PDF/XLSX i napisz, co sprawdzić."}]

# Render historii
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Upload plików (wielokrotny)
uploads = st.file_uploader("Dołącz pliki (PDF, XLSX)", type=["pdf","xlsx"], accept_multiple_files=True)

# Gdzie zapisać pliki sesji
session_dir = pathlib.Path(tempfile.gettempdir()) / f"ai_audytor_{st.session_state.get('session_id','sess')}"
session_dir.mkdir(exist_ok=True, parents=True)

def save_uploads(files):
    saved = []
    for f in files or []:
        outp = session_dir / f.name
        with open(outp, "wb") as w:
            w.write(f.read())
        saved.append(str(outp))
    return saved

def run_validate(saved_files, donut_model, anywhere=False):
    # heurystyka: wybierz pierwszy XLSX jako RES i katalog PDF jako FACT
    xlsx = next((p for p in saved_files if p.lower().endswith(".xlsx")), None)
    pdfs = [p for p in saved_files if p.lower().endswith(".pdf")]
    if not xlsx or not pdfs:
        return {"ok":False, "msg":"Potrzebny przynajmniej 1 XLSX + 1 PDF.", "out":""}

    fact_dir = str(pathlib.Path(pdfs[0]).parent)
    mode = "anywhere1p" if anywhere else "strict"

    env = os.environ.copy()
    env["DONUT_MODEL"] = donut_model
    env["USE_DONUT"] = "1"

    # wybiórczo uruchamiamy „koszty” albo „przychody” na podstawie nazwy xlsx
    zbior = "koszty" if "koszt" in pathlib.Path(xlsx).name.lower() else "przychody"
    cmd = ["bash","scripts/validate2.sh", zbior, mode]

    # jednorazowo nadpisujemy zmienne, żeby wrapper użył naszych ścieżek
    env["KOSZTY_RES"] = xlsx
    env["KOSZTY_FACT"] = fact_dir
    env["PRZYCHODY_RES"] = xlsx
    env["PRZYCHODY_FACT"] = fact_dir

    try:
        p = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=3600)
        out = (p.stdout or "") + "\n" + (p.stderr or "")
        ok = p.returncode == 0 or "✅ Raport:" in out
        return {"ok":ok, "msg":"Walidacja zakończona." if ok else "Walidacja nie powiodła się.", "out":out}
    except subprocess.TimeoutExpired:
        return {"ok":False, "msg":"Przekroczono czas walidacji.", "out":""}

user_input = st.chat_input("Napisz, co zrobić… (np. „Sprawdź spójność”, „Duplikaty numerów”, „Anomalie kwot”)")
if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        saved = save_uploads(uploads)
        if saved:
            st.caption(f"Zapisane pliki: {', '.join([pathlib.Path(s).name for s in saved])}")
        # Prosta routing-logika: jeśli padło „sprawdź / waliduj”, odpalamy narzędzie
        intent = ("sprawd" in user_input.lower()) or ("walid" in user_input.lower())
        if intent and saved:
            with st.spinner("Pracuję nad walidacją…"):
                res = run_validate(saved, donut, use_anywhere)
            st.write(res["msg"])
            # krótki podgląd wyników, jeśli pliki powstały
            for fname in ["out_koszty_hf.csv","out_koszty_hf_anywhere.csv",
                          "out_przychody_hf.csv","out_przychody_hf_anywhere.csv",
                          "out_koszty_hf_effective.csv"]:
                fp = session_dir.parent.parent / "ai-audytor" / fname  # fallback: repo root
                if not fp.exists():
                    fp = pathlib.Path(fname)
                if fp.exists():
                    st.download_button(f"Pobierz {fp.name}", data=open(fp,"rb").read(), file_name=fp.name)
            st.code(res["out"][-2000:], language="bash")
            st.session_state.messages.append({"role":"assistant","content":res["msg"]})
        else:
            st.markdown("OK — mam pliki/wiadomość. W tej wersji potrafię od razu uruchomić **walidację**; "
                        "pozostałe analizy (duplikaty/anomalie) dołączymy jako kolejne narzędzia.")
