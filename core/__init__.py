"""
Core module for AI Auditor system.
Contains parsing, validation, and exception handling.
"""

from .exceptions import (
    APIError,
    AuditorException,
    FileProcessingError,
    ModelLoadError,
    ValidationError,
)

__all__ = [
    "AuditorException",
    "ModelLoadError",
    "ValidationError",
    "FileProcessingError",
    "APIError",
]
