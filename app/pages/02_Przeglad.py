import os, re, unicodedata, time
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="AI-Audytor – Przegląd", layout="wide")
st.title("🧐 Przegląd rozbieżności (needs_review)")


from app.ui_nav import back as _back
_back()
KOSZTY_FACT = os.getenv("KOSZTY_FACT","")
PRZYCHODY_FACT = os.getenv("PRZYCHODY_FACT","")

def norm(s:str):
    s = (str(s) if s is not None else "").replace("\\","/").split("/")[-1]
    s = unicodedata.normalize("NFKC", s).replace("\xa0"," ").strip().upper()
    return re.sub(r"\s+"," ", s)

def load_csv_pair(kind:str):
    # wybór właściwych plików wynikowych
    base = "out_koszty" if kind=="Koszty" else "out_przychody"
    for name in [f"{base}_hf_recheck_anchor.csv", f"{base}_hf_anywhere.csv"]:
        if Path(name).is_file():
            df = pd.read_csv(name)
            return name, df
    return None, None

def find_pdf(kind:str, filename:str):
    base = KOSZTY_FACT if kind=="Koszty" else PRZYCHODY_FACT
    key = norm(filename)
    for root,_,files in os.walk(base or "."):
        for f in files:
            if f.lower().endswith(".pdf") and norm(f)==key:
                return os.path.join(root,f)
    return None

def load_overrides():
    p=Path("docs/overrides.csv")
    if p.is_file():
        return pd.read_csv(p)
    return pd.DataFrame(columns=["plik","decision","note","ts"])

def save_override(row, decision, note=""):
    o=load_overrides()
    o = pd.concat([o, pd.DataFrame([{
        "plik": row["plik"],
        "decision": decision,     # ok / mismatch
        "note": note,
        "ts": pd.Timestamp.utcnow().isoformat()
    }])], ignore_index=True)
    o.to_csv("docs/overrides.csv", index=False)
    return o

def recompute_effective(kind:str, df:pd.DataFrame):
    """status_effective_override: bierze pod uwagę overrides"""
    o=load_overrides()
    if o.empty:
        df["status_effective_override"] = df["status"]
        return df
    o_map = o.groupby("plik").last()["decision"].to_dict()
    eff = []
    for _,r in df.iterrows():
        dec = o_map.get(r.get("plik"))
        if dec=="ok":
            eff.append("ok")
        elif dec=="mismatch":
            eff.append("mismatch")
        else:
            # domyślna reguła: anchor > anywhere; needs_review traktuj jak mismatch
            if (r.get("status")=="mismatch" and r.get("status_alt")=="ok_anywhere1p"):
                eff.append("mismatch")
            else:
                eff.append(r.get("status"))
    df["status_effective_override"] = eff
    out_name = ("out_koszty" if kind=="Koszty" else "out_przychody")+"_hf_effective_override.csv"
    df.to_csv(out_name, index=False)
    return df

kind = st.radio("Zestaw", ["Koszty","Przychody"], horizontal=True)

src_name, df = load_csv_pair(kind)
if df is None:
    st.error(f"Brak plików wynikowych dla: {kind}. Najpierw uruchom walidację.")
    st.stop()

st.caption(f"Źródło: {src_name}")
needs = df[df.get("status_alt","")=="needs_review"].copy()
if needs.empty:
    st.success("Brak pozycji needs_review 🎉")
    st.dataframe(df.head(20))
    st.stop()

st.subheader("Pozycje do przeglądu")
show_cols = [c for c in ["plik","found_numer","found_data","found_netto","best_page","best_value","best_diff_pct","note_alt"] if c in needs.columns]
st.dataframe(needs[show_cols], use_container_width=True, hide_index=True)

sel = st.selectbox("Wybierz plik do przeglądu:", needs["plik"].tolist())
row = needs[needs["plik"]==sel].iloc[0]

col1, col2 = st.columns(2)
with col1:
    st.write("**Szczegóły dopasowania**")
    st.write({k: row[k] for k in ["best_value","best_diff_pct","best_page","status","status_alt"] if k in row})

with col2:
    st.write("**Podgląd PDF (tekstowo, strona z trafieniem)**")
    path = find_pdf(kind, row["plik"])
    if not path:
        st.error("Nie znaleziono PDF na dysku.")
    else:
        try:
            import pdfplumber
            pg = int(row.get("best_page") or 1)
            with pdfplumber.open(path) as pdf:
                pg = max(1, min(pg, len(pdf.pages)))
                text = pdf.pages[pg-1].extract_text() or ""
            # pokaż tylko kilka linii:
            lines = [l for l in (text.splitlines() if text else []) if l.strip()]
            st.code("\n".join(lines[:40]) if lines else "(brak tekstu na tej stronie)")
            st.caption(f"Plik: {path} (p.{pg})")
        except Exception as e:
            st.warning(f"Podgląd nieudany: {e}")

with st.form("dec_form"):
    st.write("**Twoja decyzja:**")
    decision = st.radio("Akceptujesz tę pozycję?", ["mismatch","ok"], index=0, horizontal=True)
    note = st.text_input("Notatka (opcjonalnie)")
    submitted = st.form_submit_button("Zapisz decyzję")
    if submitted:
        o = save_override(row, decision, note)
        df2 = recompute_effective(kind, df.copy())
        st.success("Zapisano. Przeliczono status_effective_override.")
        st.rerun()
