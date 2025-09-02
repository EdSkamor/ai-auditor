
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ai-audytor API", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-audytor", "mode": "api"}

# Poniższe endpointy są stubami – podpinamy lokalne funkcje później.
@app.post("/benford")
async def benford(file: UploadFile = File(...)):
    return {"ok": True, "task": "benford", "note": "stub demo"}

@app.post("/beneish")
async def beneish(file: UploadFile = File(...)):
    return {"ok": True, "task": "beneish", "note": "stub demo"}

@app.post("/regresja")
async def regresja(file: UploadFile = File(...)):
    return {"ok": True, "task": "regresja", "note": "stub demo"}
