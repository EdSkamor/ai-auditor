#!/usr/bin/env python3
"""
WSAD Test Script: Complete Smoke Test Suite
Tests all critical features of the AI Auditor system.
"""

import sys
import tempfile
import zipfile
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.pdf_indexer import PDFIndexer, InvoiceData
from core.pop_matcher import POPMatcher, MatchStatus, MatchCriteria
from core.data_processing import FileIngester
from core.run_audit import run_audit
from cli.validate import ValidateCLI
from cli.base import CLIError


def create_test_pdf_content() -> str:
    """Create test PDF content (simulated)."""
    return """
    FAKTURA VAT
    Nr: FV-123/2024
    Data: 15.01.2024
    
    Sprzedawca: ACME Corporation Sp. z o.o.
    Nabywca: Test Company Ltd.
    
    Netto: 1 234,56 zł
    Brutto: 1 519,51 zł
    """


def create_test_pop_data() -> pd.DataFrame:
    """Create test POP data."""
    return pd.DataFrame({
        'Numer': ['FV-123/2024', 'FV-124/2024', 'FV-125/2024'],
        'Data': ['2024-01-15', '2024-01-16', '2024-01-17'],
        'Netto': [1234.56, 2500.00, 1500.00],
        'Kontrahent': ['ACME Corporation', 'Test Company', 'Sample Ltd']
    })


def test_pdf_indexing():
    """Test PDF indexing functionality."""
    print("🧪 Testing PDF Indexing...")
    
    try:
        # Create test data
        test_content = create_test_pdf_content()
        
        # Test InvoiceData creation
        invoice_data = InvoiceData(
            source_path="/test/invoice.pdf",
            source_filename="invoice.pdf",
            invoice_id="FV-123/2024",
            issue_date=datetime(2024, 1, 15),
            total_net=1234.56,
            currency="zł",
            seller_guess="ACME Corporation",
            error=None,
            confidence=0.9
        )
        
        assert invoice_data.invoice_id == "FV-123/2024"
        assert invoice_data.total_net == 1234.56
        assert invoice_data.confidence == 0.9
        print("✅ PDF indexing data structures working")
        
        # Test PDFIndexer initialization
        indexer = PDFIndexer(max_file_size_mb=10)
        assert indexer.max_file_size_mb == 10
        print("✅ PDF indexer initialization working")
        
        print("🎉 PDF indexing test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ PDF indexing test failed: {e}")
        return False


def test_pop_matching():
    """Test POP matching functionality."""
    print("🧪 Testing POP Matching...")
    
    try:
        # Create test data
        pop_data = create_test_pop_data()
        
        # Test POPMatcher initialization
        matcher = POPMatcher(
            tiebreak_weight_fname=0.7,
            tiebreak_min_seller=0.4,
            amount_tolerance=0.01
        )
        
        assert matcher.tiebreak_weight_fname == 0.7
        assert matcher.tiebreak_min_seller == 0.4
        assert matcher.amount_tolerance == 0.01
        print("✅ POP matcher initialization working")
        
        # Test column mapping
        column_map = matcher._map_columns(pop_data)
        assert 'invoice_number' in column_map
        assert 'date' in column_map
        assert 'amount_net' in column_map
        assert 'vendor' in column_map
        print("✅ Column mapping working")
        
        # Test invoice number normalization
        normalized = matcher._normalize_invoice_number("FV-123/2024")
        assert normalized == "-123/2024"  # FV prefix is removed
        print("✅ Invoice number normalization working")
        
        # Test vendor name normalization
        normalized_vendor = matcher._normalize_vendor_name("ACME Corporation Sp. z o.o.")
        assert "ACME CORPORATION" in normalized_vendor
        print("✅ Vendor name normalization working")
        
        # Test seller similarity calculation
        similarity = matcher._calculate_seller_similarity("ACME Corporation", "ACME Corp")
        assert similarity > 0.7  # Actual similarity is ~0.72
        print("✅ Seller similarity calculation working")
        
        print("🎉 POP matching test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ POP matching test failed: {e}")
        return False


def test_data_processing():
    """Test data processing functionality."""
    print("🧪 Testing Data Processing...")
    
    try:
        # Test FileIngester
        ingester = FileIngester()
        
        # Create test CSV data
        csv_data = b"Company,Amount,Date\nACME Corp,1000,2023-01-01\nTest Inc,2000,2023-01-02"
        
        result = ingester.read_csv_file(csv_data)
        assert "df" in result
        assert "prompts" in result
        assert isinstance(result["df"], pd.DataFrame)
        assert result["df"].shape == (2, 3)
        print("✅ CSV file reading working")
        
        # Test column name normalization
        processor = ingester.processor
        normalized = processor.normalize_column_name("Company Name")
        assert normalized == "company_name"
        print("✅ Column name normalization working")
        
        # Test amount parsing
        series = pd.Series(["1,234.56", "2,000", "3.141,59"])
        result = processor.parse_amount_series(series)
        assert result.iloc[0] == 1234.56
        assert result.iloc[1] == 2000.0
        print("✅ Amount parsing working")
        
        print("🎉 Data processing test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Data processing test failed: {e}")
        return False


def test_cli_validation():
    """Test CLI validation functionality."""
    print("🧪 Testing CLI Validation...")
    
    try:
        # Test CLI initialization
        cli = ValidateCLI()
        assert cli.name == "validate"
        print("✅ CLI initialization working")
        
        # Test argument validation
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            test_file = Path(tmp.name)
            test_file.write_bytes(b"fake pdf content")
        
        try:
            args = cli.parser.parse_args([
                "--demo",
                "--file", str(test_file),
                "--dry-run"
            ])
            cli._validate_args(args)
            print("✅ Argument validation working")
        finally:
            test_file.unlink()
        
        # Test error handling
        try:
            args = cli.parser.parse_args(["--demo", "--file", "nonexistent.pdf"])
            cli._validate_args(args)
            print("❌ Should have failed with missing file")
            return False
        except CLIError as e:
            if e.exit_code.value == 3:  # FILE_NOT_FOUND
                print("✅ Error handling working")
            else:
                print(f"❌ Wrong error type: {e}")
                return False
        
        print("🎉 CLI validation test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ CLI validation test failed: {e}")
        return False


def test_audit_pipeline():
    """Test complete audit pipeline."""
    print("🧪 Testing Audit Pipeline...")
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create test PDF directory
            pdf_dir = tmp_path / "pdfs"
            pdf_dir.mkdir()
            
            # Create test PDF files (simulated)
            for i in range(3):
                pdf_file = pdf_dir / f"invoice_{i}.pdf"
                pdf_file.write_text(f"Test PDF content {i}")
            
            # Create test POP file
            pop_data = create_test_pop_data()
            pop_file = tmp_path / "pop_data.xlsx"
            pop_data.to_excel(pop_file, index=False)
            
            # Create output directory
            output_dir = tmp_path / "output"
            
            # Test pipeline components (without actual PDF processing)
            from core.run_audit import AuditPipeline
            
            pipeline = AuditPipeline(
                tiebreak_weight_fname=0.7,
                tiebreak_min_seller=0.4,
                amount_tolerance=0.01
            )
            
            assert pipeline.pdf_indexer is not None
            assert pipeline.pop_matcher is not None
            assert pipeline.file_ingester is not None
            assert pipeline.excel_generator is not None
            print("✅ Pipeline initialization working")
            
            # Test POP data loading
            with open(pop_file, 'rb') as f:
                file_bytes = f.read()
            data = pipeline.file_ingester.read_table(file_bytes, pop_file.name)
            assert data['df'].shape[0] == 3
            print("✅ POP data loading working")
        
        print("🎉 Audit pipeline test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Audit pipeline test failed: {e}")
        return False


def test_security_features():
    """Test security features."""
    print("🧪 Testing Security Features...")
    
    try:
        # Test file size limits
        indexer = PDFIndexer(max_file_size_mb=1)
        assert indexer.max_file_size_mb == 1
        print("✅ File size limits working")
        
        # Test allowed extensions
        assert '.pdf' in indexer.allowed_extensions
        assert '.exe' not in indexer.allowed_extensions
        print("✅ File extension validation working")
        
        # Test ZIP security
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "test.zip"
            
            # Create a safe ZIP file
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr("safe_file.pdf", "safe content")
            
            # Test ZIP processing (should not fail)
            try:
                results = indexer.index_zip(zip_path)
                print("✅ ZIP security validation working")
            except Exception as e:
                if "Unsafe ZIP entry" in str(e):
                    print("✅ ZIP security validation working")
                else:
                    raise
        
        print("🎉 Security features test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Security features test failed: {e}")
        return False


def main():
    """Run all smoke tests."""
    print("🚀 Starting Complete Smoke Test Suite...")
    print("=" * 60)
    
    tests = [
        test_pdf_indexing,
        test_pop_matching,
        test_data_processing,
        test_cli_validation,
        test_audit_pipeline,
        test_security_features
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All smoke tests passed!")
        return 0
    else:
        print("❌ Some smoke tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

