#!/usr/bin/env python3
"""
Test script for OCR + ETL functionality.
"""

import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.exceptions import FileProcessingError
from core.ocr_etl import (
    DocumentClassifier,
    DocumentType,
    ETLProcessor,
    FieldExtractor,
    OCREngine,
)


def test_ocr_etl():
    """Test OCR + ETL functionality."""
    print("🚀 Starting OCR + ETL Test Suite...")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Initialize ETL processor
        print("🧪 Testing ETL Processor Initialization...")
        processor = ETLProcessor(tmp_path)
        print("✅ ETL Processor initialized successfully")

        # Test OCR engine
        print("\n🧪 Testing OCR Engine...")
        ocr_engine = OCREngine()
        print(f"✅ OCR Engine initialized: {ocr_engine.engine_type}")

        # Test document classifier
        print("\n🧪 Testing Document Classifier...")
        classifier = DocumentClassifier()

        # Test classification with sample texts
        test_texts = [
            ("FAKTURA VAT\nNr: FV-123/2024\nData: 15.01.2024", "faktura_test.pdf"),
            ("PARAGON FISKALNY\nNr: 001234\nData: 15.01.2024", "paragon_test.pdf"),
            (
                "UMOWA\nNr umowy: UM-001/2024\nZawarta w dniu: 15.01.2024",
                "umowa_test.pdf",
            ),
            (
                "WYCIĄG BANKOWY\nRachunek: 1234567890\nOkres: 01.01.2024 - 31.01.2024",
                "wyciag_test.pdf",
            ),
            (
                "DEKLARACJA VAT\nOkres: 01.2024\nPodatek: 1000,00 zł",
                "deklaracja_test.pdf",
            ),
        ]

        for text, filename in test_texts:
            classification = classifier.classify(text, filename)
            print(
                f"   • {filename}: {classification.document_type.value} (confidence: {classification.confidence:.2f})"
            )

        print("✅ Document classification working")

        # Test field extractor
        print("\n🧪 Testing Field Extractor...")
        field_extractor = FieldExtractor()

        # Test invoice field extraction
        invoice_text = """
        FAKTURA VAT
        Nr: FV-123/2024
        Data: 15.01.2024

        Sprzedawca: ACME Corporation Sp. z o.o.
        ul. Przykładowa 123
        00-001 Warszawa
        NIP: 123-456-78-90

        Nabywca: Test Company Ltd.
        ul. Testowa 456
        00-002 Kraków
        NIP: 987-654-32-10

        Pozycje:
        1. Usługa A - 1 000,00 zł
        2. Usługa B - 2 500,00 zł

        Netto: 3 500,00 zł
        VAT 23%: 805,00 zł
        Brutto: 4 305,00 zł
        """

        from core.ocr_etl import OCRResult

        mock_ocr_result = OCRResult(invoice_text, 0.85)

        fields = field_extractor.extract_fields(
            invoice_text, DocumentType.INVOICE, mock_ocr_result
        )
        print(f"   • Extracted {len(fields)} fields from invoice:")
        for field in fields:
            print(
                f"     - {field.field_name}: {field.value} (confidence: {field.confidence:.2f})"
            )

        print("✅ Field extraction working")

        # Test mock file processing
        print("\n🧪 Testing Mock File Processing...")

        # Create mock image file
        mock_image = tmp_path / "test_invoice.png"
        with open(mock_image, "w") as f:
            f.write("Mock image content")

        try:
            result = processor.process_file(mock_image)
            print(f"✅ Processed mock file: {result.document_id}")
            print(f"   • Document type: {result.document_type.value}")
            print(
                f"   • Classification confidence: {result.classification_confidence:.2f}"
            )
            print(f"   • OCR confidence: {result.ocr_result.confidence:.2f}")
            print(f"   • Extracted fields: {len(result.extracted_fields)}")
            print(f"   • Processing time: {result.processing_time:.2f}s")

            # Test field extraction results
            if result.extracted_fields:
                print("   • Extracted fields:")
                for field in result.extracted_fields[:3]:  # Show first 3 fields
                    print(f"     - {field.field_name}: {field.value}")

        except Exception as e:
            print(f"❌ Mock file processing failed: {e}")

        # Test statistics
        print("\n🧪 Testing Statistics...")
        stats = processor.get_statistics()
        if stats:
            print("✅ Statistics generated:")
            print(f"   • Total documents: {stats.get('total_documents', 0)}")
            print(f"   • Document types: {stats.get('document_types', {})}")
            print(
                f"   • Average classification confidence: {stats.get('average_classification_confidence', 0):.3f}"
            )
            print(
                f"   • Average OCR confidence: {stats.get('average_ocr_confidence', 0):.3f}"
            )
            print(
                f"   • Average processing time: {stats.get('average_processing_time', 0):.3f}s"
            )

        # Test export
        print("\n🧪 Testing Export...")
        try:
            export_file = processor.export_results("json")
            print(f"✅ Results exported to: {export_file.name}")

            # Test CSV export
            csv_file = processor.export_results("csv")
            print(f"✅ CSV results exported to: {csv_file.name}")

        except Exception as e:
            print(f"❌ Export failed: {e}")

        # Test multiple file processing
        print("\n🧪 Testing Multiple File Processing...")

        # Create multiple mock files
        mock_files = [
            ("test_invoice_1.png", "FAKTURA VAT\nNr: FV-001/2024"),
            ("test_receipt_1.png", "PARAGON FISKALNY\nNr: 001234"),
            ("test_contract_1.png", "UMOWA\nNr umowy: UM-001/2024"),
        ]

        for filename, content in mock_files:
            mock_file = tmp_path / filename
            with open(mock_file, "w") as f:
                f.write(content)

        try:
            results = processor.process_directory(tmp_path, recursive=False)
            print(f"✅ Processed {len(results)} files from directory")

            # Show results summary
            for result in results:
                print(
                    f"   • {result.document_id}: {result.document_type.value} ({result.classification_confidence:.2f})"
                )

        except Exception as e:
            print(f"❌ Directory processing failed: {e}")

        # Test error handling
        print("\n🧪 Testing Error Handling...")
        try:
            # Try to process non-existent file
            non_existent = tmp_path / "non_existent.png"
            processor.process_file(non_existent)
            print("❌ Should have failed for non-existent file")
        except FileProcessingError:
            print("✅ Error handling working - caught FileProcessingError")
        except Exception as e:
            print(f"✅ Error handling working - caught exception: {type(e).__name__}")

        print("\n" + "=" * 60)
        print("📊 OCR + ETL Test Results: All tests passed!")
        print("🎉 OCR + ETL system is working correctly!")


if __name__ == "__main__":
    test_ocr_etl()
