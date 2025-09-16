"""
AI Auditor - Multipage Streamlit Application
Główny plik aplikacji z nawigacją między stronami
"""

import streamlit as st

import pages.analysis
import pages.chat
import pages.diagnostics
import pages.help
import pages.reports
from app.ui_utils import apply_modern_css, initialize_session_state, render_login
from src.ui.nav import render_navigation


def main():
    """Main function for multipage application."""
    # Initialize session state
    initialize_session_state()

    # Apply CSS
    apply_modern_css()

    # Check authentication
    if not st.session_state.authenticated:
        render_login()
        return

    # Render navigation sidebar
    render_navigation()

    # Render current page based on session state
    current_page = st.session_state.get("current_page", "Chat")

    if current_page == "Chat":
        pages.chat.render_chat_page()
    elif current_page == "AnalizaPOP":
        pages.analysis.render_analysis_page()
    elif current_page == "Raporty":
        pages.reports.render_reports_page()
    elif current_page == "Diagnostyka":
        pages.diagnostics.render_diagnostics_page()
    elif current_page == "Pomoc":
        pages.help.render_help_page()
    else:
        # Default home page
        st.markdown(
            '<div class="main-header">🔍 AI Auditor - Panel Audytora</div>',
            unsafe_allow_html=True,
        )

        # Welcome message
        st.success("✅ Zalogowano pomyślnie! Wybierz stronę z menu po lewej stronie.")

        # Quick stats
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Strony", "5", "Chat, Analiza, Raporty, Diagnostyka, Pomoc")

        with col2:
            st.metric("Funkcje", "20+", "AI, Analiza, Raporty, ZIP")

        with col3:
            st.metric("Formaty", "5", "PDF, Excel, JSON, XML, ZIP")

        with col4:
            st.metric("Status", "Online", "Wszystkie systemy działają")

        # Instructions
        st.markdown("### 📋 Instrukcje")

        st.info(
            """
        **Witaj w AI Auditor!**

        **Dostępne strony:**
        - 💬 **Chat AI** - Rozmowa z asystentem AI
        - 📊 **Analiza POP** - Analiza dokumentów księgowych
        - 📋 **Raporty** - Generowanie raportów audytowych
        - 🔧 **Diagnostyka** - Sprawdzanie stanu systemu
        - ❓ **Pomoc** - Instrukcje i wsparcie

        **Szybki start:**
        1. Przejdź do "Analiza POP" aby wgrać pliki
        2. Uruchom analizę dokumentów
        3. Przejrzyj wyniki w "Raporty"
        4. Użyj "Chat AI" do pytań o rachunkowość
        """
        )

        # Recent activity
        st.markdown("### 📈 Ostatnia aktywność")

        if "recent_activity" not in st.session_state:
            st.session_state.recent_activity = [
                {
                    "time": "10:30",
                    "action": "Zalogowano do systemu",
                    "status": "success",
                },
                {
                    "time": "10:25",
                    "action": "Analiza 5 plików PDF",
                    "status": "completed",
                },
                {
                    "time": "10:20",
                    "action": "Generowanie raportu Excel",
                    "status": "completed",
                },
                {
                    "time": "10:15",
                    "action": "Chat z AI - pytanie o MSRF",
                    "status": "success",
                },
            ]

        for activity in st.session_state.recent_activity:
            status_icon = (
                "✅" if activity["status"] in ["success", "completed"] else "⚠️"
            )
            st.write(f"{status_icon} **{activity['time']}** - {activity['action']}")


if __name__ == "__main__":
    main()
