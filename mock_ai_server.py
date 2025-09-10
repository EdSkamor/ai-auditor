#!/usr/bin/env python3
"""
Mock AI Server - Most między lokalnym AI a Streamlit Cloud
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import json
from datetime import datetime

app = FastAPI(title="Mock AI Server", version="1.0.0")

class AnalyzeRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 220
    do_sample: bool = False
    temperature: float = 0.7
    top_p: float = 0.9

class AnalyzeResponse(BaseModel):
    output: str
    status: str = "success"

def get_mock_response(prompt: str) -> str:
    """Generuje mock odpowiedź na podstawie promptu"""
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ["analiza", "analyze", "przeanalizuj"]):
        return """
## 📊 Analiza Audytorska - Wyniki

### 🔍 Podsumowanie
Na podstawie przeprowadzonej analizy można stwierdzić, że system audytorski funkcjonuje prawidłowo.

### 📈 Kluczowe Wskaźniki
- **Wskaźnik płynności**: 1.8 (dobry)
- **ROE**: 12.5% (satisfactory)
- **Zadłużenie**: 35% (akceptowalne)

### ⚠️ Zidentyfikowane Ryzyka
1. **Ryzyko operacyjne**: Średnie
2. **Ryzyko finansowe**: Niskie
3. **Ryzyko zgodności**: Niskie

### 💡 Rekomendacje
- Kontynuować obecną strategię
- Regularne monitorowanie wskaźników
- Wprowadzenie dodatkowych kontroli wewnętrznych

---
*Wygenerowano przez AI Auditor - Mock Response*
"""
    elif any(word in prompt_lower for word in ["bilans", "balance", "aktywa", "pasywa"]):
        return """
## 📊 Analiza Bilansu

### 🏦 Struktura Aktywów
- **Aktywa trwałe**: 60% (dobra struktura)
- **Aktywa obrotowe**: 40% (właściwa proporcja)

### 💰 Struktura Pasywów
- **Kapitał własny**: 65% (silna pozycja)
- **Zobowiązania**: 35% (kontrolowane)

### ⚖️ Równowaga Bilansowa
Bilans jest zrównoważony i odzwierciedla stabilną sytuację finansową.

---
*Wygenerowano przez AI Auditor - Mock Response*
"""
    else:
        return """
## 🤖 Odpowiedź AI Audytora

Dziękuję za zapytanie! Jako ekspert audytor, mogę pomóc w analizie różnych aspektów audytu.

### 📋 Dostępne Funkcje
- Analiza sprawozdań finansowych
- Ocena ryzyka audytorskiego
- Weryfikacja zgodności z przepisami
- Generowanie rekomendacji

---
*Wygenerowano przez AI Auditor - Mock Response*
"""

@app.get("/")
async def root():
    return {"message": "Mock AI Server - Most do Streamlit Cloud", "status": "active"}

@app.get("/healthz")
async def health_check():
    return {"status": "healthy", "ready": True, "timestamp": datetime.now().isoformat()}

@app.get("/ready")
async def ready_check():
    return {"ready": True, "model_loaded": True, "timestamp": datetime.now().isoformat()}

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """Mock endpoint analizy - odpowiada jak prawdziwy AI"""
    try:
        response_text = get_mock_response(request.prompt)
        return AnalyzeResponse(output=response_text, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas analizy: {str(e)}")

if __name__ == "__main__":
    print("🚀 Uruchamianie Mock AI Server...")
    uvicorn.run(app, host="0.0.0.0", port=8002)