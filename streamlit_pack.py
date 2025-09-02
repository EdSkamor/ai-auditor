import os, glob, subprocess, time, json
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Asystent Audytora – Paczka Runu", layout="wide")
st.title("📦 Paczka runu + podgląd Top50")

ROOT="web_runs"
def list_runs(root=ROOT):
    runs=[d for d in glob.glob(f"{root}/*/") if os.path.isdir(d)]
    runs.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return runs

runs = list_runs()
if not runs:
    st.warning("Brak katalogów w web_runs/*. Uruchom najpierw audyt.")
    st.stop()

run = st.selectbox("Wybierz run", runs, index=0)
colA, colB = st.columns([1,1])

with colA:
    st.subheader("Top 50 niezgodności")
    path_top = os.path.join(run, "verdicts_top50_mismatches.csv")
    if os.path.isfile(path_top):
        df = pd.read_csv(path_top)
        st.dataframe(df.head(50), use_container_width=True, hide_index=True)
    else:
        # awaryjnie budujemy z verdicts.jsonl
        jlines=[]
        vpath = os.path.join(run,"verdicts.jsonl")
        if os.path.isfile(vpath):
            with open(vpath, encoding="utf-8") as f:
                for i,l in enumerate(f):
                    try:
                        j=json.loads(l)
                        if j.get("zgodnosc")=="NIE":
                            jlines.append(j)
                    except: pass
                    if len(jlines)>=50: break
            if jlines:
                df = pd.json_normalize(jlines)
                cols = [c for c in df.columns if c.endswith(("sekcja","pozycja_id","numer_pop","data_pop","netto_pop","zgodnosc","porownanie.numer","porownanie.data","porownanie.netto","pdf.sciezka"))]
                st.dataframe(df[cols], use_container_width=True, hide_index=True)
            else:
                st.info("Brak niezgodności lub brak pliku top50.")

with colB:
    st.subheader("Paczka handoff (.zip)")
    with st.form("pack_form"):
        with_pdfs = st.checkbox("Dołącz RAW PDF-y (większy plik)", value=False)
        submitted = st.form_submit_button("Utwórz paczkę")
    if submitted:
        cmd = ["bash","-lc", f"scripts/pack_run.sh '{run.rstrip('/')}'"+(" --with-pdfs" if with_pdfs else "")]
        st.code(" ".join(cmd), language="bash")
        r = subprocess.run(cmd, text=True, capture_output=True)
        st.text(r.stdout or "")
        if r.returncode!=0:
            st.error(r.stderr or "Błąd tworzenia paczki")
        # znajdź świeżo utworzony .zip
        zips = sorted(glob.glob(os.path.join(run,"handoff_*.zip")), key=os.path.getmtime, reverse=True)
        if zips:
            z = zips[0]
            st.success(f"Gotowe: {os.path.basename(z)}")
            with open(z, "rb") as f:
                st.download_button("⬇️ Pobierz ZIP", data=f.read(), file_name=os.path.basename(z), mime="application/zip")
        else:
            st.warning("Nie znaleziono wygenerowanego ZIP-a.")

st.caption(f"Ścieżka runu: {run}")
