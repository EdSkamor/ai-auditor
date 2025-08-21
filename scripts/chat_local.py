
import os, sys, re, textwrap, pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict
try:
    import pdfplumber
except Exception:
    pdfplumber = None
from llama_cpp import Llama

# ---- KONFIG ----
MODEL=os.environ.get("LLM_GGUF","")
if not MODEL or not Path(MODEL).is_file():
    sys.exit(f"❌ Ustaw LLM_GGUF na plik .gguf (brak: {MODEL or '<pusta>'})")

CTX=int(os.environ.get("LLM_CTX","8192"))
THREADS=int(os.environ.get("LLM_THREADS", str(os.cpu_count() or 4)))
GPU_LAYERS=int(os.environ.get("LLM_GPU_LAYERS","0"))
TEMP=float(os.environ.get("LLM_TEMP","0.3"))
TOP_P=float(os.environ.get("LLM_TOP_P","0.9"))
MAX_TOK=int(os.environ.get("LLM_MAX_TOK","1024"))

prompt_path=Path("prompts/audytor_system.txt")
SYSTEM = prompt_path.read_text(encoding="utf-8") if prompt_path.is_file() else "Jesteś pomocnym audytorem."

# ---- LLM ----
print(f"🧠 model: {MODEL}\n🧵 threads={THREADS} ctx={CTX} gpu_layers={GPU_LAYERS}\n", file=sys.stderr)
llm = Llama(model_path=MODEL, n_ctx=CTX, n_threads=THREADS, n_gpu_layers=GPU_LAYERS, chat_format="llama-3", verbose=False)
messages: List[Dict[str,str]] = [{"role":"system","content": SYSTEM}]

# ---- PAMIĘĆ TABEL / PLIKI ----
loaded_tables: list[pd.DataFrame] = []
loaded_names: list[str] = []
DOC_ROOTS = [Path("data")]

def add_doc(name: str, text: str, role="system", cap=6000):
    text = textwrap.shorten(" ".join(text.split()), width=cap, placeholder=" …")
    messages.append({"role": role, "content": f"Załączony dokument: {name}\n\n{text}"})

def _normcols(df: pd.DataFrame)->pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df

def _read_xlsx(p: Path)->list[tuple[str,pd.DataFrame]]:
    out=[]
    xls=pd.ExcelFile(p)
    for sh in xls.sheet_names:
        try:
            df=pd.read_excel(xls, sheet_name=sh)
            df=_normcols(df)
            out.append((f"{p.name}:{sh}", df))
        except Exception as e:
            out.append((f"{p.name}:{sh}", pd.DataFrame({"_error":[str(e)]})))
    return out

def _read_csv(p: Path)->pd.DataFrame:
    return _normcols(pd.read_csv(p))

def _summarize_df(df: pd.DataFrame, title="Tabela"):
    head = df.head(6).to_markdown(index=False)
    info = f"Wierszy: {len(df)}, Kolumn: {len(df.columns)}"
    nums = df.select_dtypes("number")
    sums = ""
    if not nums.empty:
        sums = "\nSuma kolumn numerycznych (top 6):\n" + nums.sum().sort_values(ascending=False).head(6).round(2).to_string()
    return f"### {title}\n{info}\nPodgląd:\n{head}\n{sums}"

def _auto_data_note():
    parts=[]
    for nm, df in zip(loaded_names, loaded_tables):
        parts.append(_summarize_df(df, title=nm))
    return "\n\n".join(parts)

def _calc_totals()->dict:
    tot = {"netto":0.0,"vat":0.0,"brutto":0.0}
    for df in loaded_tables:
        for k in list(tot.keys()):
            if k in df.columns:
                tot[k]+=pd.to_numeric(df[k], errors="coerce").fillna(0).sum()
    return {k: round(float(v),2) for k,v in tot.items()}

def _top_counterpart(n=3, by="brutto")->pd.DataFrame|None:
    key_by = by.lower()
    key_cnt = None
    # szukamy kolumny na kontrahenta
    for cand in ["kontrahent","kontrahenci","sprzedawca","dostawca","nabywca","odbiorca","kontrahent_nazwa","kontrahent__nazwa"]:
        for df in loaded_tables:
            if cand in df.columns:
                key_cnt = cand; break
        if key_cnt: break
    if not key_cnt: return None
    frames=[]
    for df in loaded_tables:
        if key_by in df.columns and key_cnt in df.columns:
            grp = df.groupby(key_cnt, dropna=False)[key_by].sum().reset_index()
            frames.append(grp)
    if not frames: return None
    allg = pd.concat(frames).groupby(key_cnt, dropna=False)[key_by].sum().reset_index()
    allg = allg.sort_values(by=key_by, ascending=False).head(n)
    allg[key_by]=allg[key_by].round(2)
    return allg

def _find_pdf(query: str)->Path|None:
    # jeśli podano pełną ścieżkę/istnieje
    p=Path(query)
    if p.is_file(): return p
    name = Path(query).name.lower()
    for root in DOC_ROOTS:
        for rp in root.rglob("*.pdf"):
            if rp.name.lower()==name:
                return rp
    # fallback: substring
    for root in DOC_ROOTS:
        for rp in root.rglob("*.pdf"):
            if name in rp.name.lower():
                return rp
    return None

def load_pdf(p: Path)->str:
    if not pdfplumber:
        return "(pdfplumber nie zainstalowany – pip install pdfplumber)"
    out=[]
    with pdfplumber.open(str(p)) as pdf:
        for i,page in enumerate(pdf.pages, start=1):
            if i>5: break
            t = page.extract_text() or ""
            if t.strip(): out.append(f"[p.{i}]\n{t}\n")
    return "\n".join(out) if out else "(Brak możliwego do wyodrębnienia tekstu)"

def save_transcript():
    Path("logs").mkdir(parents=True, exist_ok=True)
    ts=datetime.now().strftime("%Y%m%d_%H%M")
    out=Path(f"logs/chat_{ts}.md")
    with out.open("w", encoding="utf-8") as f:
        for m in messages:
            role=m["role"]; content=m["content"]
            f.write(f"\n**{role.upper()}**\n\n{content}\n")
    print(f"📝 zapisano transkrypt: {out}", file=sys.stderr)

HELP = """Komendy:
/xlsx PATH         – dołącz arkusz (czyta wszystkie zakładki)
/csv PATH          – dołącz CSV
/pdf PATH|NAZWA    – sprytnie wyszuka PDF w ./data, do 5 stron tekstu
/summary           – policz dokładne sumy: netto/VAT/brutto (z Pandas)
/top [kol] [N]     – top-N kontrahentów wg kolumny (domyślnie brutto, N=3)
/reset             – wyczyść rozmowę (zostaje persona)
/exit              – wyjście
/help              – pomoc

Wskazówka: po /xlsx możesz po prostu zapytać „Policz sumaryczny VAT i top-3…”
Chat automatycznie dołączy wyliczenia do kontekstu, żeby liczby były pewne.
"""

def chat_once(user_text: str):
    # AUTO-DANE: jeżeli mamy tabele, dołącz krótki opis, a gdy pytasz o VAT/top-N – dołóż wyliczenia
    note = ""
    if loaded_tables:
        note = _auto_data_note()
        # heurystyki
        lower = user_text.lower()
        extras=[]
        if "sumaryczny vat" in lower or "suma vat" in lower:
            t=_calc_totals(); extras.append(f"Suma (dokładnie): netto={t['netto']}, vat={t['vat']}, brutto={t['brutto']}.")
        if "top-3" in lower or "top 3" in lower or "top3" in lower or "top kontrahent" in lower:
            top=_top_counterpart(n=3, by="brutto")
            if top is not None:
                extras.append("Top-3 kontrahentów wg brutto (dokładnie):\n"+top.to_markdown(index=False))
        if extras:
            note = note + "\n\n[WYLICZENIA KONTROLNE]\n" + "\n".join(extras)

    if note:
        messages.append({"role":"system","content": f"Dane referencyjne do odpowiedzi:\n\n{note}"})
    messages.append({"role":"user","content": user_text})

    stream = llm.create_chat_completion(messages=messages, temperature=TEMP, top_p=TOP_P, max_tokens=MAX_TOK, stream=True)
    print("AI:", end=" ", flush=True)
    full=[]
    for chunk in stream:
        delta = ""
        try:
            delta = chunk["choices"][0].get("delta",{}).get("content","")
        except Exception:
            delta = chunk["choices"][0]["message"]["content"]
        if delta:
            full.append(delta); print(delta, end="", flush=True)
    print()
    messages.append({"role":"assistant","content":"".join(full)})

print(HELP)

while True:
    try:
        user = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        save_transcript(); print(); break
    if not user: continue
    if user.startswith("/"):
        cmd, *rest = user.split(maxsplit=2)
        arg = (rest[0] if rest else "").strip().strip('"').strip("'")
        if cmd in ("/exit","/quit"): save_transcript(); break
        if cmd == "/help": print(HELP); continue
        if cmd == "/reset":
            messages[:] = [{"role":"system","content": SYSTEM}]
            loaded_tables.clear(); loaded_names.clear()
            print("✅ zresetowano konwersację"); continue
        if cmd == "/xlsx":
            p=Path(arg)
            if not p.is_file(): print(f"❌ brak pliku: {p}"); continue
            parts=_read_xlsx(p)
            for name,df in parts:
                loaded_tables.append(df); loaded_names.append(name)
                add_doc(name, _summarize_df(df, title=name))
            print(f"✅ dołączono arkusz: {p}"); continue
        if cmd == "/csv":
            p=Path(arg)
            if not p.is_file(): print(f"❌ brak pliku: {p}"); continue
            df=_read_csv(p)
            loaded_tables.append(df); loaded_names.append(p.name)
            add_doc(p.name, _summarize_df(df, title=p.name)); print(f"✅ dołączono CSV: {p}"); continue
        if cmd == "/pdf":
            tgt = _find_pdf(arg) if arg else None
            if not tgt: print(f"❌ nie znaleziono PDF dla: {arg}"); continue
            text = load_pdf(tgt)
            add_doc(tgt.name, text); print(f"✅ dołączono PDF: {tgt}"); continue
        if cmd == "/summary":
            if not loaded_tables: print("ℹ️ najpierw /xlsx lub /csv"); continue
            t=_calc_totals()
            print(f"Suma (dokładna): netto={t['netto']}  vat={t['vat']}  brutto={t['brutto']}"); continue
        if cmd == "/top":
            by = "brutto"; n=3
            if rest:
                parts = rest[0].split()
                if parts: by = parts[0].lower()
                if len(parts)>1 and parts[1].isdigit(): n=int(parts[1])
            top=_top_counterpart(n=n, by=by)
            if top is None: print("ℹ️ brak kolumny kontrahent/* lub kolumny miary."); continue
            print(top.to_markdown(index=False)); continue
        print("❓ nieznana komenda – /help"); continue

    # zwykła wiadomość → LLM
    chat_once(user)
