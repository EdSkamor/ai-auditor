import logging
import os
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.encoders import JSONResponse, jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from model_hf_interface import call_model
from tools.analysis import analyze_table
from tools.ingest import read_table

ALLOW_ORIGINS = [o.strip() for o in os.getenv("AIAUDITOR_ALLOW_ORIGINS", "*").split(",")]
MAX_FILE_MB   = int(os.getenv("AIAUDITOR_MAX_FILE_MB", "25"))
DEBUG         = os.getenv("AIAUDITOR_DEBUG", "false").lower() == "true"

os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

app = FastAPI(title="AI Auditor Demo", version="0.4.4")
logger = logging.getLogger("aiauditor")
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if ALLOW_ORIGINS == ["*"] else ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

web_dir = Path(__file__).resolve().parent / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

class AnalyzeReq(BaseModel):
    prompt: str
    max_new_tokens: int = 220
    do_sample: bool = False
    temperature: float = 0.7
    top_p: float = 0.9

@app.get("/")
def index():
    if not web_dir.exists():
        from fastapi.encoders import jsonable_encoder
return JSONResponse(content=jsonable_encoder({"status":"ok","note":"Brak katalogu web/"}))
    return FileResponse(web_dir / "index.html")

@app.get("/healthz")
def healthz():
    from fastapi.encoders import jsonable_encoder
return JSONResponse(content=jsonable_encoder({"status":"ok"}))

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
        from fastapi.encoders import jsonable_encoder
return JSONResponse(content=jsonable_encoder({"output": out}))
    except Exception as e:
        logger.exception("analyze error")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-file")
def analyze_file(file: UploadFile = File(...)):
    try:
        data = file.file.read()
        if len(data) > MAX_FILE_MB * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Plik za duży")

        parsed = read_table(data, file.filename)
        df = parsed["df"]
        sample = df.head(10).fillna("").to_dict(orient="records")
        analysis = analyze_table(df)
        metrics = {"rows": int(df.shape[0]), "cols": int(df.shape[1])}
        if analysis.get("amount_sum") is not None:
            metrics["amount_sum"] = analysis["amount_sum"]
            metrics["amount_mean"] = analysis.get("amount_mean")

        return JSONResponse(content=jsonable_encoder({
            "filename": file.filename,
            "shape": [int(df.shape[0]), int(df.shape[1])],
            "columns": list(df.columns),
            "metrics": metrics,
            "prompts": parsed.get("prompts", []),
            "analysis": analysis,
            "sample": sample,
            "saved_to": None
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("analyze-file error")
        raise HTTPException(status_code=400, detail=str(e))
