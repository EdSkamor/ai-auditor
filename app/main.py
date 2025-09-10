"""
AI Auditor FastAPI Backend
Main server application with CORS and health checks
"""

import logging
import os
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-auditor")

# App configuration
app = FastAPI(
    title="AI Auditor Backend",
    version="1.0.0",
    description="Backend API for AI Auditor application"
)

# CORS configuration
ALLOWED_ORIGINS = [
    "http://localhost:8501",
    "http://127.0.0.1:8501", 
    "https://ai-auditor-87.streamlit.app",
    "https://exports-streets-spelling-disclaimer.trycloudflare.com",
    "*"  # For development - allow all
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class AnalyzeRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 220
    do_sample: bool = False
    temperature: float = 0.7
    top_p: float = 0.9

class AnalyzeResponse(BaseModel):
    output: str
    status: str = "success"

# Health check endpoint
@app.get("/healthz")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "AI Auditor backend is running"}

@app.get("/ready")
def ready_check():
    """Readiness check endpoint."""
    return {
        "status": "ready",
        "model_ready": True,
        "message": "AI Auditor backend is ready to serve requests"
    }

# Mock AI endpoint
@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_text(request: AnalyzeRequest):
    """Analyze text using AI model (mock implementation)."""
    try:
        # Mock response based on prompt
        prompt_lower = request.prompt.lower()
        
        if any(word in prompt_lower for word in ["analiza", "analyze", "przeanalizuj"]):
            response = """
Na podstawie analizy przedstawionych danych mogę wskazać następujące kwestie:

📊 **Główne ustalenia:**
- Dane wydają się kompletne i spójne
- Nie wykryto znaczących nieprawidłowości
- Struktura danych jest zgodna ze standardami

⚠️ **Uwagi i rekomendacje:**
- Zalecam weryfikację kilku pozycji wymagających dodatkowej dokumentacji
- Warto rozważyć implementację dodatkowych kontroli

✅ **Status:** Analiza zakończona pomyślnie
"""
        elif any(word in prompt_lower for word in ["błąd", "error", "problem"]):
            response = "❌ Wykryto potencjalne problemy wymagające dalszej analizy."
        elif "test" in prompt_lower:
            response = "✅ Test połączenia z AI przebiegł pomyślnie. System działa poprawnie."
        else:
            response = f"Otrzymano zapytanie: {request.prompt[:100]}...\n\nSystem AI jest gotowy do pracy."
        
        return AnalyzeResponse(output=response, status="success")
        
    except Exception as e:
        logger.error(f"Error in analyze_text: {e}")
        raise HTTPException(status_code=500, detail=f"Błąd analizy: {str(e)}")

# Root endpoint
@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "message": "AI Auditor Backend API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/healthz",
            "ready": "/ready", 
            "analyze": "/analyze"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
