import os, json
from pathlib import Path
from PIL import Image
import torch, pdfplumber
from transformers import DonutProcessor, VisionEncoderDecoderModel

MODEL_DIR = os.environ.get("DONUT_MODEL","naver-clova-ix/donut-base")
USE_DONUT = os.environ.get("USE_DONUT", "1") not in ("0","false","False","no")

_PROC = None
_MODEL = None

def _load():
    global _PROC, _MODEL
    if not USE_DONUT:
        return None, None
    if _PROC is None:
        _PROC = DonutProcessor.from_pretrained(MODEL_DIR)
    if _MODEL is None:
        _MODEL = VisionEncoderDecoderModel.from_pretrained(MODEL_DIR)
        _MODEL.eval().to("cuda" if torch.cuda.is_available() else "cpu")
    return _PROC, _MODEL

def _pdf_first_page_image(path:str)->Image.Image:
    with pdfplumber.open(path) as pdf:
        pil = pdf.pages[0].to_image(resolution=220).original
    return pil.convert("RGB") if pil.mode!="RGB" else pil

def _pdf_all_text(path:str)->str:
    acc=[]
    try:
        with pdfplumber.open(path) as pdf:
            for pg in pdf.pages:
                txt = pg.extract_text(x_tolerance=2, y_tolerance=2) or ""
                acc.append(txt)
    except Exception:
        pass
    return "\n".join(acc)

def extract_fields(path:str)->dict:
    path = str(Path(path))
    pdf_text = _pdf_all_text(path)

    donut_json = {}
    donut_text = ""
    proc, model = _load()
    if proc is not None and model is not None:
        try:
            img = _pdf_first_page_image(path)
            px = proc(img, return_tensors="pt").pixel_values.to(model.device)
            with torch.no_grad():
                out = model.generate(px, max_new_tokens=512, do_sample=False)
            donut_text = proc.batch_decode(out, skip_special_tokens=True)[0].strip()
            try:
                donut_json = json.loads(donut_text)
            except Exception:
                donut_json = {}
        except Exception:
            donut_json = {}
            donut_text = ""

    combined_text = (donut_text + "\n" + pdf_text).strip()
    return {"json": donut_json, "text": combined_text}
