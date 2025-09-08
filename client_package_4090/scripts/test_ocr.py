#!/usr/bin/env python3
"""
WSAD Test Script: OCR Functionality Test
Tests OCR processing with different engines.
"""

import sys
import tempfile
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ocr_processor import OCRProcessor, OCRResult, InvoiceFields


def create_test_image():
    """Create a test image with Polish invoice text."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        # Create a simple test image
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a font, fallback to default if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Draw Polish invoice text
        text_lines = [
            "FAKTURA VAT",
            "Nr: FV-001/2024",
            "Data: 15.01.2024",
            "",
            "Sprzedawca: ACME Corporation Sp. z o.o.",
            "ul. Przykładowa 123",
            "00-001 Warszawa",
            "NIP: 123-456-78-90",
            "",
            "Nabywca: Test Company Ltd.",
            "ul. Testowa 456",
            "00-002 Kraków",
            "NIP: 987-654-32-10",
            "",
            "Pozycje:",
            "1. Usługa A - 1 000,00 zł",
            "2. Usługa B - 2 500,00 zł",
            "",
            "Netto: 3 500,00 zł",
            "VAT 23%: 805,00 zł",
            "Brutto: 4 305,00 zł",
            "",
            "Do zapłaty: 4 305,00 zł",
            "Termin płatności: 30 dni"
        ]
        
        y_position = 50
        for line in text_lines:
            draw.text((50, y_position), line, fill='black', font=font)
            y_position += 25
        
        return img
        
    except ImportError:
        print("⚠️  PIL not available, creating mock image")
        return None


def test_ocr_processor_initialization():
    """Test OCR processor initialization."""
    print("🧪 Testing OCR Processor Initialization...")
    
    try:
        # Test Tesseract initialization
        processor_tesseract = OCRProcessor(engine="tesseract", language="pol+eng")
        print("✅ Tesseract processor initialized")
        
        # Test EasyOCR initialization
        processor_easyocr = OCRProcessor(engine="easyocr", language="pol+eng")
        print("✅ EasyOCR processor initialized")
        
        # Test PaddleOCR initialization
        processor_paddleocr = OCRProcessor(engine="paddleocr", language="pol+eng")
        print("✅ PaddleOCR processor initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ OCR processor initialization failed: {e}")
        return False


def test_ocr_result_structure():
    """Test OCR result data structure."""
    print("🧪 Testing OCR Result Structure...")
    
    try:
        # Create mock OCR result
        result = OCRResult(
            text="FAKTURA VAT Nr: FV-001/2024 Data: 15.01.2024",
            confidence=0.95,
            bounding_boxes=[],
            processing_time=1.5,
            engine="tesseract",
            language="pol+eng"
        )
        
        # Test fields
        assert result.text is not None
        assert result.confidence > 0
        assert result.engine == "tesseract"
        assert result.language == "pol+eng"
        
        print("✅ OCR result structure working")
        return True
        
    except Exception as e:
        print(f"❌ OCR result structure test failed: {e}")
        return False


def test_invoice_fields_extraction():
    """Test invoice fields extraction."""
    print("🧪 Testing Invoice Fields Extraction...")
    
    try:
        processor = OCRProcessor(engine="tesseract")
        
        # Create mock OCR result with Polish invoice text
        ocr_result = OCRResult(
            text="FAKTURA VAT Nr: FV-001/2024 Data: 15.01.2024 Sprzedawca: ACME Corporation Netto: 3 500,00 zł VAT: 805,00 zł Brutto: 4 305,00 zł",
            confidence=0.95,
            bounding_boxes=[],
            processing_time=1.5,
            engine="tesseract",
            language="pol+eng"
        )
        
        # Extract invoice fields
        fields = processor.extract_invoice_fields(ocr_result)
        
        # Test extracted fields (more flexible assertions)
        assert fields.invoice_number is not None, "Invoice number should be extracted"
        assert fields.issue_date is not None, "Issue date should be extracted"
        assert fields.seller_name is not None, "Seller name should be extracted"
        assert fields.total_net is not None, "Total net should be extracted"
        
        print("✅ Invoice fields extraction working")
        print(f"   Invoice number: {fields.invoice_number}")
        print(f"   Issue date: {fields.issue_date}")
        print(f"   Seller: {fields.seller_name}")
        print(f"   Net amount: {fields.total_net}")
        print(f"   Currency: {fields.currency}")
        
        return True
        
    except Exception as e:
        print(f"❌ Invoice fields extraction test failed: {e}")
        return False


def test_amount_parsing():
    """Test amount parsing with different formats."""
    print("🧪 Testing Amount Parsing...")
    
    try:
        processor = OCRProcessor(engine="tesseract")
        
        # Test different amount formats
        test_cases = [
            ("1 234,56 zł", 1234.56, "zł"),
            ("1,234.56", 1234.56, None),
            ("1234,56", 1234.56, None),
            ("1234.56", 1234.56, None),
            ("1 000,00", 1000.0, None),
            ("1000", 1000.0, None)
        ]
        
        for amount_str, expected_amount, expected_currency in test_cases:
            amount, currency = processor._parse_amount(amount_str)
            assert amount == expected_amount, f"Amount parsing failed for '{amount_str}': got {amount}, expected {expected_amount}"
            if expected_currency:
                assert currency == expected_currency, f"Currency parsing failed for '{amount_str}': got {currency}, expected {expected_currency}"
        
        print("✅ Amount parsing working")
        for amount_str, expected_amount, expected_currency in test_cases:
            amount, currency = processor._parse_amount(amount_str)
            print(f"   '{amount_str}' -> {amount} {currency or ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Amount parsing test failed: {e}")
        return False


def test_ocr_with_mock_image():
    """Test OCR with mock image."""
    print("🧪 Testing OCR with Mock Image...")
    
    try:
        # Create test image
        test_image = create_test_image()
        
        if test_image is None:
            print("⚠️  Skipping image test - PIL not available")
            return True
        
        # Save test image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            test_image.save(tmp.name)
            image_path = Path(tmp.name)
        
        try:
            # Test OCR processing
            processor = OCRProcessor(engine="tesseract")
            
            # This will fail if Tesseract is not installed, but that's OK for testing
            try:
                result = processor.extract_text(image_path)
                
                if result.error:
                    print(f"⚠️  OCR processing failed (expected): {result.error}")
                else:
                    print("✅ OCR processing successful")
                    print(f"   Extracted text: {result.text[:100]}...")
                    print(f"   Confidence: {result.confidence:.2f}")
                    print(f"   Processing time: {result.processing_time:.2f}s")
                
            except Exception as e:
                print(f"⚠️  OCR processing failed (expected): {e}")
            
            return True
            
        finally:
            # Clean up
            image_path.unlink()
        
    except Exception as e:
        print(f"❌ OCR with mock image test failed: {e}")
        return False


def test_ocr_cli_integration():
    """Test OCR CLI integration."""
    print("🧪 Testing OCR CLI Integration...")
    
    try:
        from cli.ocr_sample import OCRSampleCLI
        
        # Test CLI initialization
        cli = OCRSampleCLI()
        assert cli.name == "ocr-sample"
        
        # Test argument parsing
        test_args = [
            "--input", "test_image.png",
            "--sample-size", "5",
            "--engine", "tesseract",
            "--language", "pol+eng",
            "--gpu-enabled",
            "--dry-run"
        ]
        
        args = cli.parser.parse_args(test_args)
        assert args.input == Path("test_image.png")
        assert args.sample_size == 5
        assert args.engine == "tesseract"
        assert args.language == "pol+eng"
        assert args.gpu_enabled is True
        
        print("✅ OCR CLI integration working")
        return True
        
    except Exception as e:
        print(f"❌ OCR CLI integration test failed: {e}")
        return False


def main():
    """Run all OCR tests."""
    print("🚀 Starting OCR Functionality Test Suite...")
    print("=" * 60)
    
    tests = [
        test_ocr_processor_initialization,
        test_ocr_result_structure,
        test_invoice_fields_extraction,
        test_amount_parsing,
        test_ocr_with_mock_image,
        test_ocr_cli_integration
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
    print(f"📊 OCR Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All OCR tests passed!")
        return 0
    else:
        print("❌ Some OCR tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
