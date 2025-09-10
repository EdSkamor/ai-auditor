import logging
import os
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from model_hf_interface import call_model
from tools.ingest import read_table

try:
    from tools.analysis import analyze_table  # opcjonalnie
except Exception:
    analyze_table = None

# --- Ustawienia (bezpieczeństwo) ---
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
ALLOW_ORIGINS = [
    o.strip() for o in os.getenv("AIAUDITOR_ALLOW_ORIGINS", "*").split(",")
]
MAX_FILE_MB = int(os.getenv("AIAUDITOR_MAX_FILE_MB", "25"))
SAVE_UPLOADS = os.getenv("AIAUDITOR_SAVE_UPLOADS", "false").lower() == "true"

app = FastAPI(title="AI Auditor Demo", version="0.4.1")
logger = logging.getLogger("aiauditor")
logging.basicConfig(level=logging.INFO)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS if ALLOW_ORIGINS != ["*"] else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Front statyczny ---
web_dir = Path(__file__).resolve().parent / "web"
web_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")


@app.get("/")
def index():
    idx = web_dir / "index.html"
    if not idx.exists():
        return JSONResponse({"error": "Brak web/index.html"}, status_code=404)
    return FileResponse(idx)


# --- API ---
class AnalyzeReq(BaseModel):
    prompt: str
    max_new_tokens: int = 160
    do_sample: bool = False
    temperature: float = 0.7
    top_p: float = 0.9


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.on_event("startup")
def _warmup():
    try:
        logger.info("Warming up model…")
        _ = call_model("ping", max_new_tokens=8, do_sample=False)
        logger.info("Model ready.")
    except Exception as e:
        logger.exception("Warmup failed: %s", e)


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
        logger.exception("Analyze error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    try:
        data = await file.read()
        if not data:
            raise ValueError("Pusty plik.")
        if len(data) > MAX_FILE_MB * 1024 * 1024:
            raise ValueError(f"Plik większy niż {MAX_FILE_MB} MB.")

        parsed = read_table(data, file.filename)  # <-- NAZWA PLIKU przekazana
        df = parsed["df"]
        info = {
            "filename": file.filename,
            "shape": parsed["shape"],
            "columns": parsed["columns"],
        }

        # opcjonalna analiza, z bezpiecznym fallbackiem
        if analyze_table is not None:
            try:
                res = analyze_table(df)
                info.update(res)
            except Exception:
                info["output"] = (
                    f"Wczytano tabelę: {parsed['shape'][0]} wierszy, {parsed['shape'][1]} kolumn."
                )
        else:
            info["output"] = (
                f"Wczytano tabelę: {parsed['shape'][0]} wierszy, {parsed['shape'][1]} kolumn."
            )

        return JSONResponse(info)
    except Exception as e:
        logger.exception("analyze-file error: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
