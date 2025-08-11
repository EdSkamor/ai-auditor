import os
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from model_hf_interface import call_model
from tools.ingest import read_table
from tools.analysis import analyze_table

os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

app = FastAPI(title="AI Auditor Demo", version="0.2.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

class AnalyzeReq(BaseModel):
    prompt: str
    max_new_tokens: int = 220
    do_sample: bool = False
    temperature: float = 0.2
    top_p: float = 0.9

class FolderReq(BaseModel):
    path: str

# statyki
web_dir = Path(__file__).parent / "web"
web_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

@app.get("/")
def index():
    return FileResponse(web_dir / "index.html")

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
        raise HTTPException(500, str(e))

@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    try:
        # zapisz do /tmp
        up_dir = Path("/tmp/aiauditor"); up_dir.mkdir(parents=True, exist_ok=True)
        dst = up_dir / file.filename
        with dst.open("wb") as f:
            while chunk := await file.read(1024 * 1024):
                f.write(chunk)

        data = read_table(dst)
        res = analyze_table(data["df"])
        # jeśli w arkuszu jest prompt – można w przyszłości podmienić prompt do LLM
        return {"columns": data["columns"], "prompts": data["prompts"], "output": res["output_md"], "metrics": res["metrics"]}
    except Exception as e:
        raise HTTPException(400, f"Nie udało się przetworzyć pliku: {e}")

@app.post("/analyze-folder")
def analyze_folder(req: FolderReq):
    p = Path(req.path).expanduser()
    if not p.exists():
        raise HTTPException(404, f"Folder nie istnieje: {p}")
    results = []
    for f in p.rglob("*"):
        if f.suffix.lower() in [".xlsx", ".xls", ".csv", ".tsv"]:
            try:
                data = read_table(f)
                res = analyze_table(data["df"])
                results.append({
                    "file": str(f),
                    "columns": data["columns"],
                    "prompts": data["prompts"],
                    "metrics": res["metrics"],
                    "output": res["output_md"],
                })
            except Exception as e:
                results.append({"file": str(f), "error": str(e)})
    return {"count": len(results), "results": results}
