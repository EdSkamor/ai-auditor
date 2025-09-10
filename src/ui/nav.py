"""
Centralized navigation system for AI Auditor
Single source of truth for all navigation
"""

import streamlit as st

# Define all pages in one place
PAGES = {
    "💬 Chat AI": "chat",
    "📊 Analiza POP": "analysis", 
    "📋 Raporty": "reports",
    "🔧 Diagnostyka": "diagnostics",
    "❓ Pomoc": "help",
}

def initialize_navigation():
    """Initialize navigation state."""
    if "current_page" not in st.session_state:
        st.session_state.current_page = "chat"

def render_navigation():
    """Render unified navigation - single source of truth."""
    with st.sidebar:
        st.markdown("### 🎛️ Panel Sterowania")
        
        # Theme toggle
        theme_icon = "🌙" if not st.session_state.get("dark_mode", False) else "☀️"
        if st.button(theme_icon, key="theme_toggle_nav"):
            st.session_state.dark_mode = not st.session_state.get("dark_mode", False)
            st.rerun()
        
        st.divider()
        
        # Navigation buttons
        for label, page_key in PAGES.items():
            is_active = st.session_state.get("current_page", "chat") == page_key
            if st.button(
                label, 
                key=f"nav_btn_{page_key}", 
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.divider()
        
        # Status info
        st.markdown("### 🔧 Status")
        try:
            import requests
            from src.config import get_backend_url, get_timeout
            backend_url = get_backend_url()
            response = requests.get(f"{backend_url}/healthz", timeout=get_timeout())
            if response.ok:
                st.success("🤖 AI Online")
            else:
                st.warning("⚠️ AI Issues")
        except:
            st.error("❌ AI Offline")

def get_current_page():
    """Get current page key."""
    return st.session_state.get("current_page", "chat")
