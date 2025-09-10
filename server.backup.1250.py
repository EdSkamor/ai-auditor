import logging
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from model_hf_interface import call_model
from tools.analysis import analyze_table
from tools.ingest import read_table

# --- Ustawienia (możesz nadpisać zmiennymi środowiskowymi/systemd) ---
ALLOW_ORIGINS = [
    o.strip() for o in os.getenv("AIAUDITOR_ALLOW_ORIGINS", "*").split(",")
]  # w prod ustaw np. "https://izaufani.pl"
MAX_FILE_MB = int(os.getenv("AIAUDITOR_MAX_FILE_MB", "25"))
SAVE_UPLOADS = os.getenv("AIAUDITOR_SAVE_UPLOADS", "false").lower() == "true"
DEBUG = os.getenv("AIAUDITOR_DEBUG", "false").lower() == "true"

os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

app = FastAPI(title="AI Auditor Demo", version="0.4.0")
logger = logging.getLogger("aiauditor")
logging.basicConfig(level=logging.INFO if not DEBUG else logging.DEBUG)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS if ALLOW_ORIGINS != ["*"] else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Modele żądań ---
class AnalyzeReq(BaseModel):
    prompt: str
    max_new_tokens: int = 220
    do_sample: bool = False
    temperature: float = 0.7
    top_p: float = 0.9


# --- Statyczny frontend ---
web_dir = (Path(__file__).parent / "web").resolve()
web_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")


@app.get("/")
def index():
    idx = web_dir / "index.html"
    if not idx.exists():
        return JSONResponse({"error": "Brak web/index.html"}, status_code=404)
    return FileResponse(idx)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


# --- Warmup modelu na starcie ---
@app.on_event("startup")
def _warmup():
    try:
        logger.info("Warming up model…")
        _ = call_model("ping", max_new_tokens=8, do_sample=False)
        logger.info("Model ready.")
    except Exception:
        logger.exception("Warmup failed")


# --- Tekstowe analizy ---
@app.post("/analyze")
def analyze(req: AnalyzeReq):
    try:
        # nie logujemy pełnej treści promptu (PII) – tylko długość
        logger.info("Analyze called (prompt_len=%d)", len(req.prompt or ""))
        out = call_model(
            req.prompt,
            max_new_tokens=req.max_new_tokens,
            do_sample=req.do_sample,
            temperature=req.temperature,
            top_p=req.top_p,
        )
        return {"output": out}
    except Exception as e:
        logger.exception("/analyze failed")
        raise HTTPException(status_code=500, detail=str(e))


# --- Upload pliku (CSV/XLSX) + analiza ---
ALLOWED_EXT = {".csv", ".tsv", ".xlsx", ".xls"}


@app.post("/analyze-file")
async def analyze_file(
    file: UploadFile = File(...), prompt: Optional[str] = Form(None)
):
    try:
        fname = (file.filename or "").strip()
        suffix = Path(fname).suffix.lower()

        if suffix not in ALLOWED_EXT:
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"Niedozwolone rozszerzenie: {suffix}. Dozwolone: {sorted(ALLOWED_EXT)}"
                },
            )

        # zapis tymczasowy (domyślnie NIE trwale)
        tmp_dir = Path("data/processed/tmp")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(delete=False, dir=tmp_dir, suffix=suffix) as tmp:
            total = 0
            while True:
                chunk = await file.read(1024 * 1024)  # 1MB
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_FILE_MB * 1024 * 1024:
                    raise ValueError(f"Plik przekracza limit {MAX_FILE_MB} MB")
                tmp.write(chunk)
            tmp_path = Path(tmp.name)

        df = read_table(tmp_path)
        result = analyze_table(df)

        # Opcjonalny prompt do modelu – budujemy krótkie podsumowanie z metryk
        summary = result.get("output_md", "")
        if prompt:
            prompt2 = (
                f"{prompt}\n\nKontekst (metryki wyliczone z tabeli):\n{summary[:2000]}"
            )
            model_output = call_model(prompt2, max_new_tokens=200, do_sample=False)
        else:
            model_output = summary

        # sprzątanie – jeśli nie chcemy trwałego zapisu
        if not SAVE_UPLOADS:
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                logger.warning("Nie udało się usunąć pliku tymczasowego: %s", tmp_path)

        return {"metrics": result.get("metrics", {}), "output": model_output}

    except Exception as e:
        logger.exception("/analyze-file failed")
        return JSONResponse(status_code=400, content={"error": str(e)})
