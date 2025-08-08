import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from model_hf_interface import call_model

os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

app = FastAPI(title="AI Auditor Demo", version="0.1.0")

# dla demo – odpalamy CORS na wszystkie źródła
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# statyki
app.mount("/static", StaticFiles(directory="web"), name="static")

@app.get("/")
def index():
    return FileResponse("web/index.html")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

class AnalyzeRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 200
    do_sample: bool = False

class AnalyzeResponse(BaseModel):
    output: str

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    out = call_model(
        req.prompt,
        max_new_tokens=req.max_new_tokens,
        do_sample=req.do_sample
    )
    return {"output": out}
