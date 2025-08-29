import os, io, time, json, base64, shutil, subprocess
from pathlib import Path
import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Asystent Audytora – Panel", page_icon="📄", layout="wide")

# =============== MOTYW (jasny/ciemny + akcent spójnie) ===============
def inject_theme(mode: str, accent: str):
    st.markdown(r"""
<style id="theme-vars">
html[data-app-theme="light"] {
  --bg:#ffffff; --text:#0f172a; --muted:#475569; --card:#f8fafc; --border:#e5e7eb;
  --code:#0f172a; --code-bg:#f3f4f6;
  color-scheme: light;
}
html[data-app-theme="dark"] {
  --bg:#0b0e14; --text:#e5e7eb; --muted:#9aa3af; --card:#11151f; --border:#2b3240;
  --code:#e5e7eb; --code-bg:#0f1320;
  color-scheme: dark;
}
html[data-accent="blue"]   { --accent:#3b82f6; --accent-contrast:#fff; }
html[data-accent="green"]  { --accent:#10b981; --accent-contrast:#0b0e14; }
html[data-accent="amber"]  { --accent:#f59e0b; --accent-contrast:#0b0e14; }
html[data-accent="purple"] { --accent:#8b5cf6; --accent-contrast:#fff; }

/* tło/kolor ogólny */
.stApp, .block-container { background: var(--bg) !important; color: var(--text) !important; }
[data-testid="stHeader"] { background: var(--bg) !important; }
section[data-testid="stSidebar"] { background: var(--card) !important; border-right:1px solid var(--border); }
section[data-testid="stSidebar"] * { color: var(--text) !important; }
hr, .stDivider { border-color: var(--border) !important; }

/* wejścia/wyjścia */
.stTextInput input, .stTextArea textarea, .stSelectbox div[role="combobox"],
.stNumberInput input, .stFileUploader, textarea, input, select, .stMultiSelect, .stDateInput input {
  background: var(--card) !important; color: var(--text) !important; border:1px solid var(--border) !important;
}
.stAlert, .stExpander, .stTabs { background: var(--card) !important; }

/* przyciski */
.stButton>button, .stDownloadButton>button[kind="primary"] {
  background: var(--accent) !important; color: var(--accent-contrast) !important; border:0 !important; box-shadow:none !important;
}
.stDownloadButton>button:not([kind="primary"]) {
  background: var(--card) !important; color: var(--text) !important; border:1px solid var(--border) !important;
}

/* tabele/df */
[data-testid="stDataFrame"] * { color: var(--text) !important; }
[data-testid="stDataFrame"] div { border-color: var(--border) !important; }
.stTable { border-color: var(--border) !important; }

/* code blocks / logi */
code, pre, .stCode { color: var(--code) !important; background: var(--code-bg) !important; }

/* linki */
a { color: var(--accent) !important; }
</style>
    """, unsafe_allow_html=True)

    # Uwaga: .lower() po stronie Pythona (wcześniej był błąd .toLowerCase())
    st.markdown(f"""
<script>
(function() {{
  const html = document.documentElement;
  const mode = "{(mode or 'System').lower()}";
  const accent = "{(accent or 'Blue').lower()}";
  const sysDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

  let theme = localStorage.getItem('app-theme');
  let acc   = localStorage.getItem('app-accent');

  if (!theme) {{
    theme = (mode==="ciemny") ? "dark" : (mode==="jasny") ? "light" : (sysDark ? "dark" : "light");
  }} else {{
    if (mode==="ciemny") theme = "dark";
    if (mode==="jasny")  theme = "light";
    if (mode==="system") theme = (sysDark ? "dark" : "light");
  }}
  acc = (accent || acc || "blue");

  localStorage.setItem('app-theme', theme);
  localStorage.setItem('app-accent', acc);
  html.setAttribute('data-app-theme', theme);
  html.setAttribute('data-accent', acc);
}})();
</script>
    """, unsafe_allow_html=True)

# =============== SIDEBAR: pełne menu + motyw + reset biegu ===============
PAGES = [
    "Panel testów",
    "Wyniki ostatniego biegu",
    "Przegląd PDF (preview)",
    "Niejednoznaczności",
    "Chat operacyjny",
    "Indeks PDF (manualny)",
    "Renamer (z ostatniego biegu)",
    "Ustawienia / Motyw",
    "Pomoc"
]

def _reset_run():
    for k in ["run_dir","last_run","messages"]:
        if k in st.session_state: del st.session_state[k]
    st.toast("Zresetowano kontekst biegu.", icon="✅")

with st.sidebar:
    st.header("Nawigacja")
    page = st.radio("Sekcja", PAGES, index=0)
    st.divider()
    colA, colB = st.columns(2)
    with colA:
        theme_choice = st.selectbox("Motyw", ["System", "Jasny", "Ciemny"], index=0, key="theme_choice")
    with colB:
        accent_choice = st.selectbox("Akcent", ["Blue", "Green", "Amber", "Purple"], index=0, key="accent_choice")
    inject_theme(theme_choice, accent_choice)
    st.caption("Obsługa wielu PDF (30+).")
    if st.button("♻️ Reset biegu", use_container_width=True):
        _reset_run()

# =============== wspólne utils ===============
def _save_bytes(file, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as f: f.write(file.getbuffer())

def _run(cmd, cwd=None, label=None):
    if label: st.info(label)
    st.write("`$ " + " ".join(cmd) + "`")
    with st.status("Wykonywanie...", expanded=False) as status:
        p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
        if p.stdout: st.code(p.stdout.strip()[-20000:])
        if p.stderr: st.code(p.stderr.strip()[-20000:], language="bash")
        status.update(state="complete", label="Zakończono")
    return p.returncode

def _ensure_run_dir():
    if "run_dir" not in st.session_state:
        stamp = time.strftime("%Y%m%d_%H%M%S")
        st.session_state.run_dir = Path("web_runs") / stamp
    run_dir = Path(st.session_state.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "pdfs").mkdir(parents=True, exist_ok=True)
    return run_dir

def _render_downloads(run_dir: Path):
    files = [
        ("📥 All_invoices.csv", run_dir/"All_invoices.csv"),
        ("📥 verdicts.jsonl", run_dir/"verdicts.jsonl"),
        ("📥 verdicts_summary.json", run_dir/"verdicts_summary.json"),
        ("📥 populacja_enriched.xlsx", run_dir/"populacja_enriched.xlsx"),
    ]
    for label, p in files:
        if p.exists():
            st.download_button(label, data=open(p,"rb").read(), file_name=p.name, key=str(p))

def _make_zip_bundle(run_dir: Path)->Path|None:
    out_base = run_dir / "export_bundle"
    out_path = Path(shutil.make_archive(str(out_base), "zip", root_dir=str(run_dir)))
    return out_path if out_path.exists() else None

def _pdf_preview(file_path: Path, height=650):
    try:
        b = open(file_path, "rb").read()
        b64 = base64.b64encode(b).decode("ascii")
        html = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="{height}" style="border:1px solid var(--border)"></iframe>'
        st.components.v1.html(html, height=height+10, scrolling=True)
    except Exception as e:
        st.warning(f"Nie udało się wczytać PDF: {e}")

# =============== Strony ===============
def page_panel_testow():
    st.title("📄 Panel testów wiarygodności")
    run_dir = _ensure_run_dir()
    pdf_dir = run_dir / "pdfs"

    st.subheader("1) Wgraj pliki")
    pop_file = st.file_uploader("Plik populacji (XLSX)", type=["xlsx"], accept_multiple_files=False)
    pdf_files = st.file_uploader("Faktury (PDF – możesz wybrać 30+)", type=["pdf"], accept_multiple_files=True)
    c1, c2 = st.columns(2)
    with c1:
        if pop_file: st.success(f"Załadowano: {pop_file.name}")
    with c2:
        st.info(f"PDF: {len(pdf_files or [])} plików")

    st.divider()
    st.subheader("2) Ustawienia")
    cc1, cc2, cc3 = st.columns([1,1,2])
    with cc1:
        opt_rename = st.checkbox("Proponuj nazwy (rename) w raporcie", value=True)
    with cc2:
        opt_apply  = st.checkbox("Wykonaj rename (kopie do katalogu)", value=False)
    with cc3:
        rename_dir = st.text_input("Katalog docelowy rename", value="renamed")

    st.divider()
    st.subheader("3) Uruchom")
    if st.button("🚀 Start"):
        if not pop_file:
            st.error("Wgraj najpierw plik populacji (XLSX).")
            st.stop()

        # zapisz wejścia
        pop_path = run_dir / "populacja.xlsx"
        _save_bytes(pop_file, pop_path)
        for f in (pdf_files or []): _save_bytes(f, pdf_dir / f.name)

        st.write(f"Run dir: `{run_dir}`")
        st.write(f"PDF dir: `{pdf_dir}`")

        # A) indeks PDF
        rc = _run([os.fspath(Path(os.sys.executable)), "pdf_indexer.py",
                   os.fspath(pdf_dir), os.fspath(run_dir/"All_invoices.csv")],
                  cwd=REPO_ROOT, label="Krok A: indeks PDF (pdf_indexer.py)")
        if rc != 0: st.stop()

        # B) matcher
        cmd = [os.fspath(Path(os.sys.executable)), "pop_matcher.py",
               "--pop", os.fspath(pop_path),
               "--pdf-root", os.fspath(pdf_dir),
               "--out-jsonl", os.fspath(run_dir/"verdicts.jsonl"),
               "--out-xlsx", os.fspath(run_dir/"populacja_enriched.xlsx"),
               "--index-csv", os.fspath(run_dir/"All_invoices.csv")]
        if opt_rename: cmd.append("--rename")
        if opt_apply: cmd += ["--apply", "--rename-dir", os.fspath(run_dir/rename_dir), "--attach-col", "ZAŁĄCZNIK"]
        rc = _run(cmd, cwd=REPO_ROOT, label="Krok B: testy wiarygodności (pop_matcher.py)")
        if rc != 0: st.stop()

        # C) metryki
        sum_path = run_dir / "verdicts_summary.json"
        if sum_path.exists():
            summary = json.load(open(sum_path, "r", encoding="utf-8"))
            st.success("Gotowe ✅ — poniżej metryki i top niezgodności")
            m = summary.get("metryki", {})
            a,b,c,d = st.columns(4)
            a.metric("Pozycji KOSZTY", m.get("liczba_pozycji_koszty",0))
            b.metric("PDF KOSZTY", m.get("liczba_pdf_koszty",0))
            c.metric("Pozycji PRZYCHODY", m.get("liczba_pozycji_przychody",0))
            d.metric("PDF PRZYCHODY", m.get("liczba_pdf_przychody",0))

            st.markdown("#### Niezgodności (liczby)")
            st.write(pd.DataFrame([m.get("niezgodnosci", {})]))

            top_csv = run_dir / "verdicts_top50_mismatches.csv"
            if top_csv.exists():
                st.markdown("#### Top 50 niezgodności")
                st.dataframe(pd.read_csv(top_csv), use_container_width=True, height=380)

            st.session_state.last_run = {
                "dir": os.fspath(run_dir),
                "summary": os.fspath(sum_path),
                "verdicts": os.fspath(run_dir/"verdicts.jsonl"),
                "enriched": os.fspath(run_dir/"populacja_enriched.xlsx"),
                "allcsv": os.fspath(run_dir/"All_invoices.csv"),
            }
            _render_downloads(run_dir)
            # ZIP
            if st.button("📦 Pobierz ZIP z całym biegiem"):
                zip_path = _make_zip_bundle(run_dir)
                if zip_path:
                    st.download_button("Pobierz export_bundle.zip", data=open(zip_path,"rb").read(),
                                       file_name="export_bundle.zip")
        else:
            st.warning("Brak verdicts_summary.json — sprawdź logi powyżej.")

def page_wyniki():
    st.title("📊 Wyniki ostatniego biegu")
    data = st.session_state.get("last_run")
    if not data:
        st.info("Uruchom najpierw **Panel testów**.")
        return
    run_dir = Path(data["dir"])
    st.write(f"Katalog biegu: `{run_dir}`")

    if (run_dir/"verdicts_summary.json").exists():
        s = json.load(open(run_dir/"verdicts_summary.json","r",encoding="utf-8"))
        st.subheader("Metryki")
        st.json(s.get("metryki", {}))
        st.subheader("Uwagi globalne")
        for u in s.get("uwagi_globalne", []): st.write("- " + u)

    if (run_dir/"verdicts.jsonl").exists():
        rows=[]
        with open(run_dir/"verdicts.jsonl","r",encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i>=500: break
                try: rows.append(json.loads(line))
                except: pass
        if rows:
            st.subheader("Podgląd wyników (max 500)")
            st.dataframe(pd.json_normalize(rows), use_container_width=True, height=420)

    st.subheader("Pobrania")
    _render_downloads(run_dir)
    if st.button("📦 Zbiorczy ZIP"):
        zip_path = _make_zip_bundle(run_dir)
        if zip_path:
            st.download_button("Pobierz export_bundle.zip", data=open(zip_path,"rb").read(),
                               file_name="export_bundle.zip", key="zip2")

def page_pdf_preview():
    st.title("🗂️ Przegląd PDF (preview)")
    data = st.session_state.get("last_run")
    if not data:
        st.info("Uruchom najpierw **Panel testów**.")
        return
    run_dir = Path(data["dir"]); pdf_dir = run_dir/"pdfs"
    files = sorted([p for p in pdf_dir.glob("**/*.pdf")])
    st.write(f"Znaleziono {len(files)} plików PDF.")
    if not files: return
    names = [str(p.relative_to(run_dir)) for p in files]
    pick = st.selectbox("Wybierz plik do podglądu", names)
    if pick:
        fpath = run_dir / pick
        _pdf_preview(fpath)

def page_ambiguous():
    st.title("🧩 Niejednoznaczności / braki")
    data = st.session_state.get("last_run")
    if not data:
        st.info("Uruchom najpierw **Panel testów**.")
        return
    run_dir = Path(data["dir"])
    ver = run_dir/"verdicts.jsonl"
    if not ver.exists():
        st.warning("Brak verdicts.jsonl")
        return
    rows=[]
    with open(ver,"r",encoding="utf-8") as f:
        for line in f:
            try:
                j = json.loads(line)
                stt = (j.get("dopasowanie") or {}).get("status")
                if stt in ("wiele","brak"):
                    rows.append(j)
            except: pass
    if not rows:
        st.success("Brak pozycji z 'wiele' lub 'brak' — nice!")
        return
    df = pd.json_normalize(rows)
    st.dataframe(df, use_container_width=True, height=420)
    # eksport listy do CSV (pomocniczo dla ręcznego wskazania)
    buf = io.StringIO()
    pd.DataFrame(df).to_csv(buf, index=False)
    st.download_button("Pobierz listę (CSV)", buf.getvalue().encode("utf-8"), "niejednoznacznosci.csv")

def page_chat():
    st.title("💬 Chat operacyjny")
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role":"assistant","content":"Cześć! Użyj słów kluczowych: `metryki`, `niezgodności`, `export` (po wcześniejszym uruchomieniu testów)."}]
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    msg = st.chat_input("Zadaj pytanie")
    if msg:
        st.session_state.messages.append({"role":"user","content":msg})
        reply = "Użyj: `metryki`, `niezgodności`, `export`."
        last = st.session_state.get("last_run", {})
        if msg.strip().lower()=="metryki" and last.get("summary"):
            s = json.load(open(last["summary"], "r", encoding="utf-8"))
            m = s.get("metryki", {})
            reply = f"""**Metryki**
- Pozycji KOSZTY: {m.get('liczba_pozycji_koszty',0)}
- PDF KOSZTY: {m.get('liczba_pdf_koszty',0)}
- Pozycji PRZYCHODY: {m.get('liczba_pozycji_przychody',0)}
- PDF PRZYCHODY: {m.get('liczba_pdf_przychody',0)}
- Niezgodności: {m.get('niezgodnosci',{})}"""
        elif msg.strip().lower()=="niezgodności" and last.get("verdicts"):
            rows=[]
            with open(last["verdicts"], "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if i>=5: break
                    try: rows.append(json.loads(line))
                    except: pass
            if rows:
                st.dataframe(pd.json_normalize(rows), use_container_width=True)
                reply = "Powyżej pierwsze 5 wierszy."
        elif msg.strip().lower()=="export" and last:
            reply = "Eksporty pobierzesz w **Wyniki ostatniego biegu** albo w **Panel testów** (sekcja: Pobierz pliki)."
        st.session_state.messages.append({"role":"assistant","content":reply})
        with st.chat_message("assistant"): st.markdown(reply)

def page_index_pdf():
    st.title("🧰 Indeks PDF (manualny)")
    run_dir = _ensure_run_dir(); pdf_dir = run_dir/"pdfs"
    st.info("Możesz dorzucić / podmienić PDF-y i zbudować All_invoices.csv bez uruchamiania całego testu.")
    new_pdfs = st.file_uploader("Dodaj PDF-y", type=["pdf"], accept_multiple_files=True)
    if new_pdfs and st.button("📥 Zapisz do katalogu biegu"):
        for f in new_pdfs: _save_bytes(f, pdf_dir / f.name)
        st.success(f"Zapisano {len(new_pdfs)} plików → `{pdf_dir}`")
    if st.button("🔎 Zbuduj All_invoices.csv"):
        rc = _run([os.fspath(Path(os.sys.executable)), "pdf_indexer.py",
                   os.fspath(pdf_dir), os.fspath(run_dir/"All_invoices.csv")], cwd=REPO_ROOT,
                   label="Indeksowanie PDF (pdf_indexer.py)")
        if rc==0: st.success("All_invoices.csv gotowe."); _render_downloads(run_dir)

def page_renamer():
    st.title("✏️ Renamer (ostatni bieg)")
    last = st.session_state.get("last_run", {})
    if not last:
        st.info("Najpierw odpal **Panel testów**.")
        return
    run_dir = Path(last["dir"]); pdf_dir = run_dir/"pdfs"
    rename_dir = st.text_input("Katalog docelowy", value="renamed")
    do_apply = st.checkbox("Wykonaj realny rename (kopie)", value=False)
    if st.button("🚚 Uruchom rename na wynikach ostatniego biegu"):
        cmd = [os.fspath(Path(os.sys.executable)), "pop_matcher.py",
               "--pop", os.fspath(run_dir/"populacja.xlsx"),
               "--pdf-root", os.fspath(pdf_dir),
               "--out-jsonl", os.fspath(run_dir/"verdicts.jsonl"),
               "--out-xlsx", os.fspath(run_dir/"populacja_enriched.xlsx"),
               "--index-csv", os.fspath(run_dir/"All_invoices.csv"),
               "--rename"]
        if do_apply: cmd += ["--apply","--rename-dir", os.fspath(run_dir/rename_dir), "--attach-col","ZAŁĄCZNIK"]
        rc = _run(cmd, cwd=REPO_ROOT, label="Rename na ostatnim biegu (pop_matcher.py)")
        if rc==0:
            st.success("Rename zakończony.");
            _render_downloads(run_dir)

def page_settings():
    st.title("⚙️ Ustawienia / Motyw")
    st.write("Motyw i akcent ustawiasz w **sidebarze**. Ustawienia zapisujemy w przeglądarce i działają konsekwentnie.")

def page_help():
    st.title("❓ Pomoc")
    st.markdown("""
**Szybki start**
1. Wejdź do **Panel testów**, wgraj `populacja.xlsx` i PDF-y (możesz wskazać 30+).
2. Kliknij **Start** – po chwili zobaczysz metryki i top niezgodności.
3. Szczegóły/eksporty: **Wyniki ostatniego biegu**. Podgląd PDF: **Przegląd PDF (preview)**.
4. Niejednoznaczności: lista w **Niejednoznaczności**.

**Uwaga**: Jeżeli któryś PDF nie parsuje się tekstowo – rozważ OCR (Tesseract) poza panelem.
""")

# =============== Router ===============
if page == "Panel testów":
    page_panel_testow()
elif page == "Wyniki ostatniego biegu":
    page_wyniki()
elif page == "Przegląd PDF (preview)":
    page_pdf_preview()
elif page == "Niejednoznaczności":
    page_ambiguous()
elif page == "Chat operacyjny":
    page_chat()
elif page == "Indeks PDF (manualny)":
    page_index_pdf()
elif page == "Renamer (z ostatniego biegu)":
    page_renamer()
elif page == "Ustawienia / Motyw":
    page_settings()
else:
    page_help()
