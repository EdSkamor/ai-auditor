"""
Configuration management for AI Auditor
"""

import os

import streamlit as st

# Backend configuration
# Support both BACKEND_URL and AI_API_BASE for compatibility
BACKEND_URL = (
    st.secrets.get("BACKEND_URL")
    if hasattr(st, "secrets") and st.secrets and st.secrets.get("BACKEND_URL")
    else os.getenv("BACKEND_URL") or os.getenv("AI_API_BASE", "http://127.0.0.1:8001")
)

REQUEST_TIMEOUT = float(
    st.secrets.get("REQUEST_TIMEOUT", 30)
    if hasattr(st, "secrets") and st.secrets
    else os.getenv("REQUEST_TIMEOUT", "30")
)

# AI Configuration
AI_TIMEOUT = int(REQUEST_TIMEOUT)

# Basic Auth configuration
BASIC_AUTH_USER = (
    st.secrets.get("BASIC_AUTH_USER")
    if hasattr(st, "secrets") and st.secrets
    else os.getenv("BASIC_AUTH_USER", "user")
)

BASIC_AUTH_PASS = (
    st.secrets.get("BASIC_AUTH_PASS")
    if hasattr(st, "secrets") and st.secrets
    else os.getenv("BASIC_AUTH_PASS", "TwojPIN123!")
)


def get_backend_url():
    """Get backend URL with fallback."""
    return BACKEND_URL


def get_timeout():
    """Get request timeout."""
    return REQUEST_TIMEOUT


def get_basic_auth():
    """Get Basic Auth credentials."""
    return (
        (BASIC_AUTH_USER, BASIC_AUTH_PASS)
        if BASIC_AUTH_USER and BASIC_AUTH_PASS
        else None
    )
