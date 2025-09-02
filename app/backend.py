
import os, requests
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
MODE = os.getenv("BACKEND_MODE", "local").lower()  # "local" | "remote"

def health():
    if MODE == "remote":
        r = requests.get(f"{API_URL}/health", timeout=30)
        r.raise_for_status()
        return r.json() | {"source": "remote"}
    return {"status": "ok", "service": "ai-audytor", "mode": "local", "source": "local"}

def run_benford(file_bytes: bytes, filename: str):
    if MODE == "remote":
        r = requests.post(f"{API_URL}/benford",
                          files={"file": (filename, file_bytes, "application/octet-stream")},
                          timeout=120)
        r.raise_for_status()
        return r.json() | {"source": "remote"}
    # TODO: podłącz lokalną implementację; na razie stub
    return {"ok": True, "task": "benford", "note": "local stub", "source": "local"}

def run_beneish(file_bytes: bytes, filename: str):
    if MODE == "remote":
        r = requests.post(f"{API_URL}/beneish",
                          files={"file": (filename, file_bytes, "application/octet-stream")},
                          timeout=120)
        r.raise_for_status()
        return r.json() | {"source": "remote"}
    return {"ok": True, "task": "beneish", "note": "local stub", "source": "local"}

def run_regresja(file_bytes: bytes, filename: str):
    if MODE == "remote":
        r = requests.post(f"{API_URL}/regresja",
                          files={"file": (filename, file_bytes, "application/octet-stream")},
                          timeout=120)
        r.raise_for_status()
        return r.json() | {"source": "remote"}
    return {"ok": True, "task": "regresja", "note": "local stub", "source": "local"}
