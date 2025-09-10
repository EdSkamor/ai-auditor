"""
Testy dla modułu wstepne_procedury
"""

import json
import tempfile
from pathlib import Path

import pytest

from ai_audytor.validators.wstepne_procedury import (
    FormulaEvaluator,
    eval_formulas,
    parse_wstepne,
    process_wstepne_procedury,
    to_report,
)


class TestWstepneProcedury:
    """Testy dla modułu wstepne_procedury"""

    @pytest.fixture
    def sample_data(self):
        """Przykładowe dane testowe"""
        return {
            "metadata": {
                "source_file": "test.xlsx",
                "sheets_count": 2,
                "sheets": ["Sheet1", "Sheet2"],
            },
            "sheets": {
                "Sheet1": {
                    "name": "Sheet1",
                    "rows": 3,
                    "cols": 3,
                    "data": [
                        {"0": "A1", "1": "B1", "2": "C1"},
                        {"0": "10", "1": "20", "2": "=SUM(A2:B2)"},
                        {"0": "5", "1": "15", "2": "=AVERAGE(A3:B3)"},
                    ],
                    "formulas": {},
                    "named_ranges": {},
                    "data_validations": {},
                    "header_row_absolute": 0,
                },
                "Sheet2": {
                    "name": "Sheet2",
                    "rows": 2,
                    "cols": 2,
                    "data": [
                        {"0": "X1", "1": "Y1"},
                        {"0": "100", "1": '=IF(A2>50, "High", "Low")'},
                    ],
                    "formulas": {},
                    "named_ranges": {},
                    "data_validations": {},
                    "header_row_absolute": 0,
                },
            },
        }

    @pytest.fixture
    def temp_json_file(self, sample_data):
        """Tymczasowy plik JSON z danymi testowymi"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
            return Path(f.name)

    def test_parse_wstepne(self, temp_json_file, sample_data):
        """Test funkcji parse_wstepne"""
        result = parse_wstepne(temp_json_file)

        assert result["metadata"]["sheets_count"] == 2
        assert len(result["sheets"]) == 2
        assert "Sheet1" in result["sheets"]
        assert "Sheet2" in result["sheets"]

        # Sprawdź strukturę arkusza
        sheet1 = result["sheets"]["Sheet1"]
        assert sheet1["rows"] == 3
        assert sheet1["cols"] == 3
        assert len(sheet1["data"]) == 3

        # Cleanup
        temp_json_file.unlink()

    def test_parse_wstepne_file_not_found(self):
        """Test funkcji parse_wstepne z nieistniejącym plikiem"""
        with pytest.raises(Exception):
            parse_wstepne(Path("nonexistent.json"))

    def test_formula_evaluator_sum(self, sample_data):
        """Test ewaluacji funkcji SUM"""
        evaluator = FormulaEvaluator(sample_data)

        # Test SUM z zakresem
        result = evaluator.evaluate_formula("=SUM(A2:B2)")
        assert result == 30.0  # 10 + 20

        # Test SUM z pojedynczymi komórkami
        result = evaluator.evaluate_formula("=SUM(A2,B2)")
        assert result == 30.0  # 10 + 20

    def test_formula_evaluator_average(self, sample_data):
        """Test ewaluacji funkcji AVERAGE"""
        evaluator = FormulaEvaluator(sample_data)

        result = evaluator.evaluate_formula("=AVERAGE(A3:B3)")
        assert result == 10.0  # (5 + 15) / 2

    def test_formula_evaluator_count(self, sample_data):
        """Test ewaluacji funkcji COUNT"""
        evaluator = FormulaEvaluator(sample_data)

        result = evaluator.evaluate_formula("=COUNT(A2:B2)")
        assert result == 2  # 2 komórki z wartościami

    def test_formula_evaluator_if(self, sample_data):
        """Test ewaluacji funkcji IF"""
        evaluator = FormulaEvaluator(sample_data)

        result = evaluator.evaluate_formula('=IF(A2>50, "High", "Low")')
        assert result == "Low"  # 10 < 50

    def test_eval_formulas(self, sample_data):
        """Test funkcji eval_formulas"""
        results = eval_formulas(sample_data)

        assert "evaluated_sheets" in results
        assert "total_formulas" in results
        assert "successful_evaluations" in results
        assert "formula_errors" in results

        # Sprawdź czy formuły zostały ewaluowane
        assert results["total_formulas"] > 0
        assert results["successful_evaluations"] > 0

        # Sprawdź arkusze
        assert "Sheet1" in results["evaluated_sheets"]
        assert "Sheet2" in results["evaluated_sheets"]

    def test_to_report(self, sample_data):
        """Test funkcji to_report"""
        results = eval_formulas(sample_data)
        report = to_report(sample_data, results)

        assert "metadata" in report
        assert "summary" in report
        assert "sheets_summary" in report
        assert "formula_errors" in report

        # Sprawdź podsumowanie
        summary = report["summary"]
        assert summary["total_sheets"] == 2
        assert summary["total_formulas"] > 0
        assert summary["successful_evaluations"] > 0
        assert "success_rate" in summary

        # Sprawdź podsumowanie arkuszy
        assert "Sheet1" in report["sheets_summary"]
        assert "Sheet2" in report["sheets_summary"]

    def test_process_wstepne_procedury(self, temp_json_file):
        """Test głównej funkcji process_wstepne_procedury"""
        result = process_wstepne_procedury(str(temp_json_file))

        assert result["status"] == "success"
        assert "data" in result
        assert "results" in result
        assert "report" in result

        # Sprawdź strukturę danych
        data = result["data"]
        assert data["metadata"]["sheets_count"] == 2

        # Sprawdź wyniki
        results = result["results"]
        assert "evaluated_sheets" in results
        assert "total_formulas" in results

        # Sprawdź raport
        report = result["report"]
        assert "summary" in report
        assert "sheets_summary" in report

        # Cleanup
        temp_json_file.unlink()

    def test_process_wstepne_procedury_error(self):
        """Test funkcji process_wstepne_procedury z błędem"""
        result = process_wstepne_procedury("nonexistent.json")

        assert result["status"] == "error"
        assert "error" in result

    def test_formula_evaluator_unsupported_function(self, sample_data):
        """Test ewaluacji nieobsługiwanej funkcji"""
        evaluator = FormulaEvaluator(sample_data)

        result = evaluator.evaluate_formula("=UNSUPPORTED(A1)")
        assert result == "=UNSUPPORTED(A1)"  # Powinno zwrócić oryginalną formułę

    def test_formula_evaluator_invalid_syntax(self, sample_data):
        """Test ewaluacji formuły z błędną składnią"""
        evaluator = FormulaEvaluator(sample_data)

        result = evaluator.evaluate_formula("=INVALID(")
        assert result == "=INVALID("  # Powinno zwrócić oryginalną formułę

    def test_formula_evaluator_empty_formula(self, sample_data):
        """Test ewaluacji pustej formuły"""
        evaluator = FormulaEvaluator(sample_data)

        result = evaluator.evaluate_formula("")
        assert result == ""

        result = evaluator.evaluate_formula("=")
        assert result == "="


class TestFormulaEvaluatorEdgeCases:
    """Testy przypadków brzegowych dla FormulaEvaluator"""

    @pytest.fixture
    def empty_data(self):
        """Puste dane testowe"""
        return {"metadata": {"sheets_count": 0, "sheets": []}, "sheets": {}}

    def test_empty_data(self, empty_data):
        """Test z pustymi danymi"""
        evaluator = FormulaEvaluator(empty_data)

        result = evaluator.evaluate_formula("=SUM(A1:A10)")
        assert result == 0.0

    def test_invalid_cell_reference(self, empty_data):
        """Test z nieprawidłową referencją komórki"""
        evaluator = FormulaEvaluator(empty_data)

        result = evaluator.evaluate_formula("=SUM(INVALID)")
        assert result == 0.0

    def test_nested_functions(self, empty_data):
        """Test z zagnieżdżonymi funkcjami (nieobsługiwane)"""
        evaluator = FormulaEvaluator(empty_data)

        result = evaluator.evaluate_formula("=SUM(SUM(A1:A2))")
        assert result == "=SUM(SUM(A1:A2))"  # Powinno zwrócić oryginalną formułę


if __name__ == "__main__":
    pytest.main([__file__])
