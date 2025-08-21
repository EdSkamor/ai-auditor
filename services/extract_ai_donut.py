import os
from pathlib import Path

import torch
import pdfplumber
import pypdfium2 as pdfium
from PIL import Image
from transformers import DonutProcessor, VisionEncoderDecoderModel

USE_DONUT = os.environ.get("USE_DONUT", "1").lower() not in ("0","false","no")

def _resolve_model_dir() -> str:
    base = "naver-clova-ix/donut-base"
    env  = os.environ.get("DONUT_MODEL", base)
    p = Path(env)
    if p.is_dir():
        files = {f.name for f in p.iterdir()} if p.exists() else set()
        needed_any = {"config.json","model.safetensors","pytorch_model.bin","preprocessor_config.json","tokenizer.json"}
        if files & needed_any:
            return str(p)
    return env  # pozwól też na HF repo id

_PROC = None
_MODEL = None
_DEVICE = None
_DTYPE = None

def _pdf_to_pil(path: str, page_index: int = 0, scale: float = 2.0) -> Image.Image:
    pdf = pdfium.PdfDocument(path)
    try:
        page = pdf.get_page(page_index)
        try:
            bitmap = page.render(scale=scale)
            img = bitmap.to_pil()
            return img.convert("RGB")
        finally:
            page.close()
    finally:
        pdf.close()

def _load():
    global _PROC, _MODEL, _DEVICE, _DTYPE
    if _PROC is not None and _MODEL is not None:
        return _PROC, _MODEL

    model_dir = _resolve_model_dir()
    _DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    if _DEVICE == "cuda":
        cap = torch.cuda.get_device_capability(0)[0]
        _DTYPE = torch.bfloat16 if cap >= 8 else torch.float16
    else:
        _DTYPE = torch.float32

    _PROC = DonutProcessor.from_pretrained(model_dir)
    _MODEL = VisionEncoderDecoderModel.from_pretrained(
        model_dir,
        torch_dtype=_DTYPE if _DEVICE == "cuda" else None,
    ).eval().to(_DEVICE)

    return _PROC, _MODEL

def extract_fields(pdf_path: str):
    """
    Zwraca minimalny payload do compare_row: {"text": "..."}
    - OCR z Donuta na 1. stronie PDF (szybko)
    - fallback: doklejony tekst z pdfplumber (jeśli dostępny)
    """
    # Tekst z PDF (wektorowy) – zawsze jako uzupełnienie
    pdf_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pdf_text = "\n".join(filter(None, (pg.extract_text() or "" for pg in pdf.pages)))
    except Exception:
        pass

    if not USE_DONUT:
        return {"text": (pdf_text or "").strip()}

    proc, model = _load()
    img = _pdf_to_pil(pdf_path, page_index=0, scale=2.0)
    inputs = proc(images=img, return_tensors="pt")
    pixel_values = inputs.pixel_values.to(_DEVICE)

    with torch.inference_mode():
        if _DEVICE == "cuda":
            with torch.autocast("cuda", dtype=_DTYPE):
                out_ids = model.generate(pixel_values, max_new_tokens=256, do_sample=False)
        else:
            out_ids = model.generate(pixel_values, max_new_tokens=256, do_sample=False)

    text = proc.batch_decode(out_ids, skip_special_tokens=True)[0]
    full = (text + ("\n" + pdf_text if pdf_text else "")).strip()
    return {"text": full}
