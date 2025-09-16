"""
Common UI utilities for AI Auditor
Shared functions and components across all pages
"""

import os
import time
from typing import Any, Dict

import requests
import streamlit as st
from requests.auth import HTTPBasicAuth

# Import configuration from centralized config
from src.config import AI_TIMEOUT, BACKEND_URL

# Use centralized configuration
ADMIN_PASSWORD = os.getenv("AIAUDITOR_PASSWORD", "TwojPIN123!")
AUTH = HTTPBasicAuth("ai-auditor", ADMIN_PASSWORD)


def apply_modern_css():
    """Apply modern CSS styling."""
    css = """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .view-header {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #1f2937;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 0.5rem;
    }

    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }

    .finding-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
    }

    .finding-high {
        border-left: 4px solid #e74c3c;
    }

    .finding-medium {
        border-left: 4px solid #f39c12;
    }

    .finding-low {
        border-left: 4px solid #27ae60;
    }

    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: bold;
    }

    .status-running {
        background-color: #f39c12;
        color: white;
    }

    .status-completed {
        background-color: #27ae60;
        color: white;
    }

    .status-failed {
        background-color: #e74c3c;
        color: white;
    }

    .status-pending {
        background-color: #95a5a6;
        color: white;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def get_ai_status() -> Dict[str, Any]:
    """Get AI server status with RTT measurement."""
    try:
        # Test RTT with 3 attempts
        rtt_times = []

        for i in range(3):
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}/healthz", timeout=5)
            rtt = (time.time() - start_time) * 1000  # Convert to ms
            rtt_times.append(rtt)

        rtt_avg = sum(rtt_times) / len(rtt_times)

        return {
            "available": response.ok,
            "rtt_avg": rtt_avg,
            "status_code": response.status_code,
            "server_url": BACKEND_URL,
        }
    except Exception:
        return {
            "available": False,
            "rtt_avg": None,
            "status_code": None,
            "server_url": BACKEND_URL,
        }


def render_ai_status():
    """Render AI status in sidebar."""
    status = get_ai_status()

    if status["available"]:
        st.success(f"🤖 AI Online ({status['rtt_avg']:.1f}ms)")
    else:
        st.error("❌ AI Offline")

    return status


def render_diagnostics():
    """Render diagnostics section in sidebar."""
    st.markdown("### 🔧 Diagnostyka")

    # AI Status
    ai_status = render_ai_status()

    # Backend selector
    backend = st.selectbox(
        "Backend AI:",
        ["Local (localhost:8001)", "Tunnel (loca.lt)", "Mock"],
        key="ai_backend",
    )

    # Package versions
    with st.expander("📦 Wersje pakietów"):
        try:
            import pandas as pd_lib
            import requests as req_lib
            import streamlit as st_lib

            st.text(f"Streamlit: {st_lib.__version__}")
            st.text(f"Pandas: {pd_lib.__version__}")
            st.text(f"Requests: {req_lib.__version__}")
        except Exception as e:
            st.error(f"Błąd: {e}")

    # Restart session button
    if st.button("🔄 Restart Sesji", use_container_width=True):
        st.session_state.clear()
        st.success("✅ Sesja wyczyszczona!")
        st.rerun()

    return ai_status


@st.cache_data(ttl=3600)  # Cache for 1 hour
def call_real_ai(prompt: str, temperature: float = 0.8, max_tokens: int = 2048) -> str:
    """Call the real AI model via API."""
    try:
        # Check if AI server is available
        health_response = requests.get(f"{BACKEND_URL}/healthz", timeout=5)
        if not health_response.ok:
            return f"❌ Serwer AI niedostępny (status: {health_response.status_code})"

        # Check if model is ready
        ready_response = requests.get(f"{BACKEND_URL}/ready", timeout=5)
        if ready_response.ok:
            ready_data = ready_response.json()
            if not ready_data.get("model_ready", False):
                return "⏳ Model AI się dogrzewa, spróbuj za chwilę..."

        # Call AI model
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "do_sample": True,
            "temperature": temperature,
            "top_p": 0.9,
        }

        response = requests.post(
            f"{BACKEND_URL}/analyze", json=payload, timeout=AI_TIMEOUT
        )

        if response.ok:
            data = response.json()
            return data.get("output", "Brak odpowiedzi od AI")
        else:
            return f"❌ Błąd AI: {response.status_code} - {response.text}"

    except requests.exceptions.ConnectionError:
        return "❌ Brak połączenia z serwerem AI. Upewnij się, że serwer działa na porcie 8001"
    except requests.exceptions.Timeout:
        return "⏰ Timeout - serwer AI nie odpowiada w wymaganym czasie"
    except Exception as e:
        return f"❌ Nieoczekiwany błąd: {str(e)}"


# render_navigation moved to src/ui/nav.py to avoid duplication


def initialize_session_state():
    """Initialize session state variables."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Chat"
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    if "lang" not in st.session_state:
        st.session_state.lang = "pl"


def render_login():
    """Render login page."""
    st.markdown(
        '<div class="main-header">🔐 Logowanie do AI Auditor</div>',
        unsafe_allow_html=True,
    )

    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("login_form"):
            st.markdown("**Wprowadź hasło dostępu:**")
            password = st.text_input(
                "Hasło", type="password", placeholder="Wprowadź hasło..."
            )

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                login_clicked = st.form_submit_button(
                    "🔑 Zaloguj", use_container_width=True
                )
            with col_btn2:
                if st.form_submit_button("❌ Anuluj", use_container_width=True):
                    st.stop()

            if login_clicked:
                if password == "TwojPIN123!":
                    st.session_state.authenticated = True
                    st.success("✅ Zalogowano pomyślnie!")
                    st.rerun()
                else:
                    st.error("❌ Nieprawidłowe hasło!")

        st.markdown("---")
        st.markdown("**ℹ️ Informacje:**")
        st.info(
            """
        **AI Auditor** - System audytu faktur i dokumentów księgowych

        **Funkcjonalności:**
        - 🔍 Automatyczny audyt faktur
        - 📊 Analiza ryzyka
        - 🤖 Asystent AI
        - 📋 Generowanie raportów
        - 🌐 Integracje PL-core (KSeF, JPK, KRS)
        """
        )


def render_page_header(title: str, icon: str = "📊"):
    """Render page header."""
    st.markdown(
        f'<div class="view-header">{icon} {title}</div>', unsafe_allow_html=True
    )
