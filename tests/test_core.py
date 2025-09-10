"""
Tests for core modules.
"""

import json
import tempfile
from pathlib import Path

import pandas as pd

from core.data_processing import DataAnalyzer, DataProcessor, FileIngester
from core.exceptions import (
    AuditorException,
    FileProcessingError,
    ModelLoadError,
    ValidationError,
)
from core.prompt_generator import PromptGenerator


class TestDataProcessor:
    """Test DataProcessor class."""

    def test_normalize_column_name(self):
        """Test column name normalization."""
        processor = DataProcessor()

        assert processor.normalize_column_name("Company Name") == "company_name"
        assert processor.normalize_column_name("Data Dokumentu") == "data_dokumentu"
        assert processor.normalize_column_name("Wartość Netto") == "wartosc_netto"
        assert processor.normalize_column_name("") == "col"
        assert processor.normalize_column_name("   ") == "col"

    def test_deduplicate_column_names(self):
        """Test column name deduplication."""
        processor = DataProcessor()

        names = ["Company", "Company", "Amount", "Company"]
        result = processor.deduplicate_column_names(names)

        assert result == ["company", "company__1", "amount", "company__2"]

    def test_parse_amount_series(self):
        """Test amount series parsing."""
        processor = DataProcessor()

        series = pd.Series(["1,234.56", "2,000", "3.141,59", "invalid"])
        result = processor.parse_amount_series(series)

        assert result.iloc[0] == 1234.56
        assert result.iloc[1] == 2000.0
        assert result.iloc[2] == 3141.59
        assert pd.isna(result.iloc[3])


class TestFileIngester:
    """Test FileIngester class."""

    def test_read_csv_file(self):
        """Test CSV file reading."""
        ingester = FileIngester()

        # Create test CSV data
        csv_data = (
            b"Company,Amount,Date\nACME Corp,1000,2023-01-01\nTest Inc,2000,2023-01-02"
        )

        result = ingester.read_csv_file(csv_data)

        assert "df" in result
        assert "prompts" in result
        assert isinstance(result["df"], pd.DataFrame)
        assert result["df"].shape == (2, 3)
        assert list(result["df"].columns) == ["company", "amount", "date"]

    def test_read_excel_file(self):
        """Test Excel file reading."""
        ingester = FileIngester()

        # Create test Excel data
        df = pd.DataFrame(
            {
                "Company": ["ACME Corp", "Test Inc"],
                "Amount": [1000, 2000],
                "Date": ["2023-01-01", "2023-01-02"],
            }
        )

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            df.to_excel(tmp.name, index=False)
            with open(tmp.name, "rb") as f:
                excel_data = f.read()
            Path(tmp.name).unlink()

        result = ingester.read_excel_file(excel_data)

        assert "df" in result
        assert "prompts" in result
        assert isinstance(result["df"], pd.DataFrame)
        assert result["df"].shape == (2, 3)


class TestDataAnalyzer:
    """Test DataAnalyzer class."""

    def test_analyze_table(self):
        """Test table analysis."""
        analyzer = DataAnalyzer()

        df = pd.DataFrame(
            {
                "data_dokumentu": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "wartosc_netto": ["1000", "2000", "3000"],
                "kontrahent": ["ACME", "Test Inc", "ACME"],
            }
        )

        result = analyzer.analyze_table(df)

        assert "date_col" in result
        assert "amount_col" in result
        assert "counterparty_col" in result
        assert result["date_col"] == "data_dokumentu"
        assert result["amount_col"] == "wartosc_netto"
        assert result["counterparty_col"] == "kontrahent"
        assert "amount_sum" in result
        assert result["amount_sum"] == 6000.0


class TestPromptGenerator:
    """Test PromptGenerator class."""

    def test_fill_template(self):
        """Test template filling."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test template
            template_data = {
                "name": "test_template",
                "prompt_template": "Hello {{name}}, your data is {{data}}",
            }

            template_file = Path(tmpdir) / "test_template.json"
            with open(template_file, "w") as f:
                json.dump(template_data, f)

            generator = PromptGenerator(Path(tmpdir))

            result = generator.fill_template("test_template", name="John", data="123")
            assert result == "Hello John, your data is 123"

    def test_generate_prompt(self):
        """Test prompt generation from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test template
            template_data = {
                "name": "test_template",
                "prompt_template": "Hello {{name}}, your data is {{data}}",
            }

            template_file = Path(tmpdir) / "test_template.json"
            with open(template_file, "w") as f:
                json.dump(template_data, f)

            generator = PromptGenerator()

            data = {"name": "John", "data": "123"}
            result = generator.generate_prompt(str(template_file), data)
            assert result == "Hello John, your data is 123"


class TestExceptions:
    """Test custom exceptions."""

    def test_auditor_exception(self):
        """Test base AuditorException."""
        exc = AuditorException("Test message", "TEST_ERROR")
        assert str(exc) == "[TEST_ERROR] Test message"
        assert exc.error_code == "TEST_ERROR"

    def test_model_load_error(self):
        """Test ModelLoadError."""
        exc = ModelLoadError("Model failed", "test_model")
        assert exc.model_name == "test_model"
        assert exc.error_code == "MODEL_LOAD_ERROR"

    def test_validation_error(self):
        """Test ValidationError."""
        exc = ValidationError("Invalid data", "field_name", "bad_value")
        assert exc.field == "field_name"
        assert exc.value == "bad_value"
        assert exc.error_code == "VALIDATION_ERROR"

    def test_file_processing_error(self):
        """Test FileProcessingError."""
        exc = FileProcessingError("File error", "test.pdf", ".pdf")
        assert exc.filename == "test.pdf"
        assert exc.file_type == ".pdf"
        assert exc.error_code == "FILE_PROCESSING_ERROR"
