"""
Configuration for AI Auditor web interface.
Single source of truth for AI API settings.
"""

import os

# AI API Configuration
AI_API_BASE = os.getenv("AI_API_BASE", "http://127.0.0.1:8001")
AI_TIMEOUT = float(os.getenv("AI_TIMEOUT", "15"))
AI_HEALTH = os.getenv("AI_HEALTH_PATH", "/healthz")

# UI Configuration
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "pl")
DARK_MODE = os.getenv("DARK_MODE", "false").lower() == "true"

# File Upload Configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "50"))  # MB
ALLOWED_EXTENSIONS = [".pdf", ".xlsx", ".xls", ".csv"]

# Output Configuration
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
LOGS_DIR = os.getenv("LOGS_DIR", "logs")



