"""
Translations module for AI Auditor
Provides fallback translations and language support
"""


def t(key: str, **kwargs) -> str:
    """
    Translation function with fallback to key itself
    """
    translations = {
        # Basic UI elements
        "app.title": "AI Auditor - Panel Audytora",
        "app.subtitle": "Inteligentny system wsparcia audytu",
        "nav.chat": "💬 Chat AI",
        "nav.analysis": "📊 Analiza",
        "nav.reports": "📋 Raporty",
        "nav.diagnostics": "🔧 Diagnostyka",
        "nav.help": "❓ Pomoc",
        # Status messages
        "status.ai.online": "🤖 AI Online",
        "status.ai.offline": "❌ AI Offline",
        "status.ai.connecting": "🔄 Łączenie z AI...",
        # Error messages
        "error.import": "Błąd importu: {module}",
        "error.connection": "Błąd połączenia z serwerem AI",
        "error.file_not_found": "Plik nie znaleziony: {file}",
        # Success messages
        "success.analysis_complete": "✅ Analiza zakończona",
        "success.file_uploaded": "✅ Plik wgrany pomyślnie",
        "success.report_generated": "✅ Raport wygenerowany",
        # Common actions
        "action.upload": "📁 Wgraj plik",
        "action.analyze": "🔍 Analizuj",
        "action.download": "💾 Pobierz",
        "action.clear": "🗑️ Wyczyść",
        "action.refresh": "🔄 Odśwież",
        # Analysis types
        "analysis.invoice": "Analiza faktur",
        "analysis.balance": "Analiza bilansu",
        "analysis.risk": "Analiza ryzyka",
        "analysis.compliance": "Analiza zgodności",
    }

    # Return translation or fallback to key
    return translations.get(key, key.format(**kwargs) if kwargs else key)


def get_lang() -> str:
    """
    Get current language (always Polish for now)
    """
    return "pl"


def get_available_languages() -> list:
    """
    Get list of available languages
    """
    return ["pl", "en"]
