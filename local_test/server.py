import logging
import os
import secrets
import threading
from pathlib import Path

import pandas as pd
import requests
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .core.data_processing import analyze_table, read_table
from .core.exceptions import AuditorException
from .core.model_interface import _provider as _model_provider
from .core.model_interface import call_model

# --- Konfiguracja ---
ALLOW_ORIGINS = [
    o.strip() for o in os.getenv("AIAUDITOR_ALLOW_ORIGINS", "*").split(",")
]
ADMIN_PASSWORD = os.getenv("AIAUDITOR_PASSWORD", "TwojPIN123!")

# Security
security = HTTPBasic()


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Autentykacja użytkownika."""
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowe hasło",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


MAX_FILE_MB = int(os.getenv("AIAUDITOR_MAX_FILE_MB", "100"))
SAVE_UPLOADS = os.getenv("AIAUDITOR_SAVE_UPLOADS", "false").lower() == "true"
DEBUG = os.getenv("AIAUDITOR_DEBUG", "false").lower() == "true"
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
    """Warm only if heavy provider; skip for mock/ollama."""
    global MODEL_READY
    prov = _model_provider()
    if prov in ("mock", "ollama"):
        MODEL_READY = True
        logger.info("Model ready (no-warmup for %s).", prov)
        return
    try:
        logger.info("Warming up model in background…")
        _ = call_model(
            "Krótki test startowy audytu.", max_new_tokens=8, do_sample=False
        )
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
    prov = _model_provider()
    if prov == "mock":
        return JSONResponse(
            content=jsonable_encoder({"model_ready": True, "provider": prov})
        )
    if prov == "ollama":
        try:
            base = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
            r = requests.get(f"{base}/api/tags", timeout=3)
            return JSONResponse(
                content=jsonable_encoder(
                    {"model_ready": r.ok, "provider": prov, "ollama": r.status_code}
                )
            )
        except Exception:
            return JSONResponse(
                content=jsonable_encoder({"model_ready": False, "provider": prov})
            )
    return JSONResponse(
        content=jsonable_encoder({"model_ready": MODEL_READY, "provider": prov})
    )


@app.post("/analyze")
def analyze(req: AnalyzeReq, current_user: str = Depends(get_current_user)):
    if not MODEL_READY:
        return JSONResponse(
            content=jsonable_encoder(
                {"error": "Model się dogrzewa. Spróbuj za chwilę."}
            ),
            status_code=503,
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
async def analyze_file(
    file: UploadFile = File(...), current_user: str = Depends(get_current_user)
):
    # File size limit
    if file.size and file.size > MAX_FILE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")

    try:
        content = await file.read()
        data = read_table(content, file.filename)
        df = data.get("df")

        if not isinstance(df, pd.DataFrame):
            raise ValueError("read_table did not return DataFrame in 'df' key")

        # Perform analysis
        analysis = analyze_table(df)

        # Sample data (JSON-safe)
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
            "analysis": analysis,
            "prompts": data.get("prompts", []),
            "sample": sample,
            "saved_to": None,  # Don't save uploads by default
        }
        return JSONResponse(content=jsonable_encoder(payload))

    except AuditorException as e:
        logger.error(f"Auditor error in analyze-file: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("analyze-file error")
        raise HTTPException(status_code=500, detail=str(e))
