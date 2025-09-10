"""
Configuration management for AI Auditor
"""

import os
import streamlit as st

# Backend configuration
BACKEND_URL = (
    st.secrets.get("BACKEND_URL") 
    if hasattr(st, 'secrets') and st.secrets and st.secrets.get("BACKEND_URL")
    else os.getenv("BACKEND_URL", "https://exports-streets-spelling-disclaimer.trycloudflare.com")
)

REQUEST_TIMEOUT = float(
    st.secrets.get("REQUEST_TIMEOUT", 30)
    if hasattr(st, 'secrets') and st.secrets
    else os.getenv("REQUEST_TIMEOUT", "30")
)

# AI Configuration  
AI_SERVER_URL = BACKEND_URL
AI_TIMEOUT = int(REQUEST_TIMEOUT)

def get_backend_url():
    """Get backend URL with fallback."""
    return BACKEND_URL

def get_timeout():
    """Get request timeout."""
    return REQUEST_TIMEOUT
