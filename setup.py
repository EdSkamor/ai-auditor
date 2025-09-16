#!/usr/bin/env python3
"""
Setup script for AI Auditor system.
"""

from setuptools import find_packages, setup

setup(
    name="ai-auditor",
    version="1.0.0",
    description="Production AI Auditor system for invoice validation and audit support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="EdSkamor",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.111",
        "uvicorn[standard]>=0.30",
        "pydantic>=2",
        "pandas>=2.2",
        "numpy>=1.24",
        "openpyxl>=3.1",
        "chardet>=5.2",
        "unidecode>=1.3",
        "python-multipart>=0.0.20",
        "pdfplumber>=0.11",
        "pypdf>=5.0",
        "torch>=2.0",
        "transformers>=4.30",
        "peft>=0.4",
        "bitsandbytes>=0.41",
        "accelerate>=0.20",
        "pytesseract>=0.3.10",
        "easyocr>=1.7.0",
        "rapidfuzz>=3.0",
        "streamlit>=1.28",
        "reportlab>=4.0",
        "xlsxwriter>=3.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4",
            "pytest-cov>=4.1",
            "pytest-asyncio>=0.21",
            "black>=23.0",
            "isort>=5.12",
            "flake8>=6.0",
            "mypy>=1.5",
        ],
        "docs": ["sphinx>=7.0", "sphinx-rtd-theme>=1.3"],
    },
    entry_points={
        "console_scripts": [
            "ai-auditor=cli.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
