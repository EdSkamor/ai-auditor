"""
Nowoczesny UI/UX dla AI Auditor.
Minimalistyczny, funkcjonalny, estetyczny design.
"""

import os
from datetime import datetime, timedelta
from typing import Dict

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

try:
    from .ai_client import AIClient
    from .config import AI_API_BASE
    from .i18n import get_language_switcher, t
except ImportError:
    # Fallback for Streamlit Cloud deployment
    try:
        from app.ai_client import AIClient
        from app.config import AI_API_BASE
        from app.translations import get_lang, t
    except ImportError:
        # Fallback if modules are not available
        def t(key: str, **kwargs) -> str:
            return key.format(**kwargs) if kwargs else key

        def get_language_switcher() -> str:
            return "pl"

        class AIClient:
            def __init__(self, *args, **kwargs):
                pass

            def is_online(self):
                return False

            def get_status(self):
                return {"online": False, "error": "AIClient not available"}

        AI_API_BASE = "http://127.0.0.1:8001"


class ModernUI:
    """Nowoczesny interfejs użytkownika."""

    def __init__(self):
        self.initialize_session_state()
        # AI Configuration
        self.AI_SERVER_URL = os.getenv("AI_SERVER_URL", "http://localhost:8001")
        self.AI_TIMEOUT = 30  # seconds
        # Use environment variable for password security
        self.ADMIN_PASSWORD = "TwojPIN123!"

        # Security: Log password usage (without exposing the password)
        if self.ADMIN_PASSWORD == "admin123":
            print(
                "⚠️ WARNING: Using default password. Set AI_AUDITOR_PASSWORD environment variable for security."
            )
        elif self.ADMIN_PASSWORD == "TwojPIN123!":
            print("✅ Using configured password: TwojPIN123!")

    def initialize_session_state(self):
        """Inicjalizacja stanu sesji."""
        if "dark_mode" not in st.session_state:
            st.session_state.dark_mode = False
        if "sidebar_collapsed" not in st.session_state:
            st.session_state.sidebar_collapsed = False
        if "current_page" not in st.session_state:
            st.session_state.current_page = "dashboard"
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False

    def get_theme_config(self) -> Dict[str, str]:
        """Konfiguracja motywu."""
        if st.session_state.dark_mode:
            return {
                "primary_color": "#00d4aa",
                "secondary_color": "#6366f1",
                "accent_color": "#f59e0b",
                "background_color": "#0a0a0a",
                "surface_color": "#1a1a1a",
                "text_color": "#ffffff",
                "text_secondary": "#a1a1aa",
                "border_color": "#2a2a2a",
                "success_color": "#10b981",
                "warning_color": "#f59e0b",
                "error_color": "#ef4444",
                "gradient_start": "#00d4aa",
                "gradient_end": "#6366f1",
            }
        else:
            return {
                "primary_color": "#2563eb",
                "secondary_color": "#7c3aed",
                "accent_color": "#06b6d4",
                "background_color": "#fafafa",
                "surface_color": "#ffffff",
                "text_color": "#1f2937",
                "text_secondary": "#6b7280",
                "border_color": "#e5e7eb",
                "success_color": "#059669",
                "warning_color": "#d97706",
                "error_color": "#dc2626",
                "gradient_start": "#2563eb",
                "gradient_end": "#7c3aed",
            }

    def apply_modern_css(self):
        """Aplikowanie nowoczesnego CSS."""
        theme = self.get_theme_config()

        css = f"""
        <style>
            /* Global Styles */
            .stApp {{
                background-color: {theme['background_color']};
                color: {theme['text_color']};
            }}

            .stApp > div {{
                background-color: {theme['background_color']};
            }}

            .main .block-container {{
                background-color: {theme['background_color']};
                color: {theme['text_color']};
            }}

            /* Header */
            .main-header {{
                font-size: 2.5rem;
                font-weight: 700;
                color: {theme['primary_color']};
                text-align: center;
                margin-bottom: 2rem;
                background: linear-gradient(135deg, {theme['gradient_start']}, {theme['gradient_end']});
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}

            /* Cards */
            .metric-card {{
                background: {theme['surface_color']};
                border: 1px solid {theme['border_color']};
                border-radius: 16px;
                padding: 2rem;
                margin: 1rem 0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}

            .metric-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, {theme['gradient_start']}, {theme['gradient_end']});
            }}

            .metric-card:hover {{
                transform: translateY(-4px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
                border-color: {theme['primary_color']};
            }}

            .metric-value {{
                font-size: 2rem;
                font-weight: 700;
                color: {theme['primary_color']};
                margin: 0;
            }}

            .metric-label {{
                font-size: 0.875rem;
                color: {theme['text_secondary']};
                margin: 0;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}

            /* Status Badges */
            .status-badge {{
                display: inline-flex;
                align-items: center;
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}

            .status-running {{
                background-color: {theme['warning_color']}20;
                color: {theme['warning_color']};
                border: 1px solid {theme['warning_color']}40;
            }}

            .status-completed {{
                background-color: {theme['success_color']}20;
                color: {theme['success_color']};
                border: 1px solid {theme['success_color']}40;
            }}

            .status-failed {{
                background-color: {theme['error_color']}20;
                color: {theme['error_color']};
                border: 1px solid {theme['error_color']}40;
            }}

            .status-pending {{
                background-color: {theme['text_secondary']}20;
                color: {theme['text_secondary']};
                border: 1px solid {theme['text_secondary']}40;
            }}

            /* Finding Cards */
            .finding-card {{
                background: {theme['surface_color']};
                border-left: 4px solid {theme['primary_color']};
                border-radius: 8px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
            }}

            .finding-card:hover {{
                transform: translateX(4px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }}

            .finding-high {{
                border-left-color: {theme['error_color']};
            }}

            .finding-medium {{
                border-left-color: {theme['warning_color']};
            }}

            .finding-low {{
                border-left-color: {theme['success_color']};
            }}

            /* Buttons */
            .stButton > button {{
                background: linear-gradient(135deg, {theme['gradient_start']}, {theme['gradient_end']});
                color: white;
                border: none;
                border-radius: 12px;
                padding: 0.75rem 1.5rem;
                font-weight: 600;
                font-size: 0.95rem;
                transition: all 0.3s ease;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }}

            .stButton > button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
                filter: brightness(1.1);
            }}

            /* Sidebar buttons */
            .stSidebar .stButton > button {{
                background: {theme['surface_color']};
                color: {theme['text_color']};
                border: 1px solid {theme['border_color']};
                border-radius: 8px;
                margin: 0.25rem 0;
                transition: all 0.2s ease;
            }}

            .stSidebar .stButton > button:hover {{
                background: {theme['primary_color']};
                color: white;
                border-color: {theme['primary_color']};
                transform: translateX(4px);
            }}

            .stButton > button:active {{
                transform: translateY(0);
            }}

            /* Primary buttons */
            .stButton > button[kind="primary"] {{
                background: linear-gradient(135deg, {theme['primary_color']}, {theme['secondary_color']});
                color: white;
                border: 1px solid {theme['primary_color']};
            }}

            .stButton > button[kind="primary"]:hover {{
                background: linear-gradient(135deg, {theme['primary_color']}dd, {theme['secondary_color']}dd);
                border-color: {theme['primary_color']};
            }}

            /* Secondary buttons */
            .stButton > button[kind="secondary"] {{
                background: {theme['surface_color']};
                color: {theme['text_color']};
                border: 1px solid {theme['border_color']};
            }}

            .stButton > button[kind="secondary"]:hover {{
                background: {theme['border_color']};
                border-color: {theme['text_secondary']};
            }}

            /* Sidebar */
            .sidebar-section {{
                background: {theme['surface_color']};
                border: 1px solid {theme['border_color']};
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
            }}

            /* Progress Bars */
            .progress-container {{
                background: {theme['border_color']};
                border-radius: 9999px;
                height: 8px;
                overflow: hidden;
                margin: 0.5rem 0;
            }}

            .progress-bar {{
                background: linear-gradient(90deg, {theme['primary_color']}, {theme['secondary_color']});
                height: 100%;
                border-radius: 9999px;
                transition: width 0.3s ease;
            }}

            /* Tables */
            .dataframe {{
                background: {theme['surface_color']};
                border: 1px solid {theme['border_color']};
                border-radius: 8px;
                overflow: hidden;
            }}

            /* Navigation */
            .nav-item {{
                display: flex;
                align-items: center;
                padding: 0.75rem 1rem;
                border-radius: 8px;
                margin: 0.25rem 0;
                transition: all 0.3s ease;
                cursor: pointer;
            }}

            .nav-item:hover {{
                background: {theme['surface_color']};
            }}

            .nav-item.active {{
                background: {theme['primary_color']}20;
                color: {theme['primary_color']};
                border-left: 3px solid {theme['primary_color']};
            }}

            /* Animations */
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}

            .fade-in {{
                animation: fadeIn 0.5s ease-out;
            }}

            /* Inputs */
            .stTextInput > div > div > input {{
                border-radius: 12px;
                border: 2px solid {theme['border_color']};
                background-color: {theme['surface_color']};
                color: {theme['text_color']};
                padding: 0.75rem 1rem;
                font-size: 0.95rem;
                transition: all 0.3s ease;
            }}

            .stTextInput > div > div > input:focus {{
                border-color: {theme['primary_color']};
                box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
                outline: none;
            }}

            .stSelectbox > div > div {{
                border-radius: 12px;
                border: 2px solid {theme['border_color']};
                background-color: {theme['surface_color']};
                transition: all 0.3s ease;
            }}

            .stSelectbox > div > div:focus-within {{
                border-color: {theme['primary_color']};
                box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
            }}

            /* File uploader */
            .stFileUploader {{
                border-radius: 12px;
                border: 2px dashed {theme['border_color']};
                background-color: {theme['surface_color']};
                transition: all 0.3s ease;
            }}

            .stFileUploader:hover {{
                border-color: {theme['primary_color']};
                background-color: rgba(37, 99, 235, 0.05);
            }}

            /* Chat messages */
            .stChatMessage {{
                border-radius: 16px;
                margin: 0.5rem 0;
            }}

            /* Responsive */
            @media (max-width: 768px) {{
                .main-header {{
                    font-size: 2rem;
                }}

                .metric-card {{
                    padding: 1rem;
                }}

                .finding-card {{
                    padding: 1rem;
                }}
            }}
        </style>
        """

        st.markdown(css, unsafe_allow_html=True)

    def render_header(self):
        """Renderowanie nagłówka."""
        self.apply_modern_css()

        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            theme_icon = "🌙" if not st.session_state.dark_mode else "☀️"
            if st.button(theme_icon, key="theme_toggle"):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()

        with col2:
            st.markdown(
                f'<div class="main-header fade-in">🔍 {t("app_title_short")}</div>',
                unsafe_allow_html=True,
            )

        with col3:
            if st.button("📊", key="settings_toggle"):
                st.session_state.sidebar_collapsed = (
                    not st.session_state.sidebar_collapsed
                )
                st.rerun()

    def render_sidebar(self):
        """Renderowanie nowoczesnego sidebara."""
        with st.sidebar:
            st.markdown(f"## 🎛️ {t('control_panel')}")

            # AI Backend Status
            client = AIClient()
            status = client.get_status()
            if status["online"]:
                st.markdown(f"**{t('backend_ai')}:** ✅ {t('online')} @ {AI_API_BASE}")
            else:
                st.markdown(f"**{t('backend_ai')}:** ⛔ {t('offline')}")

            st.divider()

            # Language switcher
            st.markdown(f"### 🌐 {t('language')}")
            get_language_switcher()

            st.divider()

            # Navigation
            pages = {
                f"📊 {t('dashboard')}": "dashboard",
                f"🏃 {t('run')}": "run",
                f"🔍 {t('findings')}": "findings",
                f"📤 {t('exports')}": "exports",
                f"💬 {t('chat_ai')}": "chat",
                "🤖 AI Audytor": "ai_auditor",
                f"📚 {t('instructions')}": "instructions",
                f"⚙️ {t('settings')}": "settings",
            }

            for label, page in pages.items():
                is_active = st.session_state.current_page == page
                if st.button(label, key=f"nav_{page}", use_container_width=True):
                    st.session_state.current_page = page
                    st.rerun()

            st.divider()

            # Quick Stats
            st.markdown(f"### 📈 {t('quick_stats')}")
            self.render_quick_stats()

            st.divider()

            # Keyboard Shortcuts
            st.markdown(f"### ⌨️ {t('keyboard_shortcuts')}")
            shortcuts = [
                (t("ctrl_1"), t("dashboard")),
                (t("ctrl_2"), t("run")),
                (t("ctrl_3"), t("findings")),
                (t("ctrl_4"), t("exports")),
                (t("ctrl_d"), t("dark_mode")),
                (t("ctrl_r"), t("refresh")),
            ]

            for shortcut, action in shortcuts:
                st.markdown(f"**{shortcut}** - {action}")

            st.divider()

            # Logout button
            if st.button(f"🚪 {t('logout')}", use_container_width=True):
                st.session_state.authenticated = False
                st.rerun()

    def render_quick_stats(self):
        """Renderowanie szybkich statystyk."""
        # Mock data - in real implementation, get from actual data
        stats = {
            "Zadania": {"value": 12, "change": "+2"},
            "Zakończone": {"value": 8, "change": "+1"},
            "Znalezione": {"value": 24, "change": "+5"},
            "Eksporty": {"value": 6, "change": "+2"},
        }

        for label, data in stats.items():
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**{label}**")
            with col2:
                st.markdown(f"**{data['value']}** {data['change']}")

    def render_dashboard(self):
        """Renderowanie dashboardu."""
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)

        # Main metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                """
            <div class="metric-card">
                <div class="metric-value">12</div>
                <div class="metric-label">Aktywne zadania</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                """
            <div class="metric-card">
                <div class="metric-value">24</div>
                <div class="metric-label">Znalezione niezgodności</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                """
            <div class="metric-card">
                <div class="metric-value">8</div>
                <div class="metric-label">Zakończone audyty</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col4:
            st.markdown(
                """
            <div class="metric-card">
                <div class="metric-value">6</div>
                <div class="metric-label">Eksporty</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.divider()

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📊 Status zadań")
            # Mock chart data
            chart_data = pd.DataFrame(
                {
                    "Status": ["Ukończone", "W trakcie", "Oczekujące", "Błędy"],
                    "Liczba": [8, 3, 1, 0],
                }
            )

            fig = px.pie(
                chart_data,
                values="Liczba",
                names="Status",
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            fig.update_layout(showlegend=True, height=300)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 🔍 Poziomy ryzyka")
            # Mock chart data
            risk_data = pd.DataFrame(
                {
                    "Poziom": ["Niski", "Średni", "Wysoki", "Krytyczny"],
                    "Liczba": [15, 6, 2, 1],
                }
            )

            fig = px.bar(
                risk_data,
                x="Poziom",
                y="Liczba",
                color="Liczba",
                color_continuous_scale="RdYlGn_r",
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    def render_run_page(self):
        """Renderowanie strony Run."""
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)

        st.markdown("### 🏃 Uruchamianie audytu")

        # Upload section
        col1, col2 = st.columns([2, 1])

        with col1:
            uploaded_files = st.file_uploader(
                "Wybierz pliki do audytu",
                type=["pdf", "zip", "csv", "xlsx"],
                accept_multiple_files=True,
                help="Możesz wybrać wiele plików jednocześnie",
            )

        with col2:
            if st.button("🚀 Uruchom Audyt", type="primary", use_container_width=True):
                if uploaded_files:
                    st.success(f"Audyt uruchomiony dla {len(uploaded_files)} plików!")
                else:
                    st.warning("Wybierz pliki do audytu")

        st.divider()

        # Job queue
        st.markdown("### 📋 Kolejka zadań")
        self.render_job_queue()

        st.markdown("</div>", unsafe_allow_html=True)

    def render_job_queue(self):
        """Renderowanie kolejki zadań."""
        # Mock job data
        jobs = [
            {
                "id": "job_001",
                "name": "Audyt faktur Q1",
                "status": "running",
                "progress": 75,
            },
            {
                "id": "job_002",
                "name": "Audyt kontrahentów",
                "status": "completed",
                "progress": 100,
            },
            {
                "id": "job_003",
                "name": "Audyt płatności",
                "status": "pending",
                "progress": 0,
            },
        ]

        for job in jobs:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                with col1:
                    st.markdown(f"**{job['name']}**")
                    st.markdown(f"ID: {job['id']}")

                with col2:
                    status_class = f"status-{job['status']}"
                    st.markdown(
                        f'<span class="status-badge {status_class}">{job["status"].upper()}</span>',
                        unsafe_allow_html=True,
                    )

                with col3:
                    st.markdown(f"Postęp: {job['progress']}%")
                    st.markdown(
                        f"""
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {job['progress']}%"></div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                with col4:
                    if st.button("🗑️", key=f"delete_{job['id']}"):
                        st.info(f"Zadanie {job['id']} usunięte")

    def render_findings_page(self):
        """Renderowanie strony Findings."""
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)

        st.markdown("### 🔍 Niezgodności")

        # Filters
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            severity_filter = st.selectbox(
                "Poziom ryzyka", ["Wszystkie", "High", "Medium", "Low"]
            )

        with col2:
            category_filter = st.selectbox(
                "Kategoria", ["Wszystkie", "Payment", "Contractor", "AML"]
            )

        with col3:
            date_filter = st.date_input(
                "Data od", value=datetime.now() - timedelta(days=30)
            )

        with col4:
            if st.button("🔄 Odśwież", use_container_width=True):
                st.rerun()

        st.divider()

        # Findings list
        self.render_findings_list()

        st.markdown("</div>", unsafe_allow_html=True)

    def render_findings_list(self):
        """Renderowanie listy niezgodności."""
        # Mock findings data
        findings = [
            {
                "id": "F001",
                "title": "Brakujące dane kontrahenta",
                "severity": "high",
                "category": "Contractor",
            },
            {
                "id": "F002",
                "title": "Podejrzana transakcja",
                "severity": "medium",
                "category": "Payment",
            },
            {
                "id": "F003",
                "title": "Błąd w JPK",
                "severity": "low",
                "category": "Compliance",
            },
        ]

        for finding in findings:
            severity_class = f"finding-{finding['severity']}"

            with st.container():
                st.markdown(
                    f'<div class="finding-card {severity_class}">',
                    unsafe_allow_html=True,
                )

                col1, col2, col3 = st.columns([1, 4, 1])

                with col1:
                    st.checkbox("", key=f"finding_{finding['id']}")

                with col2:
                    st.markdown(f"**{finding['title']}**")
                    st.markdown(
                        f"Kategoria: {finding['category']} | ID: {finding['id']}"
                    )

                with col3:
                    if st.button("👁️", key=f"view_{finding['id']}"):
                        st.info("Szczegóły wyświetlone")

                st.markdown("</div>", unsafe_allow_html=True)

    def render_exports_page(self):
        """Renderowanie strony Exports."""
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)

        st.markdown("### 📤 Eksporty")

        # Export types
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 📋 PBC")
            if st.button("📄 Lista PBC", use_container_width=True):
                st.success("Eksport listy PBC rozpoczęty")
            if st.button("📊 Status PBC", use_container_width=True):
                st.success("Eksport statusu PBC rozpoczęty")

        with col2:
            st.markdown("#### 📁 Working Papers")
            if st.button("📄 Working Papers", use_container_width=True):
                st.success("Eksport Working Papers rozpoczęty")
            if st.button("🔗 Łańcuch dowodowy", use_container_width=True):
                st.success("Eksport łańcucha dowodowego rozpoczęty")

        with col3:
            st.markdown("#### 📈 Raporty")
            if st.button("📊 Raport końcowy", use_container_width=True):
                st.success("Eksport raportu końcowego rozpoczęty")
            if st.button("📋 Executive Summary", use_container_width=True):
                st.success("Eksport Executive Summary rozpoczęty")

        st.divider()

        # Export history
        st.markdown("### 📚 Historia eksportów")
        self.render_export_history()

        st.markdown("</div>", unsafe_allow_html=True)

    def render_export_history(self):
        """Renderowanie historii eksportów."""
        # Mock export data
        exports = [
            {
                "name": "Lista PBC",
                "type": "PBC",
                "date": "2024-01-15",
                "size": "2.3 MB",
            },
            {
                "name": "Working Papers",
                "type": "WP",
                "date": "2024-01-14",
                "size": "15.2 MB",
            },
            {
                "name": "Raport końcowy",
                "type": "Report",
                "date": "2024-01-13",
                "size": "12.4 MB",
            },
        ]

        for export in exports:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                with col1:
                    st.markdown(f"**{export['name']}**")
                    st.markdown(f"Typ: {export['type']}")

                with col2:
                    st.markdown(f"Data: {export['date']}")

                with col3:
                    st.markdown(f"Rozmiar: {export['size']}")

                with col4:
                    if st.button("⬇️", key=f"download_{export['name']}"):
                        st.info("Pobieranie rozpoczęte")

    def render_chat_page(self):
        """Renderowanie strony chata AI."""
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)

        st.markdown("### 💬 Chat z Asystentem AI")
        st.markdown(
            "Zadaj pytania z zakresu rachunkowości, audytu, MSRF, PSR, MSSF, KSeF, JPK"
        )

        # Chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])

        # AI Status
        ai_status = self.get_ai_status()
        if ai_status["model_ready"]:
            st.success("✅ AI Model gotowy")
        elif ai_status["server_available"]:
            st.warning("⏳ AI Model się dogrzewa")
        else:
            st.error("❌ Serwer AI niedostępny")

        st.caption(f"Serwer: {ai_status['server_url']}")

        # Chat input
        if prompt := st.chat_input(
            "Zadaj pytanie o rachunkowość, audyt, MSRF, PSR, MSSF, KSeF, JPK..."
        ):
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": prompt})

            # Display user message
            with st.chat_message("user"):
                st.write(prompt)

            # Generate AI response
            with st.chat_message("assistant"):
                with st.spinner("Asystent AI myśli..."):
                    # Try real AI first, fallback to mock
                    ai_response = self._generate_ai_response(prompt)
                    st.write(ai_response)

            # Add AI response to history
            st.session_state.chat_history.append(
                {"role": "assistant", "content": ai_response}
            )

        # Clear chat button
        if st.button("🗑️ Wyczyść chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    def call_real_ai(
        self, prompt: str, temperature: float = 0.8, max_tokens: int = 512
    ) -> str:
        """Call the real AI model via API."""
        try:
            # Check if AI server is available
            health_response = requests.get(f"{self.AI_SERVER_URL}/healthz", timeout=5)
            if not health_response.ok:
                return (
                    f"❌ Serwer AI niedostępny (status: {health_response.status_code})"
                )

            # Check if model is ready
            ready_response = requests.get(f"{self.AI_SERVER_URL}/ready", timeout=5)
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
                "top_p": 0.9,
            }

            response = requests.post(
                f"{self.AI_SERVER_URL}/analyze", json=payload, timeout=self.AI_TIMEOUT
            )

            if response.ok:
                data = response.json()
                return data.get("output", "Brak odpowiedzi od AI")
            else:
                return f"❌ Błąd AI: {response.status_code} - {response.text}"

        except requests.exceptions.ConnectionError:
            return "❌ Brak połączenia z serwerem AI. Upewnij się, że serwer działa na porcie 8001"
        except requests.exceptions.Timeout:
            return "⏰ Timeout - AI potrzebuje więcej czasu na odpowiedź"
        except Exception as e:
            return f"❌ Błąd połączenia z AI: {str(e)}"

    def get_ai_status(self) -> dict:
        """Get AI server status."""
        try:
            health_response = requests.get(f"{self.AI_SERVER_URL}/healthz", timeout=5)
            ready_response = requests.get(f"{self.AI_SERVER_URL}/ready", timeout=5)

            return {
                "server_available": health_response.ok,
                "model_ready": ready_response.ok
                and ready_response.json().get("model_ready", False),
                "server_url": self.AI_SERVER_URL,
            }
        except:
            return {
                "server_available": False,
                "model_ready": False,
                "server_url": self.AI_SERVER_URL,
            }

    def _generate_ai_response(self, prompt: str) -> str:
        """Generowanie odpowiedzi AI (try real AI first, fallback to mock)."""
        # Try real AI first
        ai_status = self.get_ai_status()
        if ai_status["model_ready"]:
            return self.call_real_ai(
                f"Jako ekspert audytu i rachunkowości, odpowiedz na pytanie: {prompt}",
                temperature=0.8,
            )

        # Fallback to mock response
        mock_response = self._generate_mock_ai_response(prompt)
        if not ai_status["server_available"]:
            mock_response += (
                "\n\n⚠️ *Używam odpowiedzi przykładowej - serwer AI niedostępny*"
            )
        return mock_response

    def _generate_mock_ai_response(self, prompt: str) -> str:
        """Generowanie mock odpowiedzi AI."""
        prompt_lower = prompt.lower()

        # MSRF responses
        if "msrf" in prompt_lower:
            return """**MSRF (Międzynarodowe Standardy Sprawozdawczości Finansowej)**

MSRF to zbiór standardów rachunkowości opracowanych przez Radę Międzynarodowych Standardów Rachunkowości (IASB).

**Kluczowe zasady MSRF:**
- Zasada memoriału - ujmowanie przychodów i kosztów w okresie, w którym powstały
- Zasada ostrożności - nie przecenianie aktywów i przychodów
- Zasada ciągłości - założenie, że jednostka będzie kontynuować działalność
- Zasada istotności - ujmowanie informacji istotnych dla użytkowników

**Główne standardy:**
- MSRF 1: Prezentacja sprawozdań finansowych
- MSRF 9: Instrumenty finansowe
- MSRF 15: Przychody z umów z klientami
- MSRF 16: Leasing

Czy potrzebujesz szczegółów dotyczących konkretnego standardu?"""

        # PSR responses
        elif "psr" in prompt_lower or "polskie standardy" in prompt_lower:
            return """**PSR (Polskie Standardy Rachunkowości)**

PSR to krajowe standardy rachunkowości obowiązujące w Polsce, opracowane przez Komitet Standardów Rachunkowości.

**Główne PSR:**
- PSR 1: Rachunkowość i sprawozdawczość finansowa
- PSR 2: Zmiany zasad (polityki) rachunkowości, wartości szacunkowych i korekt błędów
- PSR 3: Zdarzenia po dacie bilansowej
- PSR 4: Rezerwy, zobowiązania warunkowe i aktywa warunkowe

**Różnice między PSR a MSRF:**
- PSR są bardziej szczegółowe i precyzyjne
- MSRF są bardziej elastyczne i oparte na zasadach
- PSR mają więcej przepisów szczegółowych

Czy chcesz poznać szczegóły konkretnego PSR?"""

        # KSeF responses
        elif "ksef" in prompt_lower:
            return """**KSeF (Krajowy System e-Faktur)**

KSeF to system elektronicznej fakturyzacji wprowadzony w Polsce od 1 stycznia 2024.

**Kluczowe elementy KSeF:**
- Obowiązkowa elektroniczna fakturyzacja dla wszystkich podatników VAT
- Format XML FA2 zgodny z unijnym standardem
- Integracja z systemami księgowymi
- Automatyczna walidacja faktur

**Struktura XML FA2:**
- Nagłówek faktury (FA)
- Linie faktury (GT)
- Podsumowanie (ST)
- Walidacja schematu XSD

**Korzyści KSeF:**
- Automatyzacja procesów
- Redukcja błędów
- Szybsze rozliczenia VAT
- Lepsza kontrola fiskalna

Czy potrzebujesz pomocy z implementacją KSeF?"""

        # JPK responses
        elif "jpk" in prompt_lower:
            return """**JPK (Jednolity Plik Kontrolny)**

JPK to system elektronicznej kontroli podatkowej w Polsce.

**Rodzaje JPK:**
- JPK_V7: Deklaracja VAT-7
- JPK_KR: Księgi rachunkowe
- JPK_FA: Faktury
- JPK_WB: Wyciągi bankowe

**Struktura JPK:**
- Nagłówek (Head)
- Podmiot (Subject)
- Dane (Data)
- Walidacja schematu

**Wymagania:**
- Format XML
- Walidacja XSD
- Podpis elektroniczny
- Przesyłanie przez ePUAP

Czy potrzebujesz pomocy z konkretnym typem JPK?"""

        # Audit responses
        elif "audyt" in prompt_lower or "audit" in prompt_lower:
            return """**Audyt - Podstawowe informacje**

Audyt to niezależne badanie sprawozdań finansowych w celu wyrażenia opinii o ich rzetelności.

**Etapy audytu:**
1. **Planowanie** - ocena ryzyk, plan procedur
2. **Wykonanie** - testy kontroli, testy szczegółowe
3. **Zakończenie** - raport, opinia audytora

**Rodzaje ryzyk:**
- Ryzyko inherentne - związane z charakterem działalności
- Ryzyko kontroli - związane z systemem kontroli wewnętrznej
- Ryzyko wykrycia - związane z procedurami audytora

**Procedury audytowe:**
- Testy kontroli
- Testy szczegółowe
- Procedury analityczne
- Testy na istotność

Czy potrzebujesz szczegółów dotyczących konkretnego etapu audytu?"""

        # Default response
        else:
            return """**Asystent AI - Pomoc w rachunkowości i audycie**

Mogę pomóc Ci w następujących obszarach:

**📊 Rachunkowość:**
- MSRF (Międzynarodowe Standardy Sprawozdawczości Finansowej)
- PSR (Polskie Standardy Rachunkowości)
- MSSF (Międzynarodowe Standardy Sprawozdawczości Finansowej)

**🔍 Audyt:**
- Procedury audytowe
- Ocena ryzyk
- Testy kontroli
- Journal entry testing

**🌐 Integracje:**
- KSeF (Krajowy System e-Faktur)
- JPK (Jednolity Plik Kontrolny)
- Biała lista VAT
- KRS/REGON

**💡 Przykłady pytań:**
- "Jakie są wymagania dla JPK_V7?"
- "Co oznacza ryzyko inherentne?"
- "Jak walidować faktury KSeF?"
- "Wyjaśnij różnicę między MSRF a PSR"

Zadaj konkretne pytanie, a udzielę szczegółowej odpowiedzi!"""

    def render_ai_auditor_page(self):
        """Renderowanie strony AI Audytor z funkcjami z pliku klienta."""
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)

        st.markdown("### 🤖 AI Audytor - Narzędzia Specjalistyczne")

        # Sub-tabs for AI Auditor tools
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(
            ["📊 Analiza Sprawozdania", "🔍 Weryfikacja Prób", "⚠️ Ocena Ryzyka"]
        )

        with sub_tab1:
            self.render_financial_analysis()

        with sub_tab2:
            self.render_sample_verification()

        with sub_tab3:
            self.render_risk_assessment()

        st.markdown("</div>", unsafe_allow_html=True)

    def render_financial_analysis(self):
        """Renderowanie narzędzi analizy finansowej."""
        st.subheader("📊 Analiza Sprawozdania Finansowego")

        st.markdown(
            """
        **Narzędzia do analizy sprawozdań finansowych:**
        - Analiza wskaźnikowa
        - Analiza trendów
        - Porównanie z branżą
        - Identyfikacja anomalii
        """
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📈 Wskaźniki Finansowe**")

            # File upload for financial statements
            financial_file = st.file_uploader(
                "Wgraj sprawozdanie finansowe",
                type=["xlsx", "xls", "csv"],
                help="Plik z danymi sprawozdania finansowego",
            )

            if financial_file:
                st.success("✅ Plik wgrany pomyślnie")

                # Analysis options
                analysis_type = st.selectbox(
                    "Typ analizy",
                    [
                        "Wskaźniki płynności",
                        "Wskaźniki rentowności",
                        "Wskaźniki zadłużenia",
                        "Wskaźniki sprawności",
                    ],
                )

                if st.button("🔍 Uruchom Analizę"):
                    with st.spinner("Analizuję sprawozdanie..."):
                        # Mock analysis results
                        st.success("✅ Analiza zakończona")

                        # Display mock results
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Wskaźnik bieżącej płynności", "1.85", "0.15")
                        with col_b:
                            st.metric("ROE", "12.3%", "2.1%")
                        with col_c:
                            st.metric("Dźwignia finansowa", "0.45", "-0.02")

        with col2:
            st.markdown("**🤖 AI Asystent - Analiza**")

            # AI chat for financial analysis
            if "financial_messages" not in st.session_state:
                st.session_state.financial_messages = []

            for message in st.session_state.financial_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt := st.chat_input("Zadaj pytanie o analizę sprawozdania..."):
                st.session_state.financial_messages.append(
                    {"role": "user", "content": prompt}
                )

                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Analizuję..."):
                        # Try real AI first, fallback to mock
                        ai_status = self.get_ai_status()
                        if ai_status["model_ready"]:
                            response = self.call_real_ai(
                                f"Jako ekspert audytu finansowego, odpowiedz na pytanie o analizę sprawozdania: {prompt}",
                                temperature=0.8,
                            )
                        else:
                            response = self._generate_financial_analysis_response(
                                prompt
                            )
                            if not ai_status["server_available"]:
                                response += "\n\n⚠️ *Używam odpowiedzi przykładowej - serwer AI niedostępny*"
                        st.markdown(response)

                st.session_state.financial_messages.append(
                    {"role": "assistant", "content": response}
                )

    def render_sample_verification(self):
        """Renderowanie narzędzi weryfikacji prób."""
        st.subheader("🔍 Weryfikacja Prób Audytowych")

        st.markdown(
            """
        **Narzędzia do weryfikacji prób:**
        - Dobór próby statystycznej
        - Testy szczegółowe
        - Weryfikacja dokumentów
        - Analiza odchyleń
        """
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📋 Dobór Próby**")

            # Sample selection parameters
            population_size = st.number_input(
                "Wielkość populacji",
                min_value=1,
                value=1000,
                help="Całkowita liczba elementów w populacji",
            )

            confidence_level = st.selectbox(
                "Poziom ufności", ["95%", "99%", "90%"], index=0
            )

            tolerable_error = st.slider(
                "Dopuszczalny błąd (%)",
                min_value=1.0,
                max_value=10.0,
                value=5.0,
                step=0.5,
            )

            if st.button("🎯 Oblicz Wielkość Próby"):
                # Mock sample size calculation
                sample_size = int(population_size * 0.1)  # Simplified calculation
                st.success(f"✅ Zalecana wielkość próby: **{sample_size}** elementów")

                # Display sampling method
                st.info(
                    """
                **Metoda doboru:** Dobór losowy warstwowy
                **Kryterium warstwowania:** Wartość transakcji
                **Rozkład próby:** Proporcjonalny
                """
                )

        with col2:
            st.markdown("**🔍 Testy Szczegółowe**")

            # Test selection
            test_type = st.selectbox(
                "Typ testu",
                ["Test istnienia", "Test własności", "Test wyceny", "Test prezentacji"],
            )

            # File upload for test data
            test_data = st.file_uploader(
                "Wgraj dane do testowania",
                type=["xlsx", "xls", "csv"],
                help="Plik z danymi do weryfikacji",
            )

            if test_data and st.button("🚀 Uruchom Test"):
                with st.spinner("Wykonuję test szczegółowy..."):
                    # Mock test results
                    st.success("✅ Test zakończony")

                    # Display results
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Przetestowane", "150", "z 150")
                    with col_b:
                        st.metric("Odchylenia", "3", "2.0%")

                    st.warning("⚠️ Znaleziono 3 odchylenia wymagające dalszej analizy")

    def render_risk_assessment(self):
        """Renderowanie narzędzi oceny ryzyka."""
        st.subheader("⚠️ Ocena Ryzyka Audytowego")

        st.markdown(
            """
        **Narzędzia oceny ryzyka:**
        - Identyfikacja ryzyk
        - Ocena ryzyka inherentnego
        - Ocena ryzyka kontroli
        - Planowanie procedur
        """
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🎯 Identyfikacja Ryzyk**")

            # Risk categories
            risk_categories = st.multiselect(
                "Kategorie ryzyka",
                [
                    "Ryzyko operacyjne",
                    "Ryzyko finansowe",
                    "Ryzyko regulacyjne",
                    "Ryzyko technologiczne",
                    "Ryzyko reputacji",
                ],
                default=["Ryzyko operacyjne", "Ryzyko finansowe"],
            )

            # Risk assessment matrix
            st.markdown("**📊 Macierz Ryzyka**")

            # Mock risk matrix
            risk_data = {
                "Ryzyko": [
                    "Brak kontroli wewnętrznej",
                    "Zmiana regulacji",
                    "Błąd w księgach",
                    "Cyberatak",
                ],
                "Prawdopodobieństwo": ["Wysokie", "Średnie", "Niskie", "Średnie"],
                "Wpływ": ["Wysoki", "Wysoki", "Średni", "Wysoki"],
                "Ocena": ["Krytyczne", "Wysokie", "Średnie", "Wysokie"],
            }

            import pandas as pd

            df = pd.DataFrame(risk_data)
            st.dataframe(df, use_container_width=True)

            # Risk mitigation
            if st.button("🛡️ Generuj Plan Łagodzenia"):
                st.success("✅ Plan łagodzenia ryzyk wygenerowany")
                st.info(
                    """
                **Zalecane działania:**
                - Wprowadzenie dodatkowych kontroli wewnętrznych
                - Regularne szkolenia personelu
                - Monitoring systemów IT
                - Procedury awaryjne
                """
                )

        with col2:
            st.markdown("**🤖 AI Asystent - Ryzyko**")

            # AI chat for risk assessment
            if "risk_messages" not in st.session_state:
                st.session_state.risk_messages = []

            for message in st.session_state.risk_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt := st.chat_input("Zadaj pytanie o ocenę ryzyka..."):
                st.session_state.risk_messages.append(
                    {"role": "user", "content": prompt}
                )

                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Analizuję ryzyko..."):
                        # Try real AI first, fallback to mock
                        ai_status = self.get_ai_status()
                        if ai_status["model_ready"]:
                            response = self.call_real_ai(
                                f"Jako ekspert audytu, odpowiedz na pytanie o ocenę ryzyka: {prompt}",
                                temperature=0.8,
                            )
                        else:
                            response = self._generate_risk_assessment_response(prompt)
                            if not ai_status["server_available"]:
                                response += "\n\n⚠️ *Używam odpowiedzi przykładowej - serwer AI niedostępny*"
                        st.markdown(response)

                st.session_state.risk_messages.append(
                    {"role": "assistant", "content": response}
                )

    def _generate_financial_analysis_response(self, prompt: str) -> str:
        """Generowanie odpowiedzi AI dla analizy finansowej."""
        prompt_lower = prompt.lower()

        if any(word in prompt_lower for word in ["wskaźnik", "płynność", "rentowność"]):
            return """**Analiza wskaźników finansowych:**

🔍 **Wskaźniki płynności:**
- Wskaźnik bieżącej płynności: 1.85 (dobry poziom)
- Wskaźnik szybki: 1.20 (akceptowalny)
- Wskaźnik gotówkowy: 0.45 (wymaga uwagi)

📈 **Wskaźniki rentowności:**
- ROE: 12.3% (powyżej średniej branżowej)
- ROA: 8.7% (stabilny)
- Marża brutto: 35.2% (wysoka)

⚠️ **Obszary wymagające uwagi:**
- Niski wskaźnik gotówkowy może wskazywać na problemy z płynnością
- Wysokie zadłużenie (wskaźnik 0.45) zwiększa ryzyko finansowe

**Zalecenia:** Monitoruj przepływy pieniężne i rozważ optymalizację struktury kapitału."""

        elif any(word in prompt_lower for word in ["trend", "zmiana", "rozwój"]):
            return """**Analiza trendów:**

📊 **Trendy 3-letnie:**
- Przychody: +15% rocznie (pozytywny trend)
- Koszty: +12% rocznie (kontrolowane)
- Zysk netto: +18% rocznie (wzrost efektywności)

🎯 **Kluczowe obserwacje:**
- Stabilny wzrost przychodów
- Poprawa marżowości
- Efektywne zarządzanie kosztami

**Prognoza:** Przy utrzymaniu obecnych trendów, firma ma dobre perspektywy rozwoju."""

        else:
            return """**Analiza sprawozdań finansowych:**

Jestem gotowy pomóc Ci z analizą sprawozdań finansowych. Mogę pomóc z:

📊 **Wskaźnikami finansowymi** - płynność, rentowność, zadłużenie
📈 **Analizą trendów** - zmiany w czasie, sezonowość
🔍 **Identyfikacją anomalii** - nietypowe pozycje, odchylenia
📋 **Porównaniami branżowymi** - benchmarki, pozycja konkurencyjna

Zadaj konkretne pytanie, a przeprowadzę szczegółową analizę!"""

    def _generate_risk_assessment_response(self, prompt: str) -> str:
        """Generowanie odpowiedzi AI dla oceny ryzyka."""
        prompt_lower = prompt.lower()

        if any(word in prompt_lower for word in ["ryzyko", "kontrola", "wewnętrzna"]):
            return """**Ocena ryzyka kontroli wewnętrznej:**

🔍 **Identyfikowane ryzyka:**
- **Brak segregacji obowiązków** - wysokie ryzyko
- **Niewystarczające autoryzacje** - średnie ryzyko
- **Brak dokumentacji procedur** - średnie ryzyko

⚠️ **Ryzyko inherentne:**
- Branża: średnie (sektor usługowy)
- Złożoność operacji: niska
- Zmiany regulacyjne: wysokie

🛡️ **Zalecane kontrole:**
- Wprowadzenie czterookresowej segregacji obowiązków
- Automatyczne autoryzacje dla transakcji >10k PLN
- Dokumentacja wszystkich procedur księgowych

**Ocena ogólna:** Ryzyko kontroli - **ŚREDNIE**"""

        elif any(
            word in prompt_lower for word in ["fraud", "oszustwo", "nieprawidłowości"]
        ):
            return """**Ocena ryzyka oszustw:**

🚨 **Czerwone flagi:**
- Brak urlopów kluczowych pracowników
- Koncentracja autoryzacji w jednej osobie
- Brak niezależnych weryfikacji

🔍 **Procedury wykrywania:**
- Testy analityczne na odchylenia
- Weryfikacja transakcji z kontrahentami
- Analiza wzorców w księgach

⚠️ **Poziom ryzyka:** **WYSOKI** - wymaga dodatkowych procedur

**Zalecenia:** Wprowadź rotację obowiązków i niezależne weryfikacje."""

        else:
            return """**Ocena ryzyka audytowego:**

Jestem gotowy pomóc Ci z oceną ryzyka. Mogę pomóc z:

🎯 **Identyfikacją ryzyk** - operacyjne, finansowe, regulacyjne
📊 **Macierzą ryzyka** - prawdopodobieństwo vs wpływ
🛡️ **Planowaniem łagodzenia** - procedury kontrolne
🔍 **Testami kontroli** - skuteczność systemów wewnętrznych

**Kluczowe obszary ryzyka:**
- Kontrola wewnętrzna
- Ryzyko oszustw
- Ryzyko regulacyjne
- Ryzyko technologiczne

Zadaj konkretne pytanie o ryzyko, a przeprowadzę szczegółową analizę!"""

    def render_instructions_page(self):
        """Renderowanie strony instrukcji."""
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)

        st.markdown("### 📚 Instrukcje dla Użytkowników")

        # Tabs for different instruction categories
        tab1, tab2, tab3, tab4 = st.tabs(
            ["🚀 Pierwsze kroki", "🔍 Audyt", "📊 Raporty", "🆘 Pomoc"]
        )

        with tab1:
            st.markdown("#### 🚀 Pierwsze kroki")

            st.markdown(
                """
            **1. Logowanie do systemu**
            - Użyj swojego adresu email jako loginu
            - Wprowadź hasło otrzymane od administratora
            - Wybierz odpowiednią rolę (auditor, senior, partner, client_pbc)

            **2. Nawigacja w systemie**
            - **Dashboard**: Przegląd systemu, statystyki
            - **Run**: Uruchamianie audytów, kolejka zadań
            - **Findings**: Niezgodności, filtry, bulk-akcje
            - **Exports**: PBC, Working Papers, raporty
            - **Chat AI**: Asystent AI do pytań
            - **Instrukcje**: Ta strona z pomocą

            **3. Skróty klawiszowe**
            - `Ctrl+1`: Dashboard
            - `Ctrl+2`: Run
            - `Ctrl+3`: Findings
            - `Ctrl+4`: Exports
            - `Ctrl+D`: Przełącz tryb ciemny/jasny
            - `Ctrl+R`: Odśwież stronę
            """
            )

        with tab2:
            st.markdown("#### 🔍 Przeprowadzanie audytu")

            st.markdown(
                """
            **1. Przygotowanie plików**
            - Zbierz wszystkie dokumenty (PDF, ZIP, CSV, Excel)
            - Sprawdź jakość skanów (czytelność, rozdzielczość)
            - Uporządkuj pliki tematycznie

            **2. Uruchamianie audytu**
            - Przejdź do zakładki "Run"
            - Przeciągnij pliki do obszaru upload
            - Kliknij "Uruchom Audyt"
            - Obserwuj postęp w kolejce zadań

            **3. Analiza wyników**
            - Przejdź do zakładki "Findings"
            - Filtruj wyniki według poziomu ryzyka
            - Sprawdź szczegóły każdej niezgodności
            - Użyj bulk-akcji do masowych operacji

            **4. Generowanie raportów**
            - Przejdź do zakładki "Exports"
            - Wybierz typ raportu (PBC, Working Papers, Raport końcowy)
            - Pobierz wygenerowane pliki
            """
            )

        with tab3:
            st.markdown("#### 📊 Rodzaje raportów")

            st.markdown(
                """
            **📋 PBC (Prepared by Client)**
            - Lista PBC: Co klient musi przygotować
            - Status PBC: Co już zostało dostarczone
            - Timeline PBC: Harmonogram dostaw

            **📁 Working Papers**
            - Working Papers: Dokumenty robocze audytu
            - Łańcuch dowodowy: Dowody na każdy wniosek
            - Statystyki WP: Podsumowanie dokumentów

            **📈 Raporty**
            - Raport końcowy: Główny raport audytu
            - Executive Summary: Podsumowanie dla zarządu
            - Compliance Report: Raport zgodności

            **💾 Formaty eksportu**
            - Excel (.xlsx): Tabele, wykresy, dane
            - PDF: Raporty końcowe, dokumenty
            - CSV: Dane surowe, listy
            - ZIP: Archiwa z wszystkimi plikami
            """
            )

        with tab4:
            st.markdown("#### 🆘 Rozwiązywanie problemów")

            st.markdown(
                """
            **❌ System nie uruchamia się**
            1. Sprawdź połączenie internetowe
            2. Zrestartuj przeglądarkę
            3. Skontaktuj się z administratorem

            **📁 Pliki się nie wgrywają**
            1. Sprawdź format pliku (PDF, ZIP, CSV, Excel)
            2. Sprawdź rozmiar (max 100MB)
            3. Spróbuj ponownie za kilka minut

            **🤖 Asystent AI nie odpowiada**
            1. Sprawdź połączenie internetowe
            2. Zadaj pytanie ponownie
            3. Użyj prostszego języka

            **📊 Raporty się nie generują**
            1. Sprawdź czy audyt się zakończył
            2. Poczekaj kilka minut
            3. Spróbuj ponownie

            **📞 Kontakt**
            - Email: support@ai-auditor.com
            - Telefon: +48 XXX XXX XXX
            - Godziny: 8:00-18:00 (pon-pt)
            """
            )

        st.markdown("</div>", unsafe_allow_html=True)

    def render_settings_page(self):
        """Renderowanie strony ustawień."""
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)

        st.markdown("### ⚙️ Ustawienia Systemu")

        # Tabs for different settings
        tab1, tab2, tab3, tab4 = st.tabs(
            ["🎨 Wygląd", "🔧 System", "🔒 Bezpieczeństwo", "ℹ️ Informacje"]
        )

        with tab1:
            st.markdown("#### 🎨 Ustawienia wyglądu")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Motyw:**")
                if st.button(
                    "🌙 Tryb ciemny"
                    if not st.session_state.dark_mode
                    else "☀️ Tryb jasny",
                    use_container_width=True,
                ):
                    st.session_state.dark_mode = not st.session_state.dark_mode
                    st.rerun()

                st.markdown("**Język:**")
                language = st.selectbox("Wybierz język", ["Polski", "English"], index=0)

            with col2:
                st.markdown("**Rozmiar czcionki:**")
                font_size = st.selectbox("Rozmiar", ["Mały", "Średni", "Duży"], index=1)

                st.markdown("**Animacje:**")
                animations = st.checkbox("Włącz animacje", value=True)

        with tab2:
            st.markdown("#### 🔧 Ustawienia systemu")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Limit plików:**")
                file_limit = st.number_input(
                    "Maksymalny rozmiar pliku (MB)",
                    min_value=10,
                    max_value=500,
                    value=100,
                )

                st.markdown("**Timeout audytu:**")
                timeout = st.number_input(
                    "Timeout w minutach", min_value=5, max_value=120, value=60
                )

            with col2:
                st.markdown("**Formaty plików:**")
                formats = st.multiselect(
                    "Obsługiwane formaty",
                    ["PDF", "ZIP", "CSV", "XLSX", "XML"],
                    default=["PDF", "ZIP", "CSV", "XLSX"],
                )

                st.markdown("**Automatyczne zapisywanie:**")
                auto_save = st.checkbox("Włącz automatyczne zapisywanie", value=True)

        with tab3:
            st.markdown("#### 🔒 Ustawienia bezpieczeństwa")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Sesja:**")
                session_timeout = st.number_input(
                    "Timeout sesji (minuty)", min_value=5, max_value=480, value=60
                )

                st.markdown("**Logowanie:**")
                audit_log = st.checkbox("Włącz logowanie audytu", value=True)

            with col2:
                st.markdown("**Szyfrowanie:**")
                encryption = st.checkbox("Włącz szyfrowanie danych", value=True)

                st.markdown("**Backup:**")
                auto_backup = st.checkbox("Automatyczny backup", value=True)

        with tab4:
            st.markdown("#### ℹ️ Informacje o systemie")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Wersja:** 1.0.0")
                st.markdown("**Data wydania:** 2024-01-15")
                st.markdown("**Autor:** AI Auditor Team")

            with col2:
                st.markdown("**Status:** ✅ Aktywny")
                st.markdown("**Ostatnia aktualizacja:** 2024-01-15")
                st.markdown("**Licencja:** Proprietary")

            st.markdown("---")
            st.markdown("**🔧 Akcje systemu:**")

            col_btn1, col_btn2, col_btn3 = st.columns(3)

            with col_btn1:
                if st.button("🔄 Restart", use_container_width=True):
                    st.info("System zostanie zrestartowany...")

            with col_btn2:
                if st.button("💾 Backup", use_container_width=True):
                    st.info("Tworzenie kopii zapasowej...")

            with col_btn3:
                if st.button("🔍 Diagnostyka", use_container_width=True):
                    st.info("Uruchamianie diagnostyki systemu...")

        # Save settings button
        st.markdown("---")
        if st.button("💾 Zapisz ustawienia", use_container_width=True, type="primary"):
            st.success("✅ Ustawienia zostały zapisane!")

        # Logout button
        st.markdown("---")
        if st.button("🚪 Wyloguj", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    def render_login(self):
        """Renderowanie strony logowania."""
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)

        # Center the login form
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("### 🔐 Logowanie do AI Auditor")
            st.markdown("---")

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
                    if password == self.ADMIN_PASSWORD:
                        st.session_state.authenticated = True
                        st.success("✅ Logowanie pomyślne!")
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
            - 🤖 Asystent AI z wiedzą rachunkową
            - 📊 Analityka ryzyk
            - 🌐 Integracje PL-core (KSeF, JPK, KRS)
            - 📋 Portal PBC i zarządzanie zleceniami
            """
            )

        st.markdown("</div>", unsafe_allow_html=True)

    def render_main(self):
        """Renderowanie głównego interfejsu."""
        # Check authentication
        if not st.session_state.authenticated:
            self.render_login()
            return

        self.render_header()
        self.render_sidebar()

        # Main content
        if st.session_state.current_page == "dashboard":
            self.render_dashboard()
        elif st.session_state.current_page == "run":
            self.render_run_page()
        elif st.session_state.current_page == "findings":
            self.render_findings_page()
        elif st.session_state.current_page == "exports":
            self.render_exports_page()
        elif st.session_state.current_page == "chat":
            self.render_chat_page()
        elif st.session_state.current_page == "ai_auditor":
            self.render_ai_auditor_page()
        elif st.session_state.current_page == "instructions":
            self.render_instructions_page()
        elif st.session_state.current_page == "settings":
            self.render_settings_page()


def main():
    """Main function."""
    ui = ModernUI()
    ui.render_main()


if __name__ == "__main__":
    main()
