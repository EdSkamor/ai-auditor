import os
import logging
import threading
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from model_hf_interface import call_model
from tools.ingest import read_table

# --- Konfiguracja ---
ALLOW_ORIGINS = [o.strip() for o in os.getenv("AIAUDITOR_ALLOW_ORIGINS", "*").split(",")]
MAX_FILE_MB   = int(os.getenv("AIAUDITOR_MAX_FILE_MB", "25"))
SAVE_UPLOADS  = os.getenv("AIAUDITOR_SAVE_UPLOADS", "false").lower() == "true"
DEBUG         = os.getenv("AIAUDITOR_DEBUG", "false").lower() == "true"
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

logger = logging.getLogger("aiauditor")
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)

app = FastAPI(title="AI Auditor Demo", version="0.5.0")

# statyki
web_dir = Path(__file__).resolve().parent / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if ALLOW_ORIGINS == ["*"] else ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Warm-up modelu w tle ---
MODEL_READY = False
def _warmup():
    global MODEL_READY
    try:
        logger.info("Warming up model in background…")
        _ = call_model("Krótki test startowy audytu.", max_new_tokens=8, do_sample=False)
        MODEL_READY = True
        logger.info("Model ready.")
    except Exception as e:
        logger.exception("Warm-up failed: %s", e)

@app.on_event("startup")
def _on_startup():
    th = threading.Thread(target=_warmup, name="warmup", daemon=True)
    th.start()

# --- Schematy ---
class AnalyzeReq(BaseModel):
    prompt: str
    max_new_tokens: int = 220
    do_sample: bool = False
    temperature: float = 0.7
    top_p: float = 0.9

# --- Endpoints ---
@app.get("/healthz")
def healthz():
    # podstawowe 'żyję' – bez czekania na model
    return JSONResponse(content=jsonable_encoder({"status": "ok"}))

@app.get("/")
def index():
    if web_dir.exists() and (web_dir / "index.html").exists():
        return FileResponse(web_dir / "index.html")
    return JSONResponse(content=jsonable_encoder({"status": "ok", "ui": False}))

@app.get("/ready")
def ready():
    return JSONResponse(content=jsonable_encoder({"model_ready": MODEL_READY}))

@app.post("/analyze")
def analyze(req: AnalyzeReq):
    if not MODEL_READY:
        return JSONResponse(
            content=jsonable_encoder({"error": "Model się dogrzewa. Spróbuj za chwilę."}),
            status_code=503
        )
    try:
        out = call_model(
            req.prompt,
            max_new_tokens=req.max_new_tokens,
            do_sample=req.do_sample,
            temperature=req.temperature,
            top_p=req.top_p,
        )
        return JSONResponse(content=jsonable_encoder({"output": out}))
    except Exception as e:
        logger.exception("analyze error")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    # limit rozmiaru
    if file.size and file.size > MAX_FILE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Plik zbyt duży")

    try:
        content = await file.read()
        data = read_table(content, file.filename)  # spodziewamy się dict z 'df' + meta
        df = data.get("df")
        if not isinstance(df, pd.DataFrame):
            raise ValueError("read_table nie zwrócił DataFrame w kluczu 'df'")

        # sample + metryki (JSON-safe)
        sample = df.head(10).astype(str).to_dict(orient="records")
        metrics = {
            "rows": int(df.shape[0]),
            "cols": int(df.shape[1]),
        }

        payload = {
            "filename": file.filename,
            "shape": [int(df.shape[0]), int(df.shape[1])],
            "columns": list(map(str, df.columns)),
            "metrics": metrics,
            "prompts": data.get("prompts", []),
            "sample": sample,
            "saved_to": None,  # nie zapisujemy uploadów domyślnie
        }
        return JSONResponse(content=jsonable_encoder(payload))
    except Exception as e:
        logger.exception("analyze-file error")
        raise HTTPException(status_code=400, detail=str(e))
