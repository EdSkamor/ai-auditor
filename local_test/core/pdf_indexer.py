"""
Production PDF indexing and crawling system.
Handles recursive PDF processing with security and performance optimizations.
"""

import logging
import re
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd

try:
    import pdfplumber
    import pypdf

    HAS_PDF_LIBS = True
except ImportError:
    HAS_PDF_LIBS = False

from .exceptions import FileProcessingError, ValidationError


@dataclass
class InvoiceData:
    """Structured invoice data."""

    source_path: str
    source_filename: str
    invoice_id: Optional[str]
    issue_date: Optional[datetime]
    total_net: Optional[float]
    currency: Optional[str]
    seller_guess: Optional[str]
    error: Optional[str]
    confidence: float = 0.0
    processing_time: float = 0.0


class PDFIndexer:
    """Production PDF indexing system with security and performance optimizations."""

    def __init__(self, max_file_size_mb: int = 50, max_pages: int = 100):
        self.max_file_size_mb = max_file_size_mb
        self.max_pages = max_pages
        self.logger = logging.getLogger(__name__)

        # Security: Allowed file extensions
        self.allowed_extensions = {".pdf"}

        # Invoice patterns (Polish and English)
        self.invoice_patterns = {
            "invoice_id": [
                r"(?:faktura|invoice|fv)\s*[#:]?\s*([a-zA-Z0-9\-/]+)",
                r"(?:nr|no|number)\s*[#:]?\s*([a-zA-Z0-9\-/]+)",
                r"([A-Z]{2,4}[0-9]{4,8})",  # Common invoice formats
            ],
            "date": [
                r"(?:data|date)\s*[#:]?\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})",
                r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})",
            ],
            "amount": [
                r"(?:netto|net|total)\s*[#:]?\s*([0-9\s,.-]+)",
                r"(?:kwota|amount)\s*[#:]?\s*([0-9\s,.-]+)",
                r"([0-9\s,.-]+\s*(?:zł|pln|eur|usd))",
            ],
            "seller": [
                r"(?:sprzedawca|seller|vendor)\s*[#:]?\s*([a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s\-.,&]+)",
                r"(?:firma|company)\s*[#:]?\s*([a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s\-.,&]+)",
            ],
        }

    def _validate_file_security(self, file_path: Path) -> None:
        """Validate file security and size."""
        if not file_path.exists():
            raise FileProcessingError(f"File not found: {file_path}")

        if file_path.suffix.lower() not in self.allowed_extensions:
            raise FileProcessingError(f"Unsupported file type: {file_path.suffix}")

        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            raise FileProcessingError(
                f"File too large: {file_size_mb:.1f}MB > {self.max_file_size_mb}MB"
            )

    def _extract_text_safely(self, file_path: Path) -> str:
        """Extract text from PDF with error handling."""
        if not HAS_PDF_LIBS:
            raise FileProcessingError(
                "PDF libraries not available. Install: pip install pdfplumber pypdf"
            )

        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                # Security: Limit pages processed
                pages_to_process = min(len(pdf.pages), self.max_pages)

                for i, page in enumerate(pdf.pages[:pages_to_process]):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as e:
                        self.logger.warning(
                            f"Error extracting page {i+1} from {file_path}: {e}"
                        )
                        continue

            return text.strip()

        except Exception as e:
            raise FileProcessingError(f"Failed to extract text from {file_path}: {e}")

    def _parse_amount(self, amount_str: str) -> Tuple[Optional[float], Optional[str]]:
        """Parse amount with locale awareness."""
        if not amount_str:
            return None, None

        # Clean the string
        cleaned = re.sub(r"[^\d,.\-\s]", "", amount_str.strip())

        # Extract currency
        currency_match = re.search(r"(zł|pln|eur|usd|€|\$)", amount_str.lower())
        currency = currency_match.group(1) if currency_match else None

        # Handle different number formats
        # Polish: 1 234,56 or 1234,56
        # English: 1,234.56 or 1234.56

        # Remove spaces
        cleaned = cleaned.replace(" ", "")

        # Handle thousands separators
        if "," in cleaned and "." in cleaned:
            # Both present - assume comma is decimal separator
            cleaned = cleaned.replace(",", ".")
        elif "," in cleaned:
            # Only comma - could be decimal or thousands separator
            parts = cleaned.split(",")
            if len(parts) == 2 and len(parts[1]) <= 2:
                # Likely decimal separator
                cleaned = cleaned.replace(",", ".")
            else:
                # Likely thousands separator
                cleaned = cleaned.replace(",", "")

        try:
            amount = float(cleaned)
            return amount, currency
        except ValueError:
            return None, currency

    def _extract_invoice_data(self, text: str, file_path: Path) -> InvoiceData:
        """Extract structured invoice data from text."""
        start_time = datetime.now()

        try:
            # Extract invoice ID
            invoice_id = None
            for pattern in self.invoice_patterns["invoice_id"]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    invoice_id = match.group(1).strip()
                    break

            # Extract date
            issue_date = None
            for pattern in self.invoice_patterns["date"]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    date_str = match.group(1).strip()
                    try:
                        # Try different date formats
                        for fmt in [
                            "%d.%m.%Y",
                            "%d/%m/%Y",
                            "%d-%m-%Y",
                            "%d.%m.%y",
                            "%d/%m/%y",
                        ]:
                            try:
                                issue_date = datetime.strptime(date_str, fmt)
                                break
                            except ValueError:
                                continue
                    except:
                        pass
                    break

            # Extract amount
            total_net = None
            currency = None
            for pattern in self.invoice_patterns["amount"]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    amount_str = match.group(1).strip()
                    total_net, currency = self._parse_amount(amount_str)
                    if total_net is not None:
                        break

            # Extract seller
            seller_guess = None
            for pattern in self.invoice_patterns["seller"]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    seller_guess = match.group(1).strip()
                    break

            # Calculate confidence based on extracted fields
            confidence = 0.0
            if invoice_id:
                confidence += 0.3
            if issue_date:
                confidence += 0.3
            if total_net is not None:
                confidence += 0.3
            if seller_guess:
                confidence += 0.1

            processing_time = (datetime.now() - start_time).total_seconds()

            return InvoiceData(
                source_path=str(file_path),
                source_filename=file_path.name,
                invoice_id=invoice_id,
                issue_date=issue_date,
                total_net=total_net,
                currency=currency,
                seller_guess=seller_guess,
                error=None,
                confidence=confidence,
                processing_time=processing_time,
            )

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return InvoiceData(
                source_path=str(file_path),
                source_filename=file_path.name,
                invoice_id=None,
                issue_date=None,
                total_net=None,
                currency=None,
                seller_guess=None,
                error=str(e),
                confidence=0.0,
                processing_time=processing_time,
            )

    def index_single_pdf(self, file_path: Path) -> InvoiceData:
        """Index a single PDF file."""
        self._validate_file_security(file_path)

        try:
            text = self._extract_text_safely(file_path)
            if not text:
                raise FileProcessingError("No text extracted from PDF")

            return self._extract_invoice_data(text, file_path)

        except Exception as e:
            return InvoiceData(
                source_path=str(file_path),
                source_filename=file_path.name,
                invoice_id=None,
                issue_date=None,
                total_net=None,
                currency=None,
                seller_guess=None,
                error=str(e),
                confidence=0.0,
                processing_time=0.0,
            )

    def index_directory(
        self, directory: Path, recursive: bool = True
    ) -> List[InvoiceData]:
        """Index all PDFs in a directory."""
        if not directory.exists():
            raise FileProcessingError(f"Directory not found: {directory}")

        if not directory.is_dir():
            raise FileProcessingError(f"Path is not a directory: {directory}")

        pdf_files = []
        if recursive:
            pdf_files = list(directory.rglob("*.pdf"))
        else:
            pdf_files = list(directory.glob("*.pdf"))

        self.logger.info(f"Found {len(pdf_files)} PDF files to process")

        results = []
        for i, pdf_file in enumerate(pdf_files, 1):
            try:
                self.logger.info(f"Processing {i}/{len(pdf_files)}: {pdf_file.name}")
                result = self.index_single_pdf(pdf_file)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to process {pdf_file}: {e}")
                results.append(
                    InvoiceData(
                        source_path=str(pdf_file),
                        source_filename=pdf_file.name,
                        error=str(e),
                        confidence=0.0,
                    )
                )

        return results

    def index_zip(
        self, zip_path: Path, extract_to: Optional[Path] = None
    ) -> List[InvoiceData]:
        """Index PDFs from a ZIP file."""
        if not zip_path.exists():
            raise FileProcessingError(f"ZIP file not found: {zip_path}")

        if extract_to is None:
            extract_to = Path(tempfile.mkdtemp(prefix="pdf_indexer_"))

        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                # Security: Validate ZIP contents
                for info in zip_ref.infolist():
                    if info.filename.startswith("/") or ".." in info.filename:
                        raise FileProcessingError(f"Unsafe ZIP entry: {info.filename}")

                zip_ref.extractall(extract_to)

            return self.index_directory(extract_to, recursive=True)

        except zipfile.BadZipFile:
            raise FileProcessingError(f"Invalid ZIP file: {zip_path}")
        except Exception as e:
            raise FileProcessingError(f"Failed to process ZIP file: {e}")
        finally:
            # Cleanup extracted files
            if extract_to.exists() and extract_to != zip_path.parent:
                shutil.rmtree(extract_to, ignore_errors=True)

    def save_to_csv(self, results: List[InvoiceData], output_path: Path) -> None:
        """Save indexing results to CSV."""
        if not results:
            raise ValidationError("No results to save")

        # Convert to DataFrame
        data = []
        for result in results:
            data.append(
                {
                    "source_path": result.source_path,
                    "source_filename": result.source_filename,
                    "invoice_id": result.invoice_id,
                    "issue_date": (
                        result.issue_date.strftime("%Y-%m-%d")
                        if result.issue_date
                        else None
                    ),
                    "total_net": result.total_net,
                    "currency": result.currency,
                    "seller_guess": result.seller_guess,
                    "error": result.error,
                    "confidence": result.confidence,
                    "processing_time": result.processing_time,
                }
            )

        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False, encoding="utf-8")
        self.logger.info(f"Saved {len(results)} results to {output_path}")


# Global instance
_pdf_indexer = PDFIndexer()


def index_pdf(file_path: Path) -> InvoiceData:
    """Convenience function to index a single PDF."""
    return _pdf_indexer.index_single_pdf(file_path)


def index_directory(directory: Path, recursive: bool = True) -> List[InvoiceData]:
    """Convenience function to index a directory."""
    return _pdf_indexer.index_directory(directory, recursive)


def index_zip(zip_path: Path, extract_to: Optional[Path] = None) -> List[InvoiceData]:
    """Convenience function to index a ZIP file."""
    return _pdf_indexer.index_zip(zip_path, extract_to)
