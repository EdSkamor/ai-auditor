from __future__ import annotations
import os, re, json, shutil, subprocess, tempfile
from dateutil.parser import parse as date_parse
from llama_cpp import Llama
import pdfplumber

MODEL = os.environ.get("LLAMA_MODEL", "/home/romaks/models/llama3/meta-llama-3-8b-instruct.Q4_K_M.gguf")
LLM = Llama(model_path=MODEL, n_gpu_layers=-1, n_ctx=8192, n_batch=1024, verbose=False)

SYS = "Ekstrahuj z tekstu faktury pola wg schematu. Zwróć TYLKO czysty JSON."
USR_TMPL = """Tekst faktury:
---
{body}
---
Zwróć JSON o kluczach: invoice_id, issue_date (YYYY-MM-DD), seller_name, buyer_name, currency, total_net, total_vat, total_gross, vat_rate, po_number.
Jeśli czegoś brak, ustaw null. Bez komentarzy i dodatkowego tekstu."""

def _read_pdf_text(path:str)->str:
    text_parts=[]
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            if not txt.strip() and shutil.which("tesseract"):
                img = page.to_image(resolution=300).original
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                    img.save(f.name)
                    have_pol = os.system("tesseract --list-langs 2>/dev/null | grep -qi '^pol$'")==0
                    lang = "pol" if have_pol else "eng"
                    res = subprocess.run(["tesseract", f.name, "stdout", "-l", lang], capture_output=True, text=True)
                    txt = res.stdout
                    os.unlink(f.name)
            text_parts.append(txt)
    return "\n".join(text_parts)

def _coerce_date(s):
    if not s: return None
    try:
        return date_parse(str(s), dayfirst=True).date().isoformat()
    except Exception:
        return None

def _to_float(x):
    if x is None: return None
    s = str(x).replace("\xa0","").replace(" ","").replace(",", ".")
    m = re.findall(r"[-+]?\d+(?:\.\d+)?", s)
    try:
        return float(m[-1]) if m else None
    except Exception:
        return None

def _guess_currency(body:str)->str|None:
    bU = body.upper()
    if "PLN" in bU or " ZŁ" in bU or " ZL" in bU: return "PLN"
    if "EUR" in bU or "€" in body: return "EUR"
    if "USD" in bU or "$" in body: return "USD"
    return None

def _parse_json_loose(txt:str)->dict:
    try:
        return json.loads(txt)
    except Exception:
        pass
    if "{" in txt and "}" in txt:
        frag = txt[txt.find("{"): txt.rfind("}")+1]
        return json.loads(frag)
    raise ValueError("Nie udało się sparsować JSON z odpowiedzi LLM")

def _fallback_po_number(body:str)->str|None:
    m = re.search(r"(?:PO|Order|Zamówienie)\s*[:#]?\s*([A-Z0-9\-_/]{4,})", body, re.IGNORECASE)
    return m.group(1) if m else None

def llm_extract(body:str)->dict:
    body_clip = body[:4000]
    resp = LLM.create_chat_completion(
        messages=[{"role":"system","content":SYS},
                  {"role":"user","content":USR_TMPL.format(body=body_clip)}],
        temperature=0.2, max_tokens=512)
    raw = resp["choices"][0]["message"]["content"]
    data = _parse_json_loose(raw)

    data["issue_date"] = _coerce_date(data.get("issue_date"))
    for k in ["total_net","total_vat","total_gross","vat_rate"]:
        data[k] = _to_float(data.get(k))
    if not data.get("currency"):
        data["currency"] = _guess_currency(body)
    if not data.get("po_number"):
        data["po_number"] = _fallback_po_number(body)
    return data

def extract_invoice(path:str)->dict:
    body = _read_pdf_text(path)
    out = llm_extract(body)
    out["source_path"] = path
    out["source_filename"] = os.path.basename(path)
    return out

if __name__ == "__main__":
    import sys
    p = sys.argv[1]
    print(json.dumps(extract_invoice(p), ensure_ascii=False, indent=2))
