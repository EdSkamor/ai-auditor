"""
AI Auditor Configuration Example
Copy this file to config.py and set your values
"""

import os

# Security Configuration
AI_AUDITOR_PASSWORD = os.getenv("AI_AUDITOR_PASSWORD", "admin123")

# Server Configuration
SERVER_PORT = int(os.getenv("SERVER_PORT", "8501"))
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS", "0.0.0.0")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/ai_auditor.log")

# Database Configuration (if needed)
DATABASE_URL = os.getenv("DATABASE_URL", "")

# API Keys (if needed)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Security Settings
SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "104857600"))  # 100MB

# Feature Flags
ENABLE_DARK_MODE = os.getenv("ENABLE_DARK_MODE", "true").lower() == "true"
ENABLE_MULTILINGUAL = os.getenv("ENABLE_MULTILINGUAL", "true").lower() == "true"
ENABLE_AI_ASSISTANT = os.getenv("ENABLE_AI_ASSISTANT", "true").lower() == "true"

# Default Language
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "pl")

# Security Headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}
