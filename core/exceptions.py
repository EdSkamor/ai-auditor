"""
Custom exception classes for the AI Auditor system.
Provides consistent error handling across all modules.
"""

from typing import Any, Dict, Optional


class AuditorException(Exception):
    """Base exception for all AI Auditor errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ModelLoadError(AuditorException):
    """Raised when model loading fails."""

    def __init__(self, message: str, model_name: Optional[str] = None):
        super().__init__(message, "MODEL_LOAD_ERROR")
        self.model_name = model_name


class ValidationError(AuditorException):
    """Raised when data validation fails."""

    def __init__(
        self, message: str, field: Optional[str] = None, value: Optional[Any] = None
    ):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        self.value = value


class FileProcessingError(AuditorException):
    """Raised when file processing fails."""

    def __init__(
        self,
        message: str,
        filename: Optional[str] = None,
        file_type: Optional[str] = None,
    ):
        super().__init__(message, "FILE_PROCESSING_ERROR")
        self.filename = filename
        self.file_type = file_type


class APIError(AuditorException):
    """Raised when external API calls fail."""

    def __init__(
        self,
        message: str,
        api_name: Optional[str] = None,
        status_code: Optional[int] = None,
    ):
        super().__init__(message, "API_ERROR")
        self.api_name = api_name
        self.status_code = status_code


class ConfigurationError(AuditorException):
    """Raised when configuration is invalid."""

    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, "CONFIG_ERROR")
        self.config_key = config_key


class SecurityError(AuditorException):
    """Raised when security-related operations fail."""

    def __init__(self, message: str, security_level: Optional[str] = None):
        super().__init__(message, "SECURITY_ERROR")
        self.security_level = security_level


class AuthorizationError(AuditorException):
    """Raised when user authorization fails."""

    def __init__(
        self,
        message: str,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
    ):
        super().__init__(message, "AUTHORIZATION_ERROR")
        self.user_id = user_id
        self.resource = resource


class AuditError(AuditorException):
    """Raised when audit-related operations fail."""

    def __init__(self, message: str, audit_id: Optional[str] = None):
        super().__init__(message, "AUDIT_ERROR")
        self.audit_id = audit_id
