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
from .model_interface import ModelInterface

__all__ = [
    "AuditorException",
    "ModelLoadError",
    "ValidationError",
    "FileProcessingError",
    "APIError",
    "ModelInterface",
]
