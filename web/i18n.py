"""
Simple i18n system for AI Auditor web interface.
Minimal translation system with fallback to keys.
"""

from typing import Dict

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "app_title_short": "AI-Auditor",
        "language": "Language",
        "control_panel": "Control panel",
        "backend_ai": "Backend AI",
        "online": "online",
        "offline": "offline",
        "analyze": "Analyze",
        "upload_files": "Upload files",
        "processing": "Processing...",
        "success": "Success",
        "error": "Error",
        "file_uploaded": "File uploaded successfully",
        "analysis_complete": "Analysis completed",
        "ai_offline": "AI offline or request error",
    },
    "pl": {
        "app_title_short": "AI-Audytor",
        "language": "Język",
        "control_panel": "Panel sterowania",
        "backend_ai": "Backend AI",
        "online": "online",
        "offline": "offline",
        "analyze": "Analizuj",
        "upload_files": "Prześlij pliki",
        "processing": "Przetwarzanie...",
        "success": "Sukces",
        "error": "Błąd",
        "file_uploaded": "Plik przesłany pomyślnie",
        "analysis_complete": "Analiza zakończona",
        "ai_offline": "AI offline lub błąd zapytania",
    },
}

def t(key: str, lang: str = "en") -> str:
    """Simple translation function. Returns key if translation not found."""
    return TRANSLATIONS.get(lang, {}).get(key, key)

def get_language_switcher() -> str:
    """Language switcher component for sidebar."""
    import streamlit as st
    
    if "lang" not in st.session_state:
        st.session_state["lang"] = "pl"
    
    lang = st.sidebar.selectbox(
        label=t("language", st.session_state["lang"]),
        options=["pl", "en"],
        index=0 if st.session_state["lang"] == "pl" else 1,
        key="lang_select",
    )
    
    if lang != st.session_state["lang"]:
        st.session_state["lang"] = lang
        st.rerun()
    
    return lang



