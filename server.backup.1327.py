import os
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
import pandas as pd

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from model_hf_interface import call_model
from tools.ingest import read_table

# --- Ustawienia (możesz nadpisać przez ENV/systemd) ---
ALLOW_ORIGINS = [o.strip() for o in os.getenv("AIAUDITOR_ALLOW_ORIGINS", "*").split(",")]
MAX_FILE_MB   = int(os.getenv("AIAUDITOR_MAX_FILE_MB", "25"))
SAVE_UPLOADS  = os.getenv("AIAUDITOR_SAVE_UPLOADS", "false").lower() == "true"
DEBUG         = os.getenv("AIAUDITOR_DEBUG", "false").lower() == "true"

os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

app = FastAPI(title="AI Auditor Demo", version="0.4.2")
logger = logging.getLogger("aiauditor")
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if ALLOW_ORIGINS == ["*"] else ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Statyczny frontend ---
web_dir = Path(__file__).resolve().parent / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

class AnalyzeReq(BaseModel):
    prompt: str
    max_new_tokens: int = 220
    do_sample: bool = False
    temperature: float = 0.7
    top_p: float = 0.9

@app.on_event("startup")
async def _warmup():
    try:
        logger.info("Warming up model…")
        _ = call_model("ping", max_new_tokens=8, do_sample=False)
        logger.info("Model ready.")
    except Exception as e:
        logger.exception("Warmup failed: %s", e)

@app.get("/")
def root():
    idx = web_dir / "index.html"
    if idx.exists():
        return FileResponse(idx)
    return {"status": "ok"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/analyze")
def analyze(req: AnalyzeReq):
    try:
        out = call_model(
            req.prompt,
            max_new_tokens=req.max_new_tokens,
            do_sample=req.do_sample,
            temperature=req.temperature,
            top_p=req.top_p,
        )
        return {"output": out}
    except Exception as e:
        logger.exception("inference error: %s", e)
        raise HTTPException(500, "inference error")

@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    try:
        if file is None:
            raise HTTPException(400, "file required")
        size = getattr(file, "size", None)
        if size and size > MAX_FILE_MB * 1024 * 1024:
            raise HTTPException(413, f"file too large > {MAX_FILE_MB} MB")

        content = await file.read()
        report = read_table(content, file.filename)  # -> {"df","columns","shape"}
        df: pd.DataFrame = report["df"]
        cols = report["columns"]
        shape = report["shape"]

        # Heurystyka kolumny kwotowej
        preferred = ["wartosc_netto_dokumentu","wartosc_brutto","kwota_brutto","kwota_netto","kwota_vat"]
        amount_col = next((c for c in preferred if c in cols), None)
        if amount_col is None:
            candidates = [c for c in cols if any(k in c for k in ["kwota","wartosc","amount","netto","brutto","vat"])]
            amount_col = candidates[0] if candidates else None

        metrics = {"rows": int(shape[0]), "cols": int(shape[1])}
        if amount_col and amount_col in df.columns:
            ser = pd.to_numeric(df[amount_col].astype(str).str.replace(",", "."), errors="coerce")
            metrics.update(
                amount_column=amount_col,
                amount_sum=float(ser.sum(skipna=True)),
                amount_mean=float(ser.mean(skipna=True)),
            )

        sample = df.head(10).fillna("").astype(str).to_dict(orient="records")

        saved_to = None
        if SAVE_UPLOADS:
            with NamedTemporaryFile(prefix="upload_", suffix=f"-{file.filename}", delete=False) as tmp:
                tmp.write(content)
                saved_to = tmp.name

        return {
            "filename": file.filename,
            "shape": shape,
            "columns": cols,
            "metrics": metrics,
            "sample": sample,
            "saved_to": saved_to,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("analyze-file failed: %s", e)
        raise HTTPException(400, "cannot parse file")
