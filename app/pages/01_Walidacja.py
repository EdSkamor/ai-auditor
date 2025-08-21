import os, signal, subprocess, time, json, pathlib
import pandas as pd
import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parents[2]  # katalog repo
LOGS = ROOT / "logs"
PIDS = ROOT / "pids"
LOGS.mkdir(exist_ok=True); PIDS.mkdir(exist_ok=True)

st.set_page_config(page_title="AI-Audytor – Walidacja", layout="wide")
st.title("🧾 Walidacja (Donut)")


from app.ui_nav import back as _back
_back()
# Guard hasła (opcjonalny)
PW = os.getenv("UI_PASSWORD","")
if PW:
    typed = st.sidebar.text_input("Hasło", type="password")
    if typed != PW:
        st.info("Wpisz hasło, aby korzystać z aplikacji.")
        st.stop()

# Parametry
kind = st.selectbox("Zakres", ["koszty","przychody"], index=0)
mode = st.selectbox("Tryb", ["strict","anywhere1p"], index=0)
donut_model = os.getenv("DONUT_MODEL","SKamor/ai-audytor-donut-local")

# Ścieżki wyników
CSV_MAIN = ROOT / f"out_{kind}_hf.csv"
CSV_ANY  = ROOT / f"out_{kind}_hf_anywhere.csv"
CSV_EFF  = ROOT / f"out_{kind}_hf_effective.csv"
LOG_FILE = LOGS / f"validate_{kind}_{mode}.txt"
PID_FILE = PIDS / f"validate_{kind}.pid"

colA, colB, colC = st.columns(3)

def start_validation():
    if PID_FILE.exists():
        st.warning("Proces już działa (PID plik istnieje). Najpierw STOP.")
        return
    cmd = f'''
        cd "{ROOT}" && source .venv/bin/activate && export PYTHONPATH="$PWD:$PYTHONPATH" && \
        export DONUT_MODEL="{donut_model}" && export USE_DONUT=1 && \
        scripts/validate2.sh {kind} {mode}
    '''
    logf = open(LOG_FILE, "w")
    proc = subprocess.Popen(["bash","-lc", cmd], stdout=logf, stderr=subprocess.STDOUT)
    PID_FILE.write_text(str(proc.pid), encoding="utf-8")

def stop_validation():
    try:
        pid = int(PID_FILE.read_text().strip())
    except Exception:
        pid = None
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.8)
            # jeśli nadal żyje – kill -9
            try:
                os.kill(pid, 0)
                os.kill(pid, signal.SIGKILL)
            except Exception:
                pass
        except Exception:
            pass
    if PID_FILE.exists():
        PID_FILE.unlink(missing_ok=True)

def pid_alive():
    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, 0)
        return True, pid
    except Exception:
        return False, None

with colA:
    if st.button("▶ START walidacji"):
        start_validation()
        st.toast("Wystartowano walidację.", icon="✅")
with colB:
    if st.button("⏹ STOP walidacji"):
        stop_validation()
        st.toast("Zatrzymano walidację.", icon="🛑")
with colC:
    if st.button("🔄 Odśwież"):
        st.experimental_rerun()

alive, pid = pid_alive()
st.caption(f"Stan procesu: {'Działa' if alive else 'Nie działa'}{f' (PID={pid})' if pid else ''}")
st.caption(f"Model Donut: {donut_model}")

# Podgląd logów
st.subheader("Log procesu")
if LOG_FILE.exists():
    with st.expander(f"📜 {LOG_FILE.name}", expanded=True):
        try:
            last_k = LOG_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()[-300:]
            st.code("\n".join(last_k) if last_k else "(pusty)", language="bash")
        except Exception as e:
            st.warning(f"Nie mogę odczytać loga: {e}")
else:
    st.info("Brak logu – jeszcze nie uruchamiałeś procesu w tym trybie.")

# Podsumowania CSV
def show_counts(title, path):
    st.markdown(f"**{title}**")
    if not path.exists():
        st.write("— brak pliku")
        return
    try:
        df = pd.read_csv(path)
        if "status" in df.columns:
            st.write(df["status"].value_counts(dropna=False))
        else:
            st.write("brak kolumny 'status' (plik częściowy?)")
        st.caption(f"wierszy: {len(df)}  •  plik: {path.name}")
    except Exception as e:
        st.warning(f"Nie mogę wczytać {path.name}: {e}")

st.subheader("Wyniki")
c1, c2, c3 = st.columns(3)
with c1: show_counts("Główny raport", CSV_MAIN)
with c2: show_counts("ANYWHERE (jeśli uruchamiałeś)", CSV_ANY)
with c3: show_counts("Effective (po flipach)", CSV_EFF)

# Flipy ANYWHERE (mismatch -> ok_anywhere1p)
st.subheader("Flipy ANYWHERE (mismatch → ok_anywhere1p)")
if CSV_ANY.exists():
    try:
        df = pd.read_csv(CSV_ANY)
        if {"status","status_alt"}.issubset(df.columns):
            flips = df[(df["status"]=="mismatch") & (df["status_alt"]=="ok_anywhere1p")]
            if len(flips):
                cols = [c for c in ["plik","best_page","best_value","best_diff_pct","note_alt"] if c in flips.columns]
                st.dataframe(flips[cols], use_container_width=True, hide_index=True)
            else:
                st.write("— brak flipów")
        else:
            st.write("— brak kolumn status_alt (nie uruchamiałeś recheck_anywhere?)")
    except Exception as e:
        st.warning(f"Problem z wczytaniem ANYWHERE: {e}")
else:
    st.info("Nie znaleziono pliku ANYWHERE dla tego zakresu/trybu.")

st.divider()
st.caption("Uwaga: ta strona wywołuje lokalnie `scripts/validate2.sh`. Dane nie wychodzą na zewnątrz.")
