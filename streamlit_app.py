"""
AI Auditor - Unified Streamlit Application
Single entry point for all functionality
"""

import logging

import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)

# Page configuration - ONLY ONCE
st.set_page_config(
    page_title="AI Auditor - Panel Audytora",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

import pages.analysis

# Import page modules
import pages.chat
import pages.diagnostics
import pages.help
import pages.reports
from app.ui_utils import initialize_session_state

# Import after page config
from src.ui.nav import get_current_page, initialize_navigation, render_navigation
from src.ui.safe import safe_run


def main():
    """Main application function."""
    # Initialize
    initialize_session_state()
    initialize_navigation()

    # Twarda bramka przed PIN-em - nie renderujemy niczego poza tym
    if not st.session_state.get("authenticated"):
        with st.sidebar:
            st.info("🔒 **Zaloguj się, aby uzyskać dostęp do panelu.**")
        from app.ui_utils import render_login

        render_login()
        st.stop()  # nic poniżej nie renderujemy przed PIN-em

    # Render navigation - SINGLE SOURCE OF TRUTH
    render_navigation()

    # Get current page
    current_page = get_current_page()

    # Route to appropriate page
    if current_page == "chat":
        safe_run(pages.chat.render_chat_page, section="chat")
    elif current_page == "analysis":
        safe_run(pages.analysis.render_analysis_page, section="analysis")
    elif current_page == "reports":
        safe_run(pages.reports.render_reports_page, section="reports")
    elif current_page == "diagnostics":
        safe_run(pages.diagnostics.render_diagnostics_page, section="diagnostics")
    elif current_page == "help":
        safe_run(pages.help.render_help_page, section="help")
    else:
        # Default page
        st.markdown(
            '<div style="font-size: 2rem; text-align: center; margin: 2rem;">🔍 AI Auditor - Panel Audytora</div>',
            unsafe_allow_html=True,
        )
        st.success("✅ Zalogowano pomyślnie! Wybierz stronę z menu po lewej stronie.")


if __name__ == "__main__":
    main()
