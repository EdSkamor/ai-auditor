"""
AI Auditor FastAPI Backend
Main server application with CORS and health checks
"""

import logging
import os

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-auditor")

# Basic Auth configuration
security = HTTPBasic()
BASIC_AUTH_USER = os.getenv("BASIC_AUTH_USER", "user")
BASIC_AUTH_PASS = os.getenv("BASIC_AUTH_PASS", "TwojPIN123!")


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify Basic Auth credentials."""
    if (
        credentials.username != BASIC_AUTH_USER
        or credentials.password != BASIC_AUTH_PASS
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# App configuration
app = FastAPI(
    title="AI Auditor Backend",
    version="1.0.0",
    description="Backend API for AI Auditor application",
)

# CORS configuration
ALLOWED_ORIGINS = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "https://ai-auditor-87.streamlit.app",
    # Add tunnel URLs dynamically - for now we'll allow specific patterns
]

# For development, we need to handle dynamic tunnel URLs
# We'll allow all origins but with proper credentials handling
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for tunnel flexibility
    allow_credentials=False,  # Disable credentials to avoid CORS issues with wildcard
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


# Health check endpoint (no auth required)
@app.get("/healthz")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "ready": True}


@app.get("/ready")
def ready_check():
    """Readiness check endpoint."""
    return {
        "status": "ready",
        "model_ready": True,
        "message": "AI Auditor backend is ready to serve requests",
    }


# Mock AI endpoint (Basic Auth disabled for demo)
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
            response = (
                "✅ Test połączenia z AI przebiegł pomyślnie. System działa poprawnie."
            )
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
        "endpoints": {"health": "/healthz", "ready": "/ready", "analyze": "/analyze"},
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
