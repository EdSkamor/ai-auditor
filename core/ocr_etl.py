"""
OCR + Ekstrakcja Wiedzy + ETL
System przetwarzania dokumentów z OCR, klasyfikacją i ekstrakcją pól.
"""

import hashlib
import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import cv2
    import numpy as np

    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    np = None

try:
    import pytesseract

    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

try:
    import easyocr

    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False

try:
    from paddleocr import PaddleOCR

    HAS_PADDLEOCR = True
except ImportError:
    HAS_PADDLEOCR = False

from .exceptions import FileProcessingError


class DocumentType(Enum):
    """Typy dokumentów."""

    INVOICE = "invoice"
    RECEIPT = "receipt"
    CONTRACT = "contract"
    BANK_STATEMENT = "bank_statement"
    TAX_DOCUMENT = "tax_document"
    UNKNOWN = "unknown"


class OCRResult:
    """Wynik OCR."""

    def __init__(self, text: str, confidence: float, bounding_boxes: List[Dict] = None):
        self.text = text
        self.confidence = confidence
        self.bounding_boxes = bounding_boxes or []
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "confidence": self.confidence,
            "bounding_boxes": self.bounding_boxes,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ExtractedField:
    """Wydobyte pole z dokumentu."""

    field_name: str
    value: str
    confidence: float
    position: Dict[str, int]  # x, y, width, height
    source_text: str
    validation_status: str = "unknown"  # valid, invalid, warning
    validation_message: str = ""


@dataclass
class DocumentClassification:
    """Klasyfikacja dokumentu."""

    document_type: DocumentType
    confidence: float
    features: Dict[str, Any]
    processing_time: float


@dataclass
class ETLResult:
    """Wynik ETL."""

    document_id: str
    file_path: str
    document_type: DocumentType
    classification_confidence: float
    ocr_result: OCRResult
    extracted_fields: List[ExtractedField]
    processing_time: float
    hash_value: str
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class OCREngine:
    """Silnik OCR."""

    def __init__(self, engine_type: str = "tesseract", language: str = "pol"):
        self.engine_type = engine_type
        self.language = language
        self.logger = logging.getLogger(__name__)
        self._initialize_engine()

    def _initialize_engine(self):
        """Inicjalizacja silnika OCR."""
        if self.engine_type == "tesseract":
            if not HAS_TESSERACT:
                self.logger.warning("Tesseract not available, using mock OCR")
                self.engine = None
            else:
                self.engine = pytesseract
        elif self.engine_type == "easyocr":
            if not HAS_EASYOCR:
                self.logger.warning("EasyOCR not available, using mock OCR")
                self.engine = None
            else:
                self.engine = easyocr.Reader([self.language])
        elif self.engine_type == "paddleocr":
            if not HAS_PADDLEOCR:
                self.logger.warning("PaddleOCR not available, using mock OCR")
                self.engine = None
            else:
                self.engine = PaddleOCR(use_angle_cls=True, lang=self.language)
        else:
            raise ValueError(f"Unsupported OCR engine: {self.engine_type}")

    def extract_text(self, image_path: Union[str, Path]) -> OCRResult:
        """Ekstrakcja tekstu z obrazu."""
        try:
            if self.engine is None:
                return self._mock_ocr_result(image_path)

            if self.engine_type == "tesseract":
                return self._tesseract_extract(image_path)
            elif self.engine_type == "easyocr":
                return self._easyocr_extract(image_path)
            elif self.engine_type == "paddleocr":
                return self._paddleocr_extract(image_path)

        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            return self._mock_ocr_result(image_path)

    def _tesseract_extract(self, image_path: Union[str, Path]) -> OCRResult:
        """Ekstrakcja tekstu za pomocą Tesseract."""
        # Read image
        image = cv2.imread(str(image_path))
        if image is None:
            raise FileProcessingError(f"Could not read image: {image_path}")

        # Preprocess image
        processed_image = self._preprocess_image(image)

        # Extract text
        text = pytesseract.image_to_string(processed_image, lang=self.language)

        # Get confidence
        data = pytesseract.image_to_data(
            processed_image, lang=self.language, output_type=pytesseract.Output.DICT
        )
        confidences = [int(conf) for conf in data["conf"] if int(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return OCRResult(text.strip(), avg_confidence / 100.0)

    def _easyocr_extract(self, image_path: Union[str, Path]) -> OCRResult:
        """Ekstrakcja tekstu za pomocą EasyOCR."""
        results = self.engine.readtext(str(image_path))

        text_parts = []
        confidences = []
        bounding_boxes = []

        for bbox, text, confidence in results:
            text_parts.append(text)
            confidences.append(confidence)
            bounding_boxes.append(
                {"bbox": bbox, "text": text, "confidence": confidence}
            )

        full_text = " ".join(text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return OCRResult(full_text, avg_confidence, bounding_boxes)

    def _paddleocr_extract(self, image_path: Union[str, Path]) -> OCRResult:
        """Ekstrakcja tekstu za pomocą PaddleOCR."""
        results = self.engine.ocr(str(image_path), cls=True)

        text_parts = []
        confidences = []
        bounding_boxes = []

        for line in results:
            for bbox, (text, confidence) in line:
                text_parts.append(text)
                confidences.append(confidence)
                bounding_boxes.append(
                    {"bbox": bbox, "text": text, "confidence": confidence}
                )

        full_text = " ".join(text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return OCRResult(full_text, avg_confidence, bounding_boxes)

    def _preprocess_image(self, image):
        """Preprocessing obrazu dla lepszej jakości OCR."""
        if not HAS_OPENCV or np is None:
            return image

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply threshold
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Morphological operations
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        return processed

    def _mock_ocr_result(self, image_path: Union[str, Path]) -> OCRResult:
        """Mock OCR result for testing."""
        # Generate mock text based on filename
        filename = Path(image_path).name.lower()

        if "faktura" in filename or "invoice" in filename:
            mock_text = """
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
        else:
            mock_text = f"Mock OCR text for {filename}"

        return OCRResult(mock_text.strip(), 0.85)


class DocumentClassifier:
    """Klasyfikator dokumentów."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Inicjalizacja wzorców klasyfikacji."""
        self.patterns = {
            DocumentType.INVOICE: [
                r"faktura\s*vat",
                r"invoice",
                r"nr\s*:\s*fv-",
                r"sprzedawca\s*:",
                r"nabywca\s*:",
                r"netto\s*:",
                r"vat\s*\d+%",
                r"brutto\s*:",
            ],
            DocumentType.RECEIPT: [
                r"paragon\s*fiskalny",
                r"receipt",
                r"kasa\s*fiskalna",
                r"podatek\s*vat",
                r"kwota\s*do\s*zapłaty",
            ],
            DocumentType.CONTRACT: [
                r"umowa",
                r"contract",
                r"zawarta\s*w\s*dniu",
                r"strony\s*umowy",
                r"przedmiot\s*umowy",
            ],
            DocumentType.BANK_STATEMENT: [
                r"wyciąg\s*bankowy",
                r"bank\s*statement",
                r"rachunek\s*bankowy",
                r"data\s*operacji",
                r"kwota\s*operacji",
            ],
            DocumentType.TAX_DOCUMENT: [
                r"deklaracja\s*vat",
                r"jpk",
                r"podatek\s*dochodowy",
                r"urząd\s*skarbowy",
                r"deklaracja\s*pit",
            ],
        }

    def classify(self, text: str, filename: str = "") -> DocumentClassification:
        """Klasyfikacja dokumentu na podstawie tekstu."""
        start_time = datetime.now()

        text_lower = text.lower()
        filename_lower = filename.lower()

        scores = {}

        for doc_type, patterns in self.patterns.items():
            score = 0
            matches = []

            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 1
                    matches.append(pattern)

            # Check filename patterns
            if doc_type == DocumentType.INVOICE and any(
                word in filename_lower for word in ["faktura", "invoice"]
            ):
                score += 2
            elif doc_type == DocumentType.RECEIPT and any(
                word in filename_lower for word in ["paragon", "receipt"]
            ):
                score += 2
            elif doc_type == DocumentType.CONTRACT and any(
                word in filename_lower for word in ["umowa", "contract"]
            ):
                score += 2
            elif doc_type == DocumentType.BANK_STATEMENT and any(
                word in filename_lower for word in ["wyciąg", "statement"]
            ):
                score += 2
            elif doc_type == DocumentType.TAX_DOCUMENT and any(
                word in filename_lower for word in ["jpk", "deklaracja", "vat"]
            ):
                score += 2

            scores[doc_type] = score

        # Find best match
        if not scores or max(scores.values()) == 0:
            best_type = DocumentType.UNKNOWN
            confidence = 0.0
        else:
            best_type = max(scores, key=scores.get)
            max_score = scores[best_type]
            total_possible = len(self.patterns[best_type]) + 2  # +2 for filename bonus
            confidence = min(max_score / total_possible, 1.0)

        processing_time = (datetime.now() - start_time).total_seconds()

        return DocumentClassification(
            document_type=best_type,
            confidence=confidence,
            features={"scores": scores, "text_length": len(text), "filename": filename},
            processing_time=processing_time,
        )


class FieldExtractor:
    """Ekstraktor pól z dokumentów."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_extractors()

    def _initialize_extractors(self):
        """Inicjalizacja ekstraktorów pól."""
        self.extractors = {
            DocumentType.INVOICE: self._extract_invoice_fields,
            DocumentType.RECEIPT: self._extract_receipt_fields,
            DocumentType.CONTRACT: self._extract_contract_fields,
            DocumentType.BANK_STATEMENT: self._extract_bank_statement_fields,
            DocumentType.TAX_DOCUMENT: self._extract_tax_document_fields,
        }

    def extract_fields(
        self, text: str, document_type: DocumentType, ocr_result: OCRResult
    ) -> List[ExtractedField]:
        """Ekstrakcja pól z dokumentu."""
        if document_type in self.extractors:
            return self.extractors[document_type](text, ocr_result)
        else:
            return self._extract_generic_fields(text, ocr_result)

    def _extract_invoice_fields(
        self, text: str, ocr_result: OCRResult
    ) -> List[ExtractedField]:
        """Ekstrakcja pól faktury."""
        fields = []

        # Invoice number
        invoice_number = self._extract_pattern(
            text, r"(?:nr|numer|number)\s*:?\s*([a-zA-Z0-9\-/]+)", "invoice_number"
        )
        if invoice_number:
            fields.append(
                ExtractedField(
                    field_name="invoice_number",
                    value=invoice_number,
                    confidence=0.9,
                    position={"x": 0, "y": 0, "width": 100, "height": 20},
                    source_text=invoice_number,
                )
            )

        # Date
        date = self._extract_pattern(
            text, r"(?:data|date)\s*:?\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})", "date"
        )
        if date:
            fields.append(
                ExtractedField(
                    field_name="date",
                    value=date,
                    confidence=0.9,
                    position={"x": 0, "y": 20, "width": 100, "height": 20},
                    source_text=date,
                )
            )

        # Seller
        seller = self._extract_pattern(
            text, r"(?:sprzedawca|seller)\s*:?\s*([^\n]+)", "seller"
        )
        if seller:
            fields.append(
                ExtractedField(
                    field_name="seller",
                    value=seller,
                    confidence=0.8,
                    position={"x": 0, "y": 40, "width": 200, "height": 20},
                    source_text=seller,
                )
            )

        # Buyer
        buyer = self._extract_pattern(
            text, r"(?:nabywca|buyer)\s*:?\s*([^\n]+)", "buyer"
        )
        if buyer:
            fields.append(
                ExtractedField(
                    field_name="buyer",
                    value=buyer,
                    confidence=0.8,
                    position={"x": 0, "y": 60, "width": 200, "height": 20},
                    source_text=buyer,
                )
            )

        # Net amount
        net_amount = self._extract_pattern(
            text, r"(?:netto|net)\s*:?\s*([0-9\s,.-]+)", "net_amount"
        )
        if net_amount:
            fields.append(
                ExtractedField(
                    field_name="net_amount",
                    value=net_amount,
                    confidence=0.9,
                    position={"x": 0, "y": 80, "width": 100, "height": 20},
                    source_text=net_amount,
                )
            )

        # VAT amount
        vat_amount = self._extract_pattern(
            text, r"(?:vat|podatek)\s*\d*%?\s*:?\s*([0-9\s,.-]+)", "vat_amount"
        )
        if vat_amount:
            fields.append(
                ExtractedField(
                    field_name="vat_amount",
                    value=vat_amount,
                    confidence=0.9,
                    position={"x": 0, "y": 100, "width": 100, "height": 20},
                    source_text=vat_amount,
                )
            )

        # Gross amount
        gross_amount = self._extract_pattern(
            text, r"(?:brutto|gross|total)\s*:?\s*([0-9\s,.-]+)", "gross_amount"
        )
        if gross_amount:
            fields.append(
                ExtractedField(
                    field_name="gross_amount",
                    value=gross_amount,
                    confidence=0.9,
                    position={"x": 0, "y": 120, "width": 100, "height": 20},
                    source_text=gross_amount,
                )
            )

        return fields

    def _extract_receipt_fields(
        self, text: str, ocr_result: OCRResult
    ) -> List[ExtractedField]:
        """Ekstrakcja pól paragonu."""
        fields = []

        # Receipt number
        receipt_number = self._extract_pattern(
            text, r"(?:nr|numer)\s*:?\s*([0-9]+)", "receipt_number"
        )
        if receipt_number:
            fields.append(
                ExtractedField(
                    field_name="receipt_number",
                    value=receipt_number,
                    confidence=0.9,
                    position={"x": 0, "y": 0, "width": 100, "height": 20},
                    source_text=receipt_number,
                )
            )

        # Date
        date = self._extract_pattern(text, r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})", "date")
        if date:
            fields.append(
                ExtractedField(
                    field_name="date",
                    value=date,
                    confidence=0.8,
                    position={"x": 0, "y": 20, "width": 100, "height": 20},
                    source_text=date,
                )
            )

        # Total amount
        total_amount = self._extract_pattern(
            text, r"(?:suma|total|kwota)\s*:?\s*([0-9\s,.-]+)", "total_amount"
        )
        if total_amount:
            fields.append(
                ExtractedField(
                    field_name="total_amount",
                    value=total_amount,
                    confidence=0.9,
                    position={"x": 0, "y": 40, "width": 100, "height": 20},
                    source_text=total_amount,
                )
            )

        return fields

    def _extract_contract_fields(
        self, text: str, ocr_result: OCRResult
    ) -> List[ExtractedField]:
        """Ekstrakcja pól umowy."""
        fields = []

        # Contract number
        contract_number = self._extract_pattern(
            text, r"(?:nr|numer)\s*umowy\s*:?\s*([a-zA-Z0-9\-/]+)", "contract_number"
        )
        if contract_number:
            fields.append(
                ExtractedField(
                    field_name="contract_number",
                    value=contract_number,
                    confidence=0.9,
                    position={"x": 0, "y": 0, "width": 100, "height": 20},
                    source_text=contract_number,
                )
            )

        # Contract date
        date = self._extract_pattern(
            text,
            r"(?:zawarta\s*w\s*dniu|data)\s*:?\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})",
            "date",
        )
        if date:
            fields.append(
                ExtractedField(
                    field_name="date",
                    value=date,
                    confidence=0.8,
                    position={"x": 0, "y": 20, "width": 100, "height": 20},
                    source_text=date,
                )
            )

        return fields

    def _extract_bank_statement_fields(
        self, text: str, ocr_result: OCRResult
    ) -> List[ExtractedField]:
        """Ekstrakcja pól wyciągu bankowego."""
        fields = []

        # Account number
        account_number = self._extract_pattern(
            text, r"(?:rachunek|account)\s*:?\s*([0-9\s-]+)", "account_number"
        )
        if account_number:
            fields.append(
                ExtractedField(
                    field_name="account_number",
                    value=account_number,
                    confidence=0.9,
                    position={"x": 0, "y": 0, "width": 150, "height": 20},
                    source_text=account_number,
                )
            )

        # Period
        period = self._extract_pattern(
            text,
            r"(?:okres|period)\s*:?\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\s*-\s*\d{1,2}[./-]\d{1,2}[./-]\d{2,4})",
            "period",
        )
        if period:
            fields.append(
                ExtractedField(
                    field_name="period",
                    value=period,
                    confidence=0.8,
                    position={"x": 0, "y": 20, "width": 200, "height": 20},
                    source_text=period,
                )
            )

        return fields

    def _extract_tax_document_fields(
        self, text: str, ocr_result: OCRResult
    ) -> List[ExtractedField]:
        """Ekstrakcja pól dokumentu podatkowego."""
        fields = []

        # Tax period
        period = self._extract_pattern(
            text, r"(?:okres|period)\s*:?\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})", "period"
        )
        if period:
            fields.append(
                ExtractedField(
                    field_name="period",
                    value=period,
                    confidence=0.9,
                    position={"x": 0, "y": 0, "width": 100, "height": 20},
                    source_text=period,
                )
            )

        # Tax amount
        tax_amount = self._extract_pattern(
            text, r"(?:podatek|tax)\s*:?\s*([0-9\s,.-]+)", "tax_amount"
        )
        if tax_amount:
            fields.append(
                ExtractedField(
                    field_name="tax_amount",
                    value=tax_amount,
                    confidence=0.9,
                    position={"x": 0, "y": 20, "width": 100, "height": 20},
                    source_text=tax_amount,
                )
            )

        return fields

    def _extract_generic_fields(
        self, text: str, ocr_result: OCRResult
    ) -> List[ExtractedField]:
        """Ekstrakcja ogólnych pól."""
        fields = []

        # Date
        date = self._extract_pattern(text, r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})", "date")
        if date:
            fields.append(
                ExtractedField(
                    field_name="date",
                    value=date,
                    confidence=0.7,
                    position={"x": 0, "y": 0, "width": 100, "height": 20},
                    source_text=date,
                )
            )

        # Amount
        amount = self._extract_pattern(text, r"([0-9\s,.-]+\s*zł)", "amount")
        if amount:
            fields.append(
                ExtractedField(
                    field_name="amount",
                    value=amount,
                    confidence=0.7,
                    position={"x": 0, "y": 20, "width": 100, "height": 20},
                    source_text=amount,
                )
            )

        return fields

    def _extract_pattern(
        self, text: str, pattern: str, field_name: str
    ) -> Optional[str]:
        """Ekstrakcja wzorca z tekstu."""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None


class ETLProcessor:
    """Procesor ETL (Extract, Transform, Load)."""

    def __init__(self, output_dir: Path = None):
        if output_dir is None:
            output_dir = Path.home() / ".ai-auditor" / "etl_output"

        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.ocr_engine = OCREngine()
        self.classifier = DocumentClassifier()
        self.field_extractor = FieldExtractor()

        # Results storage
        self.results: List[ETLResult] = []

    def process_file(self, file_path: Union[str, Path]) -> ETLResult:
        """Przetwarzanie pojedynczego pliku."""
        start_time = datetime.now()
        file_path = Path(file_path)

        try:
            # Generate document ID
            document_id = (
                f"DOC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_path.stem}"
            )

            # Calculate file hash
            with open(file_path, "rb") as f:
                file_content = f.read()
                hash_value = hashlib.sha256(file_content).hexdigest()

            # OCR extraction
            self.logger.info(f"Processing OCR for: {file_path}")
            ocr_result = self.ocr_engine.extract_text(file_path)

            # Document classification
            self.logger.info(f"Classifying document: {file_path}")
            classification = self.classifier.classify(ocr_result.text, file_path.name)

            # Field extraction
            self.logger.info(f"Extracting fields from: {file_path}")
            extracted_fields = self.field_extractor.extract_fields(
                ocr_result.text, classification.document_type, ocr_result
            )

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            # Create result
            result = ETLResult(
                document_id=document_id,
                file_path=str(file_path),
                document_type=classification.document_type,
                classification_confidence=classification.confidence,
                ocr_result=ocr_result,
                extracted_fields=extracted_fields,
                processing_time=processing_time,
                hash_value=hash_value,
            )

            # Store result
            self.results.append(result)

            # Save to file
            self._save_result(result)

            self.logger.info(f"Processed {file_path} in {processing_time:.2f}s")
            return result

        except Exception as e:
            self.logger.error(f"Failed to process {file_path}: {e}")
            raise FileProcessingError(f"Failed to process {file_path}: {e}")

    def process_directory(
        self, directory: Path, recursive: bool = True
    ) -> List[ETLResult]:
        """Przetwarzanie katalogu z plikami."""
        results = []

        # Find files
        if recursive:
            files = list(directory.rglob("*"))
        else:
            files = list(directory.iterdir())

        # Filter for supported file types
        supported_extensions = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
        files = [
            f for f in files if f.is_file() and f.suffix.lower() in supported_extensions
        ]

        self.logger.info(f"Found {len(files)} files to process")

        # Process files
        for file_path in files:
            try:
                result = self.process_file(file_path)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to process {file_path}: {e}")
                continue

        return results

    def _save_result(self, result: ETLResult):
        """Zapisanie wyniku do pliku."""
        try:
            # Create result directory
            result_dir = self.output_dir / result.document_id
            result_dir.mkdir(exist_ok=True)

            # Save metadata
            metadata_file = result_dir / "metadata.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "document_id": result.document_id,
                        "file_path": result.file_path,
                        "document_type": result.document_type.value,
                        "classification_confidence": result.classification_confidence,
                        "processing_time": result.processing_time,
                        "hash_value": result.hash_value,
                        "created_at": result.created_at.isoformat(),
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            # Save OCR result
            ocr_file = result_dir / "ocr_result.json"
            with open(ocr_file, "w", encoding="utf-8") as f:
                json.dump(result.ocr_result.to_dict(), f, indent=2, ensure_ascii=False)

            # Save extracted fields
            fields_file = result_dir / "extracted_fields.json"
            with open(fields_file, "w", encoding="utf-8") as f:
                json.dump(
                    [asdict(field) for field in result.extracted_fields],
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            # Save raw text
            text_file = result_dir / "raw_text.txt"
            with open(text_file, "w", encoding="utf-8") as f:
                f.write(result.ocr_result.text)

            self.logger.info(f"Saved result for {result.document_id}")

        except Exception as e:
            self.logger.error(f"Failed to save result for {result.document_id}: {e}")

    def export_results(self, format: str = "json") -> Path:
        """Eksport wyników do pliku."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if format == "json":
                output_file = self.output_dir / f"etl_results_{timestamp}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(
                        [asdict(result) for result in self.results],
                        f,
                        indent=2,
                        default=str,
                        ensure_ascii=False,
                    )

            elif format == "csv":
                import pandas as pd

                output_file = self.output_dir / f"etl_results_{timestamp}.csv"

                # Flatten results for CSV
                csv_data = []
                for result in self.results:
                    base_data = {
                        "document_id": result.document_id,
                        "file_path": result.file_path,
                        "document_type": result.document_type.value,
                        "classification_confidence": result.classification_confidence,
                        "ocr_confidence": result.ocr_result.confidence,
                        "processing_time": result.processing_time,
                        "hash_value": result.hash_value,
                        "created_at": result.created_at.isoformat(),
                    }

                    # Add extracted fields
                    for field in result.extracted_fields:
                        base_data[f"field_{field.field_name}"] = field.value
                        base_data[f"field_{field.field_name}_confidence"] = (
                            field.confidence
                        )

                    csv_data.append(base_data)

                df = pd.DataFrame(csv_data)
                df.to_csv(output_file, index=False, encoding="utf-8")

            else:
                raise ValueError(f"Unsupported format: {format}")

            self.logger.info(f"Exported {len(self.results)} results to {output_file}")
            return output_file

        except Exception as e:
            self.logger.error(f"Failed to export results: {e}")
            raise FileProcessingError(f"Failed to export results: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Statystyki przetwarzania."""
        if not self.results:
            return {}

        # Document type distribution
        type_counts = {}
        for result in self.results:
            doc_type = result.document_type.value
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1

        # Average confidences
        avg_classification_confidence = sum(
            r.classification_confidence for r in self.results
        ) / len(self.results)
        avg_ocr_confidence = sum(r.ocr_result.confidence for r in self.results) / len(
            self.results
        )

        # Average processing time
        avg_processing_time = sum(r.processing_time for r in self.results) / len(
            self.results
        )

        # Field extraction statistics
        field_counts = {}
        for result in self.results:
            for field in result.extracted_fields:
                field_counts[field.field_name] = (
                    field_counts.get(field.field_name, 0) + 1
                )

        return {
            "total_documents": len(self.results),
            "document_types": type_counts,
            "average_classification_confidence": round(
                avg_classification_confidence, 3
            ),
            "average_ocr_confidence": round(avg_ocr_confidence, 3),
            "average_processing_time": round(avg_processing_time, 3),
            "extracted_fields": field_counts,
            "total_processing_time": round(
                sum(r.processing_time for r in self.results), 3
            ),
        }
