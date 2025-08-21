import os, subprocess, pandas as pd, streamlit as st
from huggingface_hub import HfFolder, whoami

st.set_page_config(page_title="AI-Audytor – Demo", layout="wide")
st.title("AI-Audytor – Demo walidacji (HF / lokalny Donut)")

with st.sidebar:
    st.header("Hugging Face")
    tok = st.text_input("HF token (Model: Read)", type="password", help="Z /settings/tokens na Hugging Face")
    col_a, col_b = st.columns(2)
    if col_a.button("Zapisz token"):
        if tok.strip():
            HfFolder.save_token(tok.strip())
            st.success("Token zapisany.")
            try:
                me = whoami()
                name = me.get("name") or (me.get("orgs") or ["?"])[0]
                st.caption(f"Zalogowano jako: {name}")
            except Exception:
                st.caption("Token zapisany. (Nie udało się potwierdzić konta).")

    st.header("Ustawienia")
    scenario = st.selectbox("Zbiór", ["koszty","przychody"])
    mode     = st.selectbox("Tryb", ["strict","anywhere1p"], help="ANYWHERE ≤1% = łagodniejsza walidacja")
    donut    = st.text_input("DONUT_MODEL", os.environ.get("DONUT_MODEL","SKamor/ai-audytor-donut-local"))

st.subheader("Wejścia (auto-wykryte ścieżki)")
env = os.environ.copy()
for key in ["KOSZTY_RES","KOSZTY_FACT","PRZYCHODY_RES","PRZYCHODY_FACT"]:
    st.caption(f"{key}: {env.get(key,'—')}")

run = st.button("▶ Uruchom walidację")

def show_csv(p):
    if os.path.isfile(p):
        d = pd.read_csv(p)
        st.write(f"**{p}** — {len(d)} wierszy")
        if "status" in d.columns:
            st.write(d["status"].value_counts(dropna=False))
        st.download_button(f"Pobierz {p}", d.to_csv(index=False).encode("utf-8"),
                           file_name=p, mime="text/csv")
    else:
        st.warning(f"Brak pliku: {p}")

if run:
    env = os.environ.copy()
    env["USE_DONUT"] = "1"
    env["DONUT_MODEL"] = donut
    env.setdefault("OMP_NUM_THREADS","4")
    env["CUDA_VISIBLE_DEVICES"] = ""  # CPU

    cmd = ["bash","scripts/validate2.sh", scenario, mode]
    st.write("Komenda:", " ".join(cmd))

    log_area = st.empty()
    with st.status("Pracuję…", expanded=True) as status:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, env=env)
        lines = []
        for line in proc.stdout:
            lines.append(line.rstrip())
            log_area.write("\n".join(lines[-200:]))
        rc = proc.wait()
        if rc == 0:
            status.update(label="Zakończono", state="complete")
        else:
            status.update(label=f"Zakończono z kodem {rc}", state="error")

    base = "koszty" if scenario=="koszty" else "przychody"
    show_csv(f"out_{base}_hf.csv")
    show_csv(f"out_{base}_hf_anywhere.csv")

st.caption("Używa scripts/validate2.sh (+ recheck_anywhere.py dla trybu ANYWHERE). Dane i modele zostają lokalnie.")
