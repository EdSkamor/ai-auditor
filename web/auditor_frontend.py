"""
Front-end dla audytora - minimalistyczny, szybki interfejs.
3 widoki: Run, Findings, Exports
"""

import streamlit as st
import pandas as pd
import json
import zipfile
import io
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from .translations import t, get_language_switcher, translations

# Configure page
st.set_page_config(
    page_title="AI Auditor - Panel Audytora",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with Dark Mode Support
def get_css_theme(is_dark: bool):
    if is_dark:
        return """
        <style>
            .stApp {
                background-color: #0e1117;
                color: #fafafa;
            }
            
            .stApp > div {
                background-color: #0e1117;
            }
            
            .main .block-container {
                background-color: #0e1117;
                color: #fafafa;
            }
            
            /* Sidebar dark mode */
            .css-1d391kg {
                background-color: #1f2937;
            }
            
            .css-1d391kg .css-1v0mbdj {
                background-color: #1f2937;
            }
            
            /* Buttons in dark mode */
            .stButton > button {
                background: linear-gradient(135deg, #00d4aa, #1e3a8a);
                color: #ffffff;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 0.5rem 1rem;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            
            .stButton > button:hover {
                background: linear-gradient(135deg, #00b894, #1e3a8a);
                border-color: #00d4aa;
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(0, 212, 170, 0.3);
            }
            
            .stButton > button:active {
                transform: translateY(0);
            }
            
            /* Primary buttons */
            .stButton > button[kind="primary"] {
                background: linear-gradient(135deg, #00d4aa, #1e3a8a);
                color: #ffffff;
                border: 1px solid #00d4aa;
            }
            
            .stButton > button[kind="primary"]:hover {
                background: linear-gradient(135deg, #00b894, #1e3a8a);
                border-color: #00d4aa;
            }
            
            /* Secondary buttons */
            .stButton > button[kind="secondary"] {
                background: #374151;
                color: #fafafa;
                border: 1px solid #4b5563;
            }
            
            .stButton > button[kind="secondary"]:hover {
                background: #4b5563;
                border-color: #6b7280;
            }
            
            .main-header {
                font-size: 2.5rem;
                font-weight: bold;
                color: #00d4aa;
                text-align: center;
                margin-bottom: 2rem;
            }
            
            .view-header {
                font-size: 1.8rem;
                font-weight: bold;
                color: #fafafa;
                margin-bottom: 1rem;
                border-bottom: 2px solid #00d4aa;
                padding-bottom: 0.5rem;
            }
            
            .metric-card {
                background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
                padding: 1rem;
                border-radius: 10px;
                color: white;
                text-align: center;
                margin: 0.5rem 0;
            }
            
            .finding-card {
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 1rem;
                margin: 0.5rem 0;
                background-color: #1f2937;
            }
            
            .sidebar-section {
                background-color: #1f2937;
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
            }
            
            /* Selectbox and other inputs */
            .stSelectbox > div > div {
                background-color: #1f2937;
                color: #fafafa;
                border: 1px solid #374151;
            }
            
            .stTextInput > div > div > input {
                background-color: #1f2937;
                color: #fafafa;
                border: 1px solid #374151;
            }
            
            .stTextArea > div > div > textarea {
                background-color: #1f2937;
                color: #fafafa;
                border: 1px solid #374151;
            }
            
            /* File uploader */
            .stFileUploader > div {
                background-color: #1f2937;
                border: 1px solid #374151;
            }
            
            /* Progress bars */
            .stProgress > div > div > div {
                background: linear-gradient(90deg, #00d4aa, #1e3a8a);
            }
            
            /* Metrics */
            .metric-container {
                background-color: #1f2937;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 1rem;
            }
        </style>
        """
    else:
        return """
        <style>
            .main-header {
                font-size: 2.5rem;
                font-weight: bold;
                color: #1f77b4;
                text-align: center;
                margin-bottom: 2rem;
            }
            
            .view-header {
                font-size: 1.8rem;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 1rem;
                border-bottom: 2px solid #3498db;
                padding-bottom: 0.5rem;
            }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
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
    
    .export-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
        margin: 0.25rem;
    }
    
    .export-button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }
    
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .keyboard-shortcut {
        background-color: #e9ecef;
        padding: 0.25rem 0.5rem;
        border-radius: 3px;
        font-family: monospace;
        font-size: 0.8rem;
    }
        </style>
        """


class AuditorFrontend:
    """Front-end dla audytora."""
    
    def __init__(self):
        self.initialize_session_state()
        # Use environment variable for password security
        import os
        self.ADMIN_PASSWORD = os.getenv("AI_AUDITOR_PASSWORD", "admin123")
        
        # Security: Log password usage (without exposing the password)
        if self.ADMIN_PASSWORD == "admin123":
            print("⚠️ WARNING: Using default password. Set AI_AUDITOR_PASSWORD environment variable for security.")
    
    def initialize_session_state(self):
        """Inicjalizacja stanu sesji."""
        if 'current_view' not in st.session_state:
            st.session_state.current_view = 'Run'
        
        if 'dark_mode' not in st.session_state:
            st.session_state.dark_mode = False
        
        if 'audit_jobs' not in st.session_state:
            st.session_state.audit_jobs = []
        
        if 'findings' not in st.session_state:
            st.session_state.findings = []
        
        if 'exports' not in st.session_state:
            st.session_state.exports = []
        
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
    
    @property
    def current_view(self):
        return st.session_state.current_view
    
    @current_view.setter
    def current_view(self, value):
        st.session_state.current_view = value
    
    @property
    def dark_mode(self):
        return st.session_state.dark_mode
    
    @dark_mode.setter
    def dark_mode(self, value):
        st.session_state.dark_mode = value
    
    @property
    def audit_jobs(self):
        return st.session_state.audit_jobs
    
    @property
    def findings(self):
        return st.session_state.findings
    
    @property
    def exports(self):
        return st.session_state.exports
    
    def render_header(self):
        """Renderowanie nagłówka."""
        # Apply theme
        st.markdown(get_css_theme(self.dark_mode), unsafe_allow_html=True)
        st.markdown(f'<div class="main-header">🔍 {t("app_title")}</div>', unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Renderowanie paska bocznego."""
        with st.sidebar:
            st.markdown(f"## 🎛️ {t('control_panel')}")
            
            # Language switcher
            st.markdown(f"### 🌐 {t('language')}")
            get_language_switcher()
            
            # Theme toggle
            st.markdown(f"### 🎨 {t('theme')}")
            dark_text = t('dark_mode_toggle') if not st.session_state.dark_mode else t('light_mode_toggle')
            if st.button(dark_text):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()
            
            # View selection
            st.markdown(f"### 📊 {t('views')}")
            views = {
                f"🏃 {t('run')}": "Run",
                f"🔍 {t('findings')}": "Findings", 
                f"📤 {t('exports')}": "Exports"
            }
            
            for label, view in views.items():
                if st.button(label, key=f"view_{view}"):
                    st.session_state.current_view = view
                    st.rerun()
            
            # Keyboard shortcuts
            st.markdown(f"### ⌨️ {t('keyboard_shortcuts')}")
            st.markdown(f"""
            <div class="sidebar-section">
                <div class="keyboard-shortcut">{t('ctrl_1')}</div> {t('run')}<br>
                <div class="keyboard-shortcut">{t('ctrl_2')}</div> {t('findings')}<br>
                <div class="keyboard-shortcut">{t('ctrl_3')}</div> {t('exports')}<br>
                <div class="keyboard-shortcut">{t('ctrl_u')}</div> {t('upload')}<br>
                <div class="keyboard-shortcut">{t('ctrl_r')}</div> {t('refresh')}<br>
                <div class="keyboard-shortcut">{t('ctrl_d')}</div> {t('dark_mode')}
            </div>
            """, unsafe_allow_html=True)
            
            # Quick stats
            st.markdown(f"### 📈 {t('quick_stats')}")
            self.render_quick_stats()
    
    def render_quick_stats(self):
        """Renderowanie szybkich statystyk."""
        jobs = st.session_state.audit_jobs
        findings = st.session_state.findings
        
        total_jobs = len(jobs)
        running_jobs = len([j for j in jobs if j.get('status') == 'running'])
        completed_jobs = len([j for j in jobs if j.get('status') == 'completed'])
        
        total_findings = len(findings)
        high_findings = len([f for f in findings if f.get('severity') == 'high'])
        medium_findings = len([f for f in findings if f.get('severity') == 'medium'])
        low_findings = len([f for f in findings if f.get('severity') == 'low'])
        
        st.metric(t('total_files'), total_jobs, f"{t('running')}: {running_jobs}")
        st.metric(t('completed'), completed_jobs, f"{t('failed')}: {total_jobs - completed_jobs}")
        st.metric(t('findings'), total_findings, f"{t('high')}: {high_findings}")
        st.metric(t('medium'), medium_findings, f"{t('low')}: {low_findings}")
    
    def render_run_view(self):
        """Renderowanie widoku Run."""
        st.markdown(f'<div class="view-header">🏃 {t("run")} - {t("job_queue")}</div>', unsafe_allow_html=True)
        
        # Upload section
        st.markdown(f"### 📁 {t('upload_files')}")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_files = st.file_uploader(
                t('select_files'),
                type=['pdf', 'zip', 'csv', 'xlsx'],
                accept_multiple_files=True,
                help=f"{t('file_types')} - {t('help')}"
            )
        
        with col2:
            if st.button(t('start_audit'), type="primary"):
                if uploaded_files:
                    self.start_audit_job(uploaded_files)
                else:
                    st.warning(t('select_files'))
        
        # Job queue
        st.markdown(f"### 📋 {t('job_queue')}")
        if st.session_state.audit_jobs:
            self.render_job_queue()
        else:
            st.info(t('no_jobs'))
        
        # Job details
        if st.session_state.audit_jobs:
            st.markdown(f"### 🔍 {t('job_details')}")
            self.render_job_details()
    
    def render_job_queue(self):
        """Renderowanie kolejki zadań."""
        jobs = st.session_state.audit_jobs
        
        for i, job in enumerate(jobs):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{job.get('name', f'Zadanie {i+1}')}**")
                    st.write(f"Pliki: {job.get('file_count', 0)}")
                
                with col2:
                    status = job.get('status', 'pending')
                    status_class = f"status-{status}"
                    st.markdown(f'<span class="status-badge {status_class}">{status.upper()}</span>', unsafe_allow_html=True)
                
                with col3:
                    st.write(f"Postęp: {job.get('progress', 0)}%")
                    st.progress(job.get('progress', 0) / 100)
                
                with col4:
                    if st.button("🗑️", key=f"delete_{i}"):
                        st.session_state.audit_jobs.pop(i)
                        st.rerun()
    
    def render_job_details(self):
        """Renderowanie szczegółów zadania."""
        if not st.session_state.audit_jobs:
            return
        
        selected_job = st.session_state.audit_jobs[0]  # Mock selection
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**Nazwa:** {selected_job.get('name', 'N/A')}")
            st.write(f"**Status:** {selected_job.get('status', 'N/A')}")
            st.write(f"**Utworzone:** {selected_job.get('created_at', 'N/A')}")
            st.write(f"**Pliki:** {selected_job.get('file_count', 0)}")
            st.write(f"**Postęp:** {selected_job.get('progress', 0)}%")
        
        with col2:
            if selected_job.get('status') == 'running':
                if st.button("⏸️ Pauza"):
                    st.info("Zadanie wstrzymane")
                if st.button("⏹️ Stop"):
                    st.info("Zadanie zatrzymane")
            elif selected_job.get('status') == 'completed':
                if st.button("📊 Pokaż wyniki"):
                    st.success("Wyniki załadowane")
            elif selected_job.get('status') == 'failed':
                if st.button("🔄 Ponów"):
                    st.info("Zadanie ponowione")
    
    def render_findings_view(self):
        """Renderowanie widoku Findings."""
        st.markdown('<div class="view-header">🔍 Findings - Karty Niezgodności</div>', unsafe_allow_html=True)
        
        # Filters
        st.markdown("### 🔍 Filtry")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            severity_filter = st.selectbox(
                "Poziom ryzyka",
                ["Wszystkie", "High", "Medium", "Low"],
                key="severity_filter"
            )
        
        with col2:
            category_filter = st.selectbox(
                "Kategoria",
                ["Wszystkie", "Payment", "Contractor", "AML", "Compliance"],
                key="category_filter"
            )
        
        with col3:
            date_filter = st.date_input(
                "Data od",
                value=datetime.now() - timedelta(days=30),
                key="date_filter"
            )
        
        with col4:
            if st.button("🔄 Odśwież"):
                st.rerun()
        
        # Bulk actions
        st.markdown("### ⚡ Bulk Akcje")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✅ Zaznacz wszystkie"):
                st.info("Wszystkie zaznaczone")
        
        with col2:
            if st.button("❌ Odznacz wszystkie"):
                st.info("Wszystkie odznaczone")
        
        with col3:
            if st.button("📝 Eksportuj zaznaczone"):
                st.info("Eksport rozpoczęty")
        
        with col4:
            if st.button("🗑️ Usuń zaznaczone"):
                st.info("Zaznaczone usunięte")
        
        # Findings list
        st.markdown("### 📋 Lista Niezgodności")
        if st.session_state.findings:
            self.render_findings_list()
        else:
            st.info("Brak niezgodności")
    
    def render_findings_list(self):
        """Renderowanie listy niezgodności."""
        findings = st.session_state.findings
        
        for i, finding in enumerate(findings):
            severity = finding.get('severity', 'low')
            severity_class = f"finding-{severity}"
            
            with st.container():
                st.markdown(f'<div class="finding-card {severity_class}">', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 4, 1])
                
                with col1:
                    st.checkbox("", key=f"finding_{i}")
                
                with col2:
                    st.write(f"**{finding.get('title', 'N/A')}**")
                    st.write(f"Kategoria: {finding.get('category', 'N/A')}")
                    st.write(f"Opis: {finding.get('description', 'N/A')}")
                    st.write(f"Data: {finding.get('date', 'N/A')}")
                
                with col3:
                    if st.button("👁️", key=f"view_{i}"):
                        st.info("Szczegóły wyświetlone")
                    if st.button("✏️", key=f"edit_{i}"):
                        st.info("Edycja rozpoczęta")
                    if st.button("🗑️", key=f"delete_{i}"):
                        st.info("Niezgodność usunięta")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    def render_exports_view(self):
        """Renderowanie widoku Exports."""
        st.markdown('<div class="view-header">📤 Exports - PBC/WP/Raporty</div>', unsafe_allow_html=True)
        
        # Export types
        st.markdown("### 📊 Typy Eksportów")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📋 PBC (Prepared by Client)")
            if st.button("📄 Lista PBC", key="export_pbc_list"):
                self.export_pbc_list()
            if st.button("📊 Status PBC", key="export_pbc_status"):
                self.export_pbc_status()
            if st.button("📅 Timeline PBC", key="export_pbc_timeline"):
                self.export_pbc_timeline()
        
        with col2:
            st.markdown("#### 📁 Working Papers")
            if st.button("📄 Working Papers", key="export_wp"):
                self.export_working_papers()
            if st.button("🔗 Łańcuch dowodowy", key="export_chain"):
                self.export_evidence_chain()
            if st.button("📊 Statystyki WP", key="export_wp_stats"):
                self.export_wp_statistics()
        
        with col3:
            st.markdown("#### 📈 Raporty")
            if st.button("📊 Raport końcowy", key="export_final"):
                self.export_final_report()
            if st.button("📋 Executive Summary", key="export_executive"):
                self.export_executive_summary()
            if st.button("📄 Compliance Report", key="export_compliance"):
                self.export_compliance_report()
        
        # Export history
        st.markdown("### 📚 Historia Eksportów")
        if st.session_state.exports:
            self.render_export_history()
        else:
            st.info("Brak eksportów w historii")
    
    def render_export_history(self):
        """Renderowanie historii eksportów."""
        exports = st.session_state.exports
        
        for i, export in enumerate(exports):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{export.get('name', f'Eksport {i+1}')}**")
                    st.write(f"Typ: {export.get('type', 'N/A')}")
                
                with col2:
                    st.write(f"Utworzone: {export.get('created_at', 'N/A')}")
                
                with col3:
                    st.write(f"Rozmiar: {export.get('size', 'N/A')}")
                
                with col4:
                    if st.button("⬇️", key=f"download_{i}"):
                        st.info("Pobieranie rozpoczęte")
    
    def start_audit_job(self, uploaded_files):
        """Uruchomienie zadania audytu."""
        job = {
            'id': f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'name': f"Audyt {len(uploaded_files)} plików",
            'status': 'running',
            'progress': 0,
            'file_count': len(uploaded_files),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'files': [f.name for f in uploaded_files]
        }
        
        st.session_state.audit_jobs.append(job)
        st.success(f"Zadanie audytu uruchomione: {job['name']}")
        
        # Simulate progress
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
        
        # Complete job
        job['status'] = 'completed'
        job['progress'] = 100
        
        # Add mock findings
        self.add_mock_findings()
        
        st.success("Audyt zakończony pomyślnie!")
    
    def add_mock_findings(self):
        """Dodanie przykładowych niezgodności."""
        mock_findings = [
            {
                'id': 'F001',
                'title': 'Brakujące dane kontrahenta',
                'category': 'Contractor',
                'severity': 'high',
                'description': 'Brakuje NIP dla kontrahenta ABC Corp',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'file': 'invoice_001.pdf'
            },
            {
                'id': 'F002',
                'title': 'Podejrzana transakcja',
                'category': 'Payment',
                'severity': 'medium',
                'description': 'Transakcja w weekend o dużej kwocie',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'file': 'payment_002.pdf'
            },
            {
                'id': 'F003',
                'title': 'Błąd w JPK',
                'category': 'Compliance',
                'severity': 'low',
                'description': 'Niezgodność w JPK_V7',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'file': 'jpk_003.xml'
            }
        ]
        
        st.session_state.findings.extend(mock_findings)
    
    def export_pbc_list(self):
        """Eksport listy PBC."""
        st.info("Eksport listy PBC rozpoczęty")
        # Mock export
        export = {
            'name': 'Lista PBC',
            'type': 'PBC',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'size': '2.3 MB'
        }
        st.session_state.exports.append(export)
    
    def export_pbc_status(self):
        """Eksport statusu PBC."""
        st.info("Eksport statusu PBC rozpoczęty")
        # Mock export
        export = {
            'name': 'Status PBC',
            'type': 'PBC',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'size': '1.1 MB'
        }
        st.session_state.exports.append(export)
    
    def export_pbc_timeline(self):
        """Eksport timeline PBC."""
        st.info("Eksport timeline PBC rozpoczęty")
        # Mock export
        export = {
            'name': 'Timeline PBC',
            'type': 'PBC',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'size': '0.8 MB'
        }
        st.session_state.exports.append(export)
    
    def export_working_papers(self):
        """Eksport Working Papers."""
        st.info("Eksport Working Papers rozpoczęty")
        # Mock export
        export = {
            'name': 'Working Papers',
            'type': 'WP',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'size': '15.2 MB'
        }
        st.session_state.exports.append(export)
    
    def export_evidence_chain(self):
        """Eksport łańcucha dowodowego."""
        st.info("Eksport łańcucha dowodowego rozpoczęty")
        # Mock export
        export = {
            'name': 'Łańcuch dowodowy',
            'type': 'WP',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'size': '8.7 MB'
        }
        st.session_state.exports.append(export)
    
    def export_wp_statistics(self):
        """Eksport statystyk WP."""
        st.info("Eksport statystyk WP rozpoczęty")
        # Mock export
        export = {
            'name': 'Statystyki WP',
            'type': 'WP',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'size': '0.5 MB'
        }
        st.session_state.exports.append(export)
    
    def export_final_report(self):
        """Eksport raportu końcowego."""
        st.info("Eksport raportu końcowego rozpoczęty")
        # Mock export
        export = {
            'name': 'Raport końcowy',
            'type': 'Report',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'size': '12.4 MB'
        }
        st.session_state.exports.append(export)
    
    def export_executive_summary(self):
        """Eksport Executive Summary."""
        st.info("Eksport Executive Summary rozpoczęty")
        # Mock export
        export = {
            'name': 'Executive Summary',
            'type': 'Report',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'size': '3.2 MB'
        }
        st.session_state.exports.append(export)
    
    def export_compliance_report(self):
        """Eksport raportu compliance."""
        st.info("Eksport raportu compliance rozpoczęty")
        # Mock export
        export = {
            'name': 'Compliance Report',
            'type': 'Report',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'size': '5.8 MB'
        }
        st.session_state.exports.append(export)
    
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
                password = st.text_input("Hasło", type="password", placeholder="Wprowadź hasło...")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    login_clicked = st.form_submit_button("🔑 Zaloguj", use_container_width=True)
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
            st.info("""
            **AI Auditor** - System audytu faktur i dokumentów księgowych
            
            **Funkcjonalności:**
            - 🔍 Automatyczny audyt faktur
            - 🤖 Asystent AI z wiedzą rachunkową
            - 📊 Analityka ryzyk
            - 🌐 Integracje PL-core (KSeF, JPK, KRS)
            - 📋 Portal PBC i zarządzanie zleceniami
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_main(self):
        """Renderowanie głównego interfejsu."""
        # Check authentication
        if not st.session_state.authenticated:
            self.render_login()
            return
        
        self.render_header()
        self.render_sidebar()
        
        # Main content
        if st.session_state.current_view == 'Run':
            self.render_run_view()
        elif st.session_state.current_view == 'Findings':
            self.render_findings_view()
        elif st.session_state.current_view == 'Exports':
            self.render_exports_view()


def main():
    """Main function."""
    frontend = AuditorFrontend()
    frontend.render_main()


if __name__ == "__main__":
    main()
