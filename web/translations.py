"""
System tłumaczeń dla AI Auditor.
Obsługuje polski i angielski język interfejsu.
"""

from typing import Dict

import streamlit as st


class Translations:
    """Klasa zarządzająca tłumaczeniami."""

    def __init__(self):
        self.translations = {
            "pl": {
                # Nagłówki i tytuły
                "app_title": "AI Auditor - Panel Audytora",
                "app_title_short": "AI Auditor",
                "demo_title": "AI Auditor — Demo",
                # Nawigacja
                "dashboard": "Dashboard",
                "run": "Run",
                "findings": "Findings",
                "exports": "Exports",
                "chat_ai": "Chat AI",
                "instructions": "Instrukcje",
                "settings": "Settings",
                # Panel sterowania
                "control_panel": "Panel Sterowania",
                "theme": "Motyw",
                "views": "Widoki",
                "quick_stats": "Szybkie statystyki",
                "keyboard_shortcuts": "Skróty klawiszowe",
                "logout": "Wyloguj",
                # Motywy
                "dark_mode": "Ciemny",
                "light_mode": "Jasny",
                "dark_mode_toggle": "🌙 Ciemny",
                "light_mode_toggle": "☀️ Jasny",
                # Języki
                "language": "Język",
                "polish": "Polski",
                "english": "English",
                "select_language": "Wybierz język",
                # Status i stany
                "ready": "READY",
                "model_ready": "Model gotowy",
                "model_not_ready": "Model nie gotowy",
                "status": "Status",
                "progress": "Postęp",
                "running": "Uruchomiony",
                "completed": "Zakończony",
                "failed": "Niepowodzenie",
                "pending": "Oczekujący",
                # Akcje
                "refresh": "Odśwież",
                "upload": "Prześlij",
                "download": "Pobierz",
                "delete": "Usuń",
                "edit": "Edytuj",
                "view": "Zobacz",
                "save": "Zapisz",
                "cancel": "Anuluj",
                "confirm": "Potwierdź",
                "run_audit": "Uruchom Audyt",
                "start_audit": "🚀 Uruchom Audyt",
                # Pliki i upload
                "upload_files": "Prześlij pliki",
                "select_files": "Wybierz pliki do audytu",
                "file_types": "PDF, ZIP, CSV, Excel",
                "file_uploaded": "Plik przesłany",
                "file_processing": "Przetwarzanie pliku...",
                "file_error": "Błąd pliku",
                # Zapytania i analiza
                "query": "Zapytanie",
                "prompt": "Prompt",
                "analyze": "Analizuj",
                "send_query": "Wyślij do /analyze",
                "paste_prompt": "Wklej do zapytania",
                "prompts_from_sheet": "Prompty z arkusza",
                "no_prompts": "Brak promptów w arkuszu",
                # Wyniki
                "results": "Wyniki",
                "no_results": "Brak wyniku",
                "waiting": "Czekaj...",
                "processing": "Przetwarzanie...",
                "analysis_complete": "Analiza zakończona",
                # Metryki i statystyki
                "total_files": "Łącznie plików",
                "processed_files": "Przetworzone pliki",
                "matched_files": "Dopasowane pliki",
                "unmatched_files": "Niedopasowane pliki",
                "errors": "Błędy",
                "match_rate": "Wskaźnik dopasowania",
                # Niezgodności
                "findings": "Niezgodności",
                "finding": "Niezgodność",
                "severity": "Poziom ryzyka",
                "category": "Kategoria",
                "description": "Opis",
                "date": "Data",
                "high": "Wysoki",
                "medium": "Średni",
                "low": "Niski",
                "critical": "Krytyczny",
                # Eksporty
                "export": "Eksport",
                "exports": "Eksporty",
                "export_history": "Historia eksportów",
                "pbc": "PBC",
                "working_papers": "Working Papers",
                "reports": "Raporty",
                "final_report": "Raport końcowy",
                "executive_summary": "Executive Summary",
                "compliance_report": "Compliance Report",
                # Chat AI
                "ai_assistant": "Asystent AI",
                "ask_question": "Zadaj pytanie",
                "ai_thinking": "Asystent AI myśli...",
                "clear_chat": "Wyczyść chat",
                # Ustawienia
                "appearance": "Wygląd",
                "system": "System",
                "security": "Bezpieczeństwo",
                "information": "Informacje",
                "font_size": "Rozmiar czcionki",
                "animations": "Animacje",
                "file_limit": "Limit plików",
                "timeout": "Timeout",
                "auto_save": "Automatyczne zapisywanie",
                # Logowanie
                "login": "Logowanie",
                "password": "Hasło",
                "enter_password": "Wprowadź hasło dostępu",
                "login_button": "Zaloguj",
                "login_success": "Logowanie pomyślne!",
                "login_error": "Nieprawidłowe hasło!",
                # Komunikaty
                "success": "Sukces",
                "error": "Błąd",
                "warning": "Ostrzeżenie",
                "info": "Informacja",
                "loading": "Ładowanie...",
                "please_wait": "Proszę czekać...",
                # Skróty klawiszowe
                "ctrl_1": "Ctrl+1",
                "ctrl_2": "Ctrl+2",
                "ctrl_3": "Ctrl+3",
                "ctrl_4": "Ctrl+4",
                "ctrl_d": "Ctrl+D",
                "ctrl_r": "Ctrl+R",
                "ctrl_u": "Ctrl+U",
                # Pomoc
                "help": "Pomoc",
                "documentation": "Dokumentacja",
                "support": "Wsparcie",
                "contact": "Kontakt",
                # Filtry
                "filters": "Filtry",
                "all": "Wszystkie",
                "filter_by": "Filtruj według",
                "date_from": "Data od",
                "date_to": "Data do",
                # Bulk akcje
                "bulk_actions": "Bulk Akcje",
                "select_all": "Zaznacz wszystkie",
                "deselect_all": "Odznacz wszystkie",
                "export_selected": "Eksportuj zaznaczone",
                "delete_selected": "Usuń zaznaczone",
                # Dodatkowe klucze
                "job_queue": "Kolejki i Joby",
                "job_details": "Szczegóły Zadania",
                "no_jobs": "Brak zadań w kolejce",
                "help": "Możesz wybrać wiele plików jednocześnie",
                "completed": "Zakończone",
                "medium": "Średnie",
            },
            "en": {
                # Headers and titles
                "app_title": "AI Auditor - Auditor Panel",
                "app_title_short": "AI Auditor",
                "demo_title": "AI Auditor — Demo",
                # Navigation
                "dashboard": "Dashboard",
                "run": "Run",
                "findings": "Findings",
                "exports": "Exports",
                "chat_ai": "Chat AI",
                "instructions": "Instructions",
                "settings": "Settings",
                # Control panel
                "control_panel": "Control Panel",
                "theme": "Theme",
                "views": "Views",
                "quick_stats": "Quick Statistics",
                "keyboard_shortcuts": "Keyboard Shortcuts",
                "logout": "Logout",
                # Themes
                "dark_mode": "Dark",
                "light_mode": "Light",
                "dark_mode_toggle": "🌙 Dark",
                "light_mode_toggle": "☀️ Light",
                # Languages
                "language": "Language",
                "polish": "Polski",
                "english": "English",
                "select_language": "Select language",
                # Status and states
                "ready": "READY",
                "model_ready": "Model ready",
                "model_not_ready": "Model not ready",
                "status": "Status",
                "progress": "Progress",
                "running": "Running",
                "completed": "Completed",
                "failed": "Failed",
                "pending": "Pending",
                # Actions
                "refresh": "Refresh",
                "upload": "Upload",
                "download": "Download",
                "delete": "Delete",
                "edit": "Edit",
                "view": "View",
                "save": "Save",
                "cancel": "Cancel",
                "confirm": "Confirm",
                "run_audit": "Run Audit",
                "start_audit": "🚀 Run Audit",
                # Files and upload
                "upload_files": "Upload files",
                "select_files": "Select files for audit",
                "file_types": "PDF, ZIP, CSV, Excel",
                "file_uploaded": "File uploaded",
                "file_processing": "Processing file...",
                "file_error": "File error",
                # Queries and analysis
                "query": "Query",
                "prompt": "Prompt",
                "analyze": "Analyze",
                "send_query": "Send to /analyze",
                "paste_prompt": "Paste to query",
                "prompts_from_sheet": "Prompts from sheet",
                "no_prompts": "No prompts in sheet",
                # Results
                "results": "Results",
                "no_results": "No results",
                "waiting": "Waiting...",
                "processing": "Processing...",
                "analysis_complete": "Analysis complete",
                # Metrics and statistics
                "total_files": "Total files",
                "processed_files": "Processed files",
                "matched_files": "Matched files",
                "unmatched_files": "Unmatched files",
                "errors": "Errors",
                "match_rate": "Match rate",
                # Findings
                "findings": "Findings",
                "finding": "Finding",
                "severity": "Risk level",
                "category": "Category",
                "description": "Description",
                "date": "Date",
                "high": "High",
                "medium": "Medium",
                "low": "Low",
                "critical": "Critical",
                # Exports
                "export": "Export",
                "exports": "Exports",
                "export_history": "Export history",
                "pbc": "PBC",
                "working_papers": "Working Papers",
                "reports": "Reports",
                "final_report": "Final report",
                "executive_summary": "Executive Summary",
                "compliance_report": "Compliance Report",
                # Chat AI
                "ai_assistant": "AI Assistant",
                "ask_question": "Ask a question",
                "ai_thinking": "AI Assistant thinking...",
                "clear_chat": "Clear chat",
                # Settings
                "appearance": "Appearance",
                "system": "System",
                "security": "Security",
                "information": "Information",
                "font_size": "Font size",
                "animations": "Animations",
                "file_limit": "File limit",
                "timeout": "Timeout",
                "auto_save": "Auto save",
                # Login
                "login": "Login",
                "password": "Password",
                "enter_password": "Enter access password",
                "login_button": "Login",
                "login_success": "Login successful!",
                "login_error": "Invalid password!",
                # Messages
                "success": "Success",
                "error": "Error",
                "warning": "Warning",
                "info": "Information",
                "loading": "Loading...",
                "please_wait": "Please wait...",
                # Keyboard shortcuts
                "ctrl_1": "Ctrl+1",
                "ctrl_2": "Ctrl+2",
                "ctrl_3": "Ctrl+3",
                "ctrl_4": "Ctrl+4",
                "ctrl_d": "Ctrl+D",
                "ctrl_r": "Ctrl+R",
                "ctrl_u": "Ctrl+U",
                # Help
                "help": "Help",
                "documentation": "Documentation",
                "support": "Support",
                "contact": "Contact",
                # Filters
                "filters": "Filters",
                "all": "All",
                "filter_by": "Filter by",
                "date_from": "Date from",
                "date_to": "Date to",
                # Bulk actions
                "bulk_actions": "Bulk Actions",
                "select_all": "Select all",
                "deselect_all": "Deselect all",
                "export_selected": "Export selected",
                "delete_selected": "Delete selected",
                # Additional keys
                "job_queue": "Job Queues",
                "job_details": "Job Details",
                "no_jobs": "No jobs in queue",
                "help": "You can select multiple files at once",
                "completed": "Completed",
                "medium": "Medium",
            },
        }

    def get_current_language(self) -> str:
        """Pobiera aktualny język z session state."""
        if "language" not in st.session_state:
            st.session_state.language = "pl"  # Domyślnie polski
        return st.session_state.language

    def set_language(self, language: str):
        """Ustawia język w session state."""
        if language in self.translations:
            st.session_state.language = language

    def t(self, key: str) -> str:
        """Pobiera tłumaczenie dla danego klucza."""
        current_lang = self.get_current_language()
        return self.translations.get(current_lang, {}).get(key, key)

    def get_available_languages(self) -> Dict[str, str]:
        """Zwraca dostępne języki."""
        return {
            "pl": self.translations["pl"]["polish"],
            "en": self.translations["en"]["english"],
        }


# Globalna instancja tłumaczeń
translations = Translations()


def t(key: str) -> str:
    """Krótka funkcja do pobierania tłumaczeń."""
    return translations.t(key)


def get_language_switcher():
    """Zwraca komponent przełącznika języka."""
    current_lang = translations.get_current_language()
    available_langs = translations.get_available_languages()

    # Tworzenie selectbox dla języka
    selected_lang = st.selectbox(
        translations.t("select_language"),
        options=list(available_langs.keys()),
        format_func=lambda x: available_langs[x],
        index=list(available_langs.keys()).index(current_lang),
        key="language_selector",
    )

    # Jeśli język się zmienił, zaktualizuj session state
    if selected_lang != current_lang:
        translations.set_language(selected_lang)
        st.rerun()

    return selected_lang
