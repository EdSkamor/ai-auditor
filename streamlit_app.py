"""
Production Streamlit UI for AI Auditor.
Complete web interface for invoice validation and audit support.
"""

import streamlit as st
import pandas as pd
import json
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime
import logging
import sys
import os
import requests
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from web.auditor_frontend import AuditorFrontend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Auditor - Panel Audytora",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2e6da4 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f4e79;
        margin: 0.5rem 0;
    }
    .success-card {
        background: #d4edda;
        border-left-color: #28a745;
    }
    .warning-card {
        background: #fff3cd;
        border-left-color: #ffc107;
    }
    .error-card {
        background: #f8d7da;
        border-left-color: #dc3545;
    }
    .stButton > button {
        background: #1f4e79;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton > button:hover {
        background: #2e6da4;
        color: white;
    }
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'audit_results' not in st.session_state:
    st.session_state.audit_results = None
if 'audit_history' not in st.session_state:
    st.session_state.audit_history = []
if 'ocr_results' not in st.session_state:
    st.session_state.ocr_results = None

# AI Configuration
AI_SERVER_URL = os.getenv("AI_SERVER_URL", st.secrets.get("ai", {}).get("server_url", "http://localhost:8000"))
AI_TIMEOUT = st.secrets.get("ai", {}).get("timeout", 30)


def call_real_ai(prompt: str, temperature: float = 0.8, max_tokens: int = 512) -> str:
    """Call the real AI model via API."""
    try:
        # Check if AI server is available
        health_response = requests.get(f"{AI_SERVER_URL}/healthz", timeout=5)
        if not health_response.ok:
            return f"❌ Serwer AI niedostępny (status: {health_response.status_code})"
        
        # Check if model is ready
        ready_response = requests.get(f"{AI_SERVER_URL}/ready", timeout=5)
        if ready_response.ok:
            ready_data = ready_response.json()
            if not ready_data.get("model_ready", False):
                return "⏳ Model AI się dogrzewa, spróbuj za chwilę..."
        
        # Call AI model
        payload = {
            "prompt": prompt,
            "max_new_tokens": max_tokens,
            "do_sample": True,
            "temperature": temperature,
            "top_p": 0.9
        }
        
        response = requests.post(
            f"{AI_SERVER_URL}/analyze",
            json=payload,
            timeout=AI_TIMEOUT
        )
        
        if response.ok:
            data = response.json()
            return data.get("output", "Brak odpowiedzi od AI")
        else:
            return f"❌ Błąd AI: {response.status_code} - {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Brak połączenia z serwerem AI. Upewnij się, że serwer działa na localhost:8000"
    except requests.exceptions.Timeout:
        return "⏰ Timeout - AI potrzebuje więcej czasu na odpowiedź"
    except Exception as e:
        return f"❌ Błąd połączenia z AI: {str(e)}"


def get_ai_status() -> dict:
    """Get AI server status."""
    try:
        health_response = requests.get(f"{AI_SERVER_URL}/healthz", timeout=5)
        ready_response = requests.get(f"{AI_SERVER_URL}/ready", timeout=5)
        
        return {
            "server_available": health_response.ok,
            "model_ready": ready_response.ok and ready_response.json().get("model_ready", False),
            "server_url": AI_SERVER_URL
        }
    except:
        return {
            "server_available": False,
            "model_ready": False,
            "server_url": AI_SERVER_URL
        }



def main():
    """Main Streamlit application - use the better UI."""
    try:
        # Use the better UI from auditor_frontend
        frontend = AuditorFrontend()
        frontend.render_main()
    except Exception as e:
        st.error(f"❌ Błąd ładowania UI: {e}")
        st.info("Ładowanie podstawowego UI...")
        
        # Fallback to basic UI
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h1>🔍 AI Auditor</h1>
            <p>System audytu faktur i dokumentów księgowych</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("""
        **Funkcjonalności:**
        - 🔍 Automatyczny audyt faktur
        - 🤖 Asystent AI z wiedzą rachunkową
        - 📊 Analityka ryzyk
        - 🌐 Integracje PL-core (KSeF, JPK, KRS)
        - 📋 Portal PBC i zarządzanie zleceniami
        """)


if __name__ == "__main__":
    main()
