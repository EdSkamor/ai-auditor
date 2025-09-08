"""
CLI module for AI Auditor system.
Provides command-line interfaces for all major operations.
"""

from .base import BaseCLI, CLIError
from .validate import ValidateCLI
from .ocr_sample import OCRSampleCLI
from .enrich_data import EnrichDataCLI
from .generate_risk_table import GenerateRiskTableCLI
from .build_docs import BuildDocsCLI

__all__ = [
    'BaseCLI',
    'CLIError', 
    'ValidateCLI',
    'OCRSampleCLI',
    'EnrichDataCLI',
    'GenerateRiskTableCLI',
    'BuildDocsCLI'
]

