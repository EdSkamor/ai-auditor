import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from model_hf_interface import call_model

os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

app = FastAPI(title="AI Auditor Demo", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeReq(BaseModel):
    prompt: str
    max_new_tokens: int = 220
    do_sample: bool = False
    temperature: float = 0.2
    top_p: float = 0.9

class AnalyzeResp(BaseModel):
    output: str

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalyzeResp)
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
        raise HTTPException(500, str(e))

web_dir = Path(__file__).parent / "web"
app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

@app.get("/")
def index():
    return FileResponse(web_dir / "index.html")
