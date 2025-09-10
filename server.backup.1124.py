import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from model_hf_interface import call_model
from tools.analysis import analyze_table
from tools.ingest import read_table

os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
app = FastAPI(title="AI Auditor Demo", version="0.3.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


class AnalyzeReq(BaseModel):
    prompt: str
    max_new_tokens: int = 200
    do_sample: bool = False
    temperature: float = 0.2
    top_p: float = 0.9


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
        raise HTTPException(500, f"model error: {e}")


@app.post("/analyze-file")
async def analyze_file(
    file: UploadFile = File(...), prompt: Optional[str] = Form(None)
):
    try:
        # zapisz tymczasowo
        tmp_dir = Path("data/processed")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = tmp_dir / file.filename
        with open(tmp_path, "wb") as f:
            f.write(await file.read())

        # ingest + analiza
        res = read_table(tmp_path)
        df = res["df"]
        ana = analyze_table(df)

        # jeśli jest prompt – dołącz krótką odpowiedź modelu na bazie metryk
        model_out = None
        if prompt:
            context = f"METRYKI: {ana.get('metrics', {})}\n\nZADANIE: {prompt}"
            model_out = call_model(context, max_new_tokens=200, do_sample=False)

        return {
            "file": file.filename,
            "metrics": ana["metrics"],
            "output_md": ana["output_md"],
            "model_output": model_out,
        }
    except Exception as e:
        raise HTTPException(400, f"ingest/analysis error: {e}")


# frontend
web_dir = Path("web")
web_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")


@app.get("/")
def index():
    idx = web_dir / "index.html"
    if not idx.exists():
        return JSONResponse({"msg": "Brak web/index.html"}, status_code=404)
    return FileResponse(idx)
