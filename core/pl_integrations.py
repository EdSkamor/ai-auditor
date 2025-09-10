"""
Integracje PL-core - KSeF, JPK, Biała lista VAT, KRS
System integracji z polskimi systemami podatkowymi i rejestrowymi.
"""

import hashlib
import io
import json
import logging
import time
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from cachetools import TTLCache


class IntegrationType(Enum):
    """Typy integracji."""

    KSEF = "ksef"
    JPK = "jpk"
    VAT_WHITELIST = "vat_whitelist"
    KRS = "krs"
    REGON = "regon"
    VIES = "vies"


@dataclass
class KSeFInvoice:
    """Faktura KSeF."""

    invoice_number: str
    issue_date: datetime
    seller_nip: str
    buyer_nip: str
    net_amount: float
    vat_amount: float
    gross_amount: float
    currency: str
    items: List[Dict[str, Any]]
    xml_content: str
    hash_value: str


@dataclass
class JPKDocument:
    """Dokument JPK."""

    document_type: str  # JPK_V7, JPK_KR, JPK_FA
    period: str
    nip: str
    content: str
    validation_status: str
    validation_errors: List[str]
    hash_value: str


@dataclass
class VATWhitelistEntry:
    """Wpis z Białej listy VAT."""

    nip: str
    name: str
    status: str
    account_numbers: List[str]
    registration_date: Optional[datetime]
    last_update: Optional[datetime]


@dataclass
class KRSEntry:
    """Wpis z KRS."""

    krs_number: str
    name: str
    nip: str
    regon: str
    status: str
    registration_date: Optional[datetime]
    address: str
    legal_form: str


@dataclass
class IntegrationResult:
    """Wynik integracji."""

    integration_type: IntegrationType
    success: bool
    data: Any
    error_message: Optional[str]
    processing_time: float
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class KSeFIntegration:
    """Integracja z KSeF (Krajowy System e-Faktur)."""

    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url or "https://ksef.mf.gov.pl/api"
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()

        if self.api_key:
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )

    def import_fa3_zip(self, zip_path: str) -> IntegrationResult:
        """Import faktur FA(3) z pliku ZIP."""
        start_time = time.time()

        try:
            invoices = []
            errors = []

            with zipfile.ZipFile(zip_path, "r") as zip_file:
                for file_info in zip_file.filelist:
                    if file_info.filename.endswith(".xml"):
                        try:
                            # Read XML content
                            xml_content = zip_file.read(file_info.filename).decode(
                                "utf-8"
                            )

                            # Validate and process invoice
                            validation_result = self.validate_invoice_xml(xml_content)

                            if validation_result["valid"]:
                                invoice_data = validation_result["invoice_data"]
                                hash_value = hashlib.sha256(
                                    xml_content.encode()
                                ).hexdigest()

                                invoice = KSeFInvoice(
                                    invoice_number=invoice_data.get(
                                        "invoice_number", ""
                                    ),
                                    issue_date=datetime.fromisoformat(
                                        invoice_data.get("issue_date", "2024-01-01")
                                    ),
                                    seller_nip=invoice_data.get("seller_nip", ""),
                                    buyer_nip=invoice_data.get("buyer_nip", ""),
                                    net_amount=invoice_data.get("net_amount", 0.0),
                                    vat_amount=invoice_data.get("vat_amount", 0.0),
                                    gross_amount=invoice_data.get("gross_amount", 0.0),
                                    currency=invoice_data.get("currency", "PLN"),
                                    items=invoice_data.get("items", []),
                                    xml_content=xml_content,
                                    hash_value=hash_value,
                                )
                                invoices.append(invoice)
                            else:
                                errors.append(
                                    f"{file_info.filename}: {', '.join(validation_result['errors'])}"
                                )

                        except Exception as e:
                            errors.append(f"{file_info.filename}: {str(e)}")

            return IntegrationResult(
                integration_type=IntegrationType.KSEF,
                success=len(invoices) > 0,
                data=invoices,
                error_message=f"Errors: {len(errors)}" if errors else None,
                processing_time=time.time() - start_time,
            )

        except Exception as e:
            return IntegrationResult(
                integration_type=IntegrationType.KSEF,
                success=False,
                data=None,
                error_message=str(e),
                processing_time=time.time() - start_time,
            )

    def import_fa3_from_bytes(self, zip_bytes: bytes) -> IntegrationResult:
        """Import faktur FA(3) z bytes ZIP."""
        start_time = time.time()

        try:
            invoices = []
            errors = []

            with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zip_file:
                for file_info in zip_file.filelist:
                    if file_info.filename.endswith(".xml"):
                        try:
                            # Read XML content
                            xml_content = zip_file.read(file_info.filename).decode(
                                "utf-8"
                            )

                            # Validate and process invoice
                            validation_result = self.validate_invoice_xml(xml_content)

                            if validation_result["valid"]:
                                invoice_data = validation_result["invoice_data"]
                                hash_value = hashlib.sha256(
                                    xml_content.encode()
                                ).hexdigest()

                                invoice = KSeFInvoice(
                                    invoice_number=invoice_data.get(
                                        "invoice_number", ""
                                    ),
                                    issue_date=datetime.fromisoformat(
                                        invoice_data.get("issue_date", "2024-01-01")
                                    ),
                                    seller_nip=invoice_data.get("seller_nip", ""),
                                    buyer_nip=invoice_data.get("buyer_nip", ""),
                                    net_amount=invoice_data.get("net_amount", 0.0),
                                    vat_amount=invoice_data.get("vat_amount", 0.0),
                                    gross_amount=invoice_data.get("gross_amount", 0.0),
                                    currency=invoice_data.get("currency", "PLN"),
                                    items=invoice_data.get("items", []),
                                    xml_content=xml_content,
                                    hash_value=hash_value,
                                )
                                invoices.append(invoice)
                            else:
                                errors.append(
                                    f"{file_info.filename}: {', '.join(validation_result['errors'])}"
                                )

                        except Exception as e:
                            errors.append(f"{file_info.filename}: {str(e)}")

            return IntegrationResult(
                integration_type=IntegrationType.KSEF,
                success=len(invoices) > 0,
                data=invoices,
                error_message=f"Errors: {len(errors)}" if errors else None,
                processing_time=time.time() - start_time,
            )

        except Exception as e:
            return IntegrationResult(
                integration_type=IntegrationType.KSEF,
                success=False,
                data=None,
                error_message=str(e),
                processing_time=time.time() - start_time,
            )

    def validate_invoice_xml(self, xml_content: str) -> Dict[str, Any]:
        """Walidacja XML faktury KSeF."""
        try:
            # Parse XML
            root = ET.fromstring(xml_content)

            # Basic validation
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "invoice_data": {},
            }

            # Check required elements
            required_elements = [
                "Fa",
                "Naglowek",
                "Podmiot1",
                "Podmiot2",
                "FaWiersz",
                "FaCtrl",
            ]
            for element in required_elements:
                if root.find(f".//{element}") is None:
                    validation_result["errors"].append(
                        f"Missing required element: {element}"
                    )
                    validation_result["valid"] = False

            # Advanced validation rules
            if validation_result["valid"]:
                validation_result = self._validate_advanced_rules(
                    root, validation_result
                )

            # Extract invoice data
            if validation_result["valid"]:
                validation_result["invoice_data"] = self._extract_invoice_data(root)

            return validation_result

        except ET.ParseError as e:
            return {
                "valid": False,
                "errors": [f"XML parsing error: {str(e)}"],
                "warnings": [],
                "invoice_data": {},
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "invoice_data": {},
            }

    def _validate_advanced_rules(
        self, root: ET.Element, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Zaawansowane reguły walidacji."""

        # Check NIP format (10 digits)
        nips = root.findall(".//NIP")
        for nip in nips:
            if nip.text and not self._is_valid_nip(nip.text):
                result["errors"].append(f"Invalid NIP format: {nip.text}")
                result["valid"] = False

        # Check date format (YYYY-MM-DD)
        dates = root.findall(".//DataWystawienia")
        for date in dates:
            if date.text and not self._is_valid_date(date.text):
                result["errors"].append(f"Invalid date format: {date.text}")
                result["valid"] = False

        # Check amounts consistency
        netto_total = 0.0
        vat_total = 0.0
        brutto_total = 0.0

        for wiersz in root.findall(".//FaWiersz"):
            netto = wiersz.find("Netto")
            vat = wiersz.find("VAT")
            brutto = wiersz.find("Brutto")

            if netto is not None:
                netto_total += float(netto.text)
            if vat is not None:
                vat_total += float(vat.text)
            if brutto is not None:
                brutto_total += float(brutto.text)

        # Check if Netto + VAT = Brutto (with tolerance)
        if abs((netto_total + vat_total) - brutto_total) > 0.01:
            result["warnings"].append(
                f"Amount mismatch: Netto({netto_total}) + VAT({vat_total}) ≠ Brutto({brutto_total})"
            )

        # Check currency (should be PLN for Polish invoices)
        waluta = root.find(".//Waluta")
        if waluta is not None and waluta.text not in ["PLN", "EUR", "USD"]:
            result["warnings"].append(f"Unusual currency: {waluta.text}")

        # Check invoice number format
        nr_faktury = root.find(".//NrFaktury")
        if nr_faktury is not None and not self._is_valid_invoice_number(
            nr_faktury.text
        ):
            result["warnings"].append(
                f"Unusual invoice number format: {nr_faktury.text}"
            )

        return result

    def _is_valid_nip(self, nip: str) -> bool:
        """Sprawdzenie poprawności NIP."""
        if not nip or len(nip) != 10 or not nip.isdigit():
            return False

        # NIP checksum validation
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(int(nip[i]) * weights[i] for i in range(9)) % 11
        return checksum == int(nip[9])

    def _is_valid_date(self, date_str: str) -> bool:
        """Sprawdzenie poprawności daty."""
        try:
            datetime.fromisoformat(date_str)
            return True
        except ValueError:
            return False

    def _is_valid_invoice_number(self, invoice_number: str) -> bool:
        """Sprawdzenie formatu numeru faktury."""
        if not invoice_number:
            return False

        # Basic format check (should contain year and number)
        return len(invoice_number) >= 5 and any(
            char.isdigit() for char in invoice_number
        )

    def _extract_invoice_data(self, root: ET.Element) -> Dict[str, Any]:
        """Ekstrakcja danych faktury z XML."""
        data = {}

        try:
            # Invoice number
            nr_faktury = root.find(".//NrFaktury")
            if nr_faktury is not None:
                data["invoice_number"] = nr_faktury.text

            # Issue date
            data_wystawienia = root.find(".//DataWystawienia")
            if data_wystawienia is not None:
                data["issue_date"] = data_wystawienia.text

            # Seller NIP
            nip_sprzedawcy = root.find(".//NIP")
            if nip_sprzedawcy is not None:
                data["seller_nip"] = nip_sprzedawcy.text

            # Buyer NIP
            nip_nabywcy = root.find(".//Podmiot2/NIP")
            if nip_nabywcy is not None:
                data["buyer_nip"] = nip_nabywcy.text

            # Amounts
            netto = root.find(".//Netto")
            if netto is not None:
                data["net_amount"] = float(netto.text)

            vat = root.find(".//VAT")
            if vat is not None:
                data["vat_amount"] = float(vat.text)

            brutto = root.find(".//Brutto")
            if brutto is not None:
                data["gross_amount"] = float(brutto.text)

            # Currency
            waluta = root.find(".//Waluta")
            if waluta is not None:
                data["currency"] = waluta.text

            # Items
            items = []
            for wiersz in root.findall(".//FaWiersz"):
                item = {}
                if wiersz.find("Nazwa") is not None:
                    item["name"] = wiersz.find("Nazwa").text
                if wiersz.find("Ilosc") is not None:
                    item["quantity"] = float(wiersz.find("Ilosc").text)
                if wiersz.find("CenaJedn") is not None:
                    item["unit_price"] = float(wiersz.find("CenaJedn").text)
                if wiersz.find("Netto") is not None:
                    item["net_amount"] = float(wiersz.find("Netto").text)
                items.append(item)

            data["items"] = items

        except Exception as e:
            self.logger.error(f"Error extracting invoice data: {e}")

        return data

    def process_invoice(self, xml_content: str) -> IntegrationResult:
        """Przetwarzanie faktury KSeF."""
        start_time = time.time()

        try:
            # Validate XML
            validation_result = self.validate_invoice_xml(xml_content)

            if not validation_result["valid"]:
                return IntegrationResult(
                    integration_type=IntegrationType.KSEF,
                    success=False,
                    data=None,
                    error_message=f"Validation failed: {', '.join(validation_result['errors'])}",
                    processing_time=time.time() - start_time,
                )

            # Create KSeF invoice object
            invoice_data = validation_result["invoice_data"]
            hash_value = hashlib.sha256(xml_content.encode()).hexdigest()

            invoice = KSeFInvoice(
                invoice_number=invoice_data.get("invoice_number", ""),
                issue_date=datetime.fromisoformat(
                    invoice_data.get("issue_date", "2024-01-01")
                ),
                seller_nip=invoice_data.get("seller_nip", ""),
                buyer_nip=invoice_data.get("buyer_nip", ""),
                net_amount=invoice_data.get("net_amount", 0.0),
                vat_amount=invoice_data.get("vat_amount", 0.0),
                gross_amount=invoice_data.get("gross_amount", 0.0),
                currency=invoice_data.get("currency", "PLN"),
                items=invoice_data.get("items", []),
                xml_content=xml_content,
                hash_value=hash_value,
            )

            return IntegrationResult(
                integration_type=IntegrationType.KSEF,
                success=True,
                data=invoice,
                error_message=None,
                processing_time=time.time() - start_time,
            )

        except Exception as e:
            return IntegrationResult(
                integration_type=IntegrationType.KSEF,
                success=False,
                data=None,
                error_message=str(e),
                processing_time=time.time() - start_time,
            )


class JPKIntegration:
    """Integracja z JPK (Jednolity Plik Kontrolny)."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate_jpk_xml(self, xml_content: str, jpk_type: str) -> Dict[str, Any]:
        """Walidacja XML JPK."""
        try:
            root = ET.fromstring(xml_content)

            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "jpk_data": {},
            }

            # Check JPK type
            if jpk_type == "JPK_V7":
                validation_result = self._validate_jpk_v7(root, validation_result)
            elif jpk_type == "JPK_KR":
                validation_result = self._validate_jpk_kr(root, validation_result)
            elif jpk_type == "JPK_FA":
                validation_result = self._validate_jpk_fa(root, validation_result)
            else:
                validation_result["errors"].append(f"Unknown JPK type: {jpk_type}")
                validation_result["valid"] = False

            return validation_result

        except ET.ParseError as e:
            return {
                "valid": False,
                "errors": [f"XML parsing error: {str(e)}"],
                "warnings": [],
                "jpk_data": {},
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "jpk_data": {},
            }

    def _validate_jpk_v7(
        self, root: ET.Element, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Walidacja JPK_V7."""
        # Check required elements for JPK_V7
        required_elements = ["Naglowek", "Podmiot1", "SprzedazWiersz", "SprzedazCtrl"]
        for element in required_elements:
            if root.find(f".//{element}") is None:
                result["errors"].append(
                    f"Missing required element for JPK_V7: {element}"
                )
                result["valid"] = False

        # Extract basic data
        if result["valid"]:
            result["jpk_data"] = {
                "type": "JPK_V7",
                "period": self._extract_period(root),
                "nip": self._extract_nip(root),
                "sales_count": len(root.findall(".//SprzedazWiersz")),
                "total_sales": self._calculate_total_sales(root),
            }

        return result

    def _validate_jpk_kr(
        self, root: ET.Element, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Walidacja JPK_KR."""
        # Check required elements for JPK_KR
        required_elements = ["Naglowek", "Podmiot1", "KontoZapisKod", "KontoZapisCtrl"]
        for element in required_elements:
            if root.find(f".//{element}") is None:
                result["errors"].append(
                    f"Missing required element for JPK_KR: {element}"
                )
                result["valid"] = False

        # Extract basic data
        if result["valid"]:
            result["jpk_data"] = {
                "type": "JPK_KR",
                "period": self._extract_period(root),
                "nip": self._extract_nip(root),
                "account_entries_count": len(root.findall(".//KontoZapisKod")),
                "total_debit": self._calculate_total_debit(root),
                "total_credit": self._calculate_total_credit(root),
            }

        return result

    def _validate_jpk_fa(
        self, root: ET.Element, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Walidacja JPK_FA."""
        # Check required elements for JPK_FA
        required_elements = ["Naglowek", "Podmiot1", "FaWiersz", "FaCtrl"]
        for element in required_elements:
            if root.find(f".//{element}") is None:
                result["errors"].append(
                    f"Missing required element for JPK_FA: {element}"
                )
                result["valid"] = False

        # Extract basic data
        if result["valid"]:
            result["jpk_data"] = {
                "type": "JPK_FA",
                "period": self._extract_period(root),
                "nip": self._extract_nip(root),
                "invoices_count": len(root.findall(".//FaWiersz")),
                "total_net": self._calculate_total_net(root),
                "total_vat": self._calculate_total_vat(root),
            }

        return result

    def _extract_period(self, root: ET.Element) -> str:
        """Ekstrakcja okresu z JPK."""
        okres = root.find(".//Okres")
        if okres is not None:
            return okres.text
        return ""

    def _extract_nip(self, root: ET.Element) -> str:
        """Ekstrakcja NIP z JPK."""
        nip = root.find(".//NIP")
        if nip is not None:
            return nip.text
        return ""

    def _calculate_total_sales(self, root: ET.Element) -> float:
        """Obliczenie całkowitej sprzedaży."""
        total = 0.0
        for wiersz in root.findall(".//SprzedazWiersz"):
            netto = wiersz.find("Netto")
            if netto is not None:
                total += float(netto.text)
        return total

    def _calculate_total_debit(self, root: ET.Element) -> float:
        """Obliczenie całkowitego debetu."""
        total = 0.0
        for zapis in root.findall(".//KontoZapisKod"):
            debit = zapis.find("Wn")
            if debit is not None:
                total += float(debit.text)
        return total

    def _calculate_total_credit(self, root: ET.Element) -> float:
        """Obliczenie całkowitego kredytu."""
        total = 0.0
        for zapis in root.findall(".//KontoZapisKod"):
            credit = zapis.find("Ma")
            if credit is not None:
                total += float(credit.text)
        return total

    def _calculate_total_net(self, root: ET.Element) -> float:
        """Obliczenie całkowitej kwoty netto."""
        total = 0.0
        for wiersz in root.findall(".//FaWiersz"):
            netto = wiersz.find("Netto")
            if netto is not None:
                total += float(netto.text)
        return total

    def _calculate_total_vat(self, root: ET.Element) -> float:
        """Obliczenie całkowitej kwoty VAT."""
        total = 0.0
        for wiersz in root.findall(".//FaWiersz"):
            vat = wiersz.find("VAT")
            if vat is not None:
                total += float(vat.text)
        return total

    def process_jpk(self, xml_content: str, jpk_type: str) -> IntegrationResult:
        """Przetwarzanie JPK."""
        start_time = time.time()

        try:
            # Validate XML
            validation_result = self.validate_jpk_xml(xml_content, jpk_type)

            if not validation_result["valid"]:
                return IntegrationResult(
                    integration_type=IntegrationType.JPK,
                    success=False,
                    data=None,
                    error_message=f"Validation failed: {', '.join(validation_result['errors'])}",
                    processing_time=time.time() - start_time,
                )

            # Create JPK document object
            jpk_data = validation_result["jpk_data"]
            hash_value = hashlib.sha256(xml_content.encode()).hexdigest()

            jpk_doc = JPKDocument(
                document_type=jpk_type,
                period=jpk_data.get("period", ""),
                nip=jpk_data.get("nip", ""),
                content=xml_content,
                validation_status="valid",
                validation_errors=[],
                hash_value=hash_value,
            )

            return IntegrationResult(
                integration_type=IntegrationType.JPK,
                success=True,
                data=jpk_doc,
                error_message=None,
                processing_time=time.time() - start_time,
            )

        except Exception as e:
            return IntegrationResult(
                integration_type=IntegrationType.JPK,
                success=False,
                data=None,
                error_message=str(e),
                processing_time=time.time() - start_time,
            )


class VATWhitelistIntegration:
    """Integracja z Białą listą VAT."""

    def __init__(
        self, api_key: str = None, base_url: str = None, cache_ttl: int = 3600
    ):
        self.api_key = api_key
        self.base_url = base_url or "https://wl-api.mf.gov.pl/api"
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()

        # Cache for API responses (TTL in seconds)
        self.cache = TTLCache(maxsize=1000, ttl=cache_ttl)
        self.cache_file = Path("cache/vat_whitelist_cache.json")

        if self.api_key:
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )

        # Load cache from file
        self._load_cache()

    def check_nip(self, nip: str) -> IntegrationResult:
        """Sprawdzenie NIP w Białej liście VAT."""
        start_time = time.time()

        try:
            # Check cache first
            cache_key = f"vat_whitelist_{nip}"
            if cache_key in self.cache:
                cached_result = self.cache[cache_key]
                cached_result.processing_time = time.time() - start_time
                self.logger.info(f"Cache hit for NIP: {nip}")
                return cached_result

            # Mock response for testing
            if not self.api_key:
                result = self._mock_vat_whitelist_response(nip, start_time)
            else:
                # Real API call
                response = self.session.get(f"{self.base_url}/check/nip/{nip}")

                if response.status_code == 200:
                    data = response.json()

                    whitelist_entry = VATWhitelistEntry(
                        nip=data.get("nip", nip),
                        name=data.get("name", ""),
                        status=data.get("status", ""),
                        account_numbers=data.get("accountNumbers", []),
                        registration_date=(
                            datetime.fromisoformat(data.get("registrationDate", ""))
                            if data.get("registrationDate")
                            else None
                        ),
                        last_update=(
                            datetime.fromisoformat(data.get("lastUpdate", ""))
                            if data.get("lastUpdate")
                            else None
                        ),
                    )

                    result = IntegrationResult(
                        integration_type=IntegrationType.VAT_WHITELIST,
                        success=True,
                        data=whitelist_entry,
                        error_message=None,
                        processing_time=time.time() - start_time,
                    )
                else:
                    result = IntegrationResult(
                        integration_type=IntegrationType.VAT_WHITELIST,
                        success=False,
                        data=None,
                        error_message=f"API error: {response.status_code}",
                        processing_time=time.time() - start_time,
                    )

            # Cache the result
            self.cache[cache_key] = result
            self._save_cache()

            return result

        except Exception as e:
            result = IntegrationResult(
                integration_type=IntegrationType.VAT_WHITELIST,
                success=False,
                data=None,
                error_message=str(e),
                processing_time=time.time() - start_time,
            )
            return result

    def _load_cache(self):
        """Load cache from file."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)

                for key, data in cache_data.items():
                    # Reconstruct IntegrationResult from cache
                    if data.get("success"):
                        whitelist_entry = VATWhitelistEntry(
                            nip=data["data"]["nip"],
                            name=data["data"]["name"],
                            status=data["data"]["status"],
                            account_numbers=data["data"]["account_numbers"],
                            registration_date=(
                                datetime.fromisoformat(
                                    data["data"]["registration_date"]
                                )
                                if data["data"]["registration_date"]
                                else None
                            ),
                            last_update=(
                                datetime.fromisoformat(data["data"]["last_update"])
                                if data["data"]["last_update"]
                                else None
                            ),
                        )

                        result = IntegrationResult(
                            integration_type=IntegrationType.VAT_WHITELIST,
                            success=True,
                            data=whitelist_entry,
                            error_message=None,
                            processing_time=0.0,
                            timestamp=datetime.fromisoformat(data["timestamp"]),
                        )
                    else:
                        result = IntegrationResult(
                            integration_type=IntegrationType.VAT_WHITELIST,
                            success=False,
                            data=None,
                            error_message=data["error_message"],
                            processing_time=0.0,
                            timestamp=datetime.fromisoformat(data["timestamp"]),
                        )

                    self.cache[key] = result

                self.logger.info(f"Loaded {len(cache_data)} entries from cache")
        except Exception as e:
            self.logger.warning(f"Failed to load cache: {e}")

    def _save_cache(self):
        """Save cache to file."""
        try:
            # Create cache directory if it doesn't exist
            self.cache_file.parent.mkdir(exist_ok=True)

            cache_data = {}
            for key, result in self.cache.items():
                if result.success and result.data:
                    cache_data[key] = {
                        "success": True,
                        "data": {
                            "nip": result.data.nip,
                            "name": result.data.name,
                            "status": result.data.status,
                            "account_numbers": result.data.account_numbers,
                            "registration_date": (
                                result.data.registration_date.isoformat()
                                if result.data.registration_date
                                else None
                            ),
                            "last_update": (
                                result.data.last_update.isoformat()
                                if result.data.last_update
                                else None
                            ),
                        },
                        "error_message": None,
                        "timestamp": result.timestamp.isoformat(),
                    }
                else:
                    cache_data[key] = {
                        "success": False,
                        "data": None,
                        "error_message": result.error_message,
                        "timestamp": result.timestamp.isoformat(),
                    }

            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.warning(f"Failed to save cache: {e}")

    def clear_cache(self):
        """Clear cache."""
        self.cache.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()
        self.logger.info("Cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.cache.maxsize,
            "ttl": self.cache.ttl,
            "cache_file": str(self.cache_file),
            "cache_file_exists": self.cache_file.exists(),
        }

    def _mock_vat_whitelist_response(
        self, nip: str, start_time: float
    ) -> IntegrationResult:
        """Mock response dla testów."""
        # Generate mock data based on NIP
        mock_data = {
            "1234567890": {
                "name": "ACME Corporation Sp. z o.o.",
                "status": "Czynny",
                "accountNumbers": ["12345678901234567890123456"],
                "registrationDate": "2020-01-15",
                "lastUpdate": "2024-01-15",
            },
            "9876543210": {
                "name": "Test Company Ltd.",
                "status": "Czynny",
                "accountNumbers": ["98765432109876543210987654"],
                "registrationDate": "2019-06-20",
                "lastUpdate": "2024-01-10",
            },
        }

        data = mock_data.get(
            nip,
            {
                "name": f"Company {nip}",
                "status": "Nieznany",
                "accountNumbers": [],
                "registrationDate": None,
                "lastUpdate": None,
            },
        )

        whitelist_entry = VATWhitelistEntry(
            nip=nip,
            name=data["name"],
            status=data["status"],
            account_numbers=data["accountNumbers"],
            registration_date=(
                datetime.fromisoformat(data["registrationDate"])
                if data["registrationDate"]
                else None
            ),
            last_update=(
                datetime.fromisoformat(data["lastUpdate"])
                if data["lastUpdate"]
                else None
            ),
        )

        return IntegrationResult(
            integration_type=IntegrationType.VAT_WHITELIST,
            success=True,
            data=whitelist_entry,
            error_message=None,
            processing_time=time.time() - start_time,
        )

    def batch_check_nips(self, nips: List[str]) -> List[IntegrationResult]:
        """Sprawdzenie wielu NIP-ów jednocześnie."""
        results = []

        for nip in nips:
            result = self.check_nip(nip)
            results.append(result)
            # Add delay to avoid rate limiting
            time.sleep(0.1)

        return results


class KRSIntegration:
    """Integracja z KRS (Krajowy Rejestr Sądowy)."""

    def __init__(
        self, api_key: str = None, base_url: str = None, cache_ttl: int = 7200
    ):
        self.api_key = api_key
        self.base_url = base_url or "https://api-krs.ms.gov.pl/api"
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()

        # Cache for API responses (TTL in seconds)
        self.cache = TTLCache(maxsize=1000, ttl=cache_ttl)
        self.cache_file = Path("cache/krs_cache.json")

        if self.api_key:
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )

        # Load cache from file
        self._load_cache()

    def search_company(
        self, query: str, search_type: str = "name"
    ) -> IntegrationResult:
        """Wyszukiwanie firmy w KRS."""
        start_time = time.time()

        try:
            # Check cache first
            cache_key = f"krs_{search_type}_{query}"
            if cache_key in self.cache:
                cached_result = self.cache[cache_key]
                cached_result.processing_time = time.time() - start_time
                self.logger.info(f"Cache hit for KRS query: {query}")
                return cached_result

            # Mock response for testing
            if not self.api_key:
                result = self._mock_krs_response(query, start_time)
            else:
                # Real API call
                params = {search_type: query}
                response = self.session.get(f"{self.base_url}/search", params=params)

                if response.status_code == 200:
                    data = response.json()

                    if data.get("results"):
                        company_data = data["results"][0]

                        krs_entry = KRSEntry(
                            krs_number=company_data.get("krs", ""),
                            name=company_data.get("name", ""),
                            nip=company_data.get("nip", ""),
                            regon=company_data.get("regon", ""),
                            status=company_data.get("status", ""),
                            registration_date=(
                                datetime.fromisoformat(
                                    company_data.get("registrationDate", "")
                                )
                                if company_data.get("registrationDate")
                                else None
                            ),
                            address=company_data.get("address", ""),
                            legal_form=company_data.get("legalForm", ""),
                        )

                        result = IntegrationResult(
                            integration_type=IntegrationType.KRS,
                            success=True,
                            data=krs_entry,
                            error_message=None,
                            processing_time=time.time() - start_time,
                        )
                    else:
                        result = IntegrationResult(
                            integration_type=IntegrationType.KRS,
                            success=False,
                            data=None,
                            error_message="No results found",
                            processing_time=time.time() - start_time,
                        )
                else:
                    result = IntegrationResult(
                        integration_type=IntegrationType.KRS,
                        success=False,
                        data=None,
                        error_message=f"API error: {response.status_code}",
                        processing_time=time.time() - start_time,
                    )

            # Cache the result
            self.cache[cache_key] = result
            self._save_cache()

            return result

        except Exception as e:
            result = IntegrationResult(
                integration_type=IntegrationType.KRS,
                success=False,
                data=None,
                error_message=str(e),
                processing_time=time.time() - start_time,
            )
            return result

    def _load_cache(self):
        """Load cache from file."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)

                for key, data in cache_data.items():
                    # Reconstruct IntegrationResult from cache
                    if data.get("success"):
                        krs_entry = KRSEntry(
                            krs_number=data["data"]["krs_number"],
                            name=data["data"]["name"],
                            nip=data["data"]["nip"],
                            regon=data["data"]["regon"],
                            status=data["data"]["status"],
                            registration_date=(
                                datetime.fromisoformat(
                                    data["data"]["registration_date"]
                                )
                                if data["data"]["registration_date"]
                                else None
                            ),
                            address=data["data"]["address"],
                            legal_form=data["data"]["legal_form"],
                        )

                        result = IntegrationResult(
                            integration_type=IntegrationType.KRS,
                            success=True,
                            data=krs_entry,
                            error_message=None,
                            processing_time=0.0,
                            timestamp=datetime.fromisoformat(data["timestamp"]),
                        )
                    else:
                        result = IntegrationResult(
                            integration_type=IntegrationType.KRS,
                            success=False,
                            data=None,
                            error_message=data["error_message"],
                            processing_time=0.0,
                            timestamp=datetime.fromisoformat(data["timestamp"]),
                        )

                    self.cache[key] = result

                self.logger.info(f"Loaded {len(cache_data)} entries from KRS cache")
        except Exception as e:
            self.logger.warning(f"Failed to load KRS cache: {e}")

    def _save_cache(self):
        """Save cache to file."""
        try:
            # Create cache directory if it doesn't exist
            self.cache_file.parent.mkdir(exist_ok=True)

            cache_data = {}
            for key, result in self.cache.items():
                if result.success and result.data:
                    cache_data[key] = {
                        "success": True,
                        "data": {
                            "krs_number": result.data.krs_number,
                            "name": result.data.name,
                            "nip": result.data.nip,
                            "regon": result.data.regon,
                            "status": result.data.status,
                            "registration_date": (
                                result.data.registration_date.isoformat()
                                if result.data.registration_date
                                else None
                            ),
                            "address": result.data.address,
                            "legal_form": result.data.legal_form,
                        },
                        "error_message": None,
                        "timestamp": result.timestamp.isoformat(),
                    }
                else:
                    cache_data[key] = {
                        "success": False,
                        "data": None,
                        "error_message": result.error_message,
                        "timestamp": result.timestamp.isoformat(),
                    }

            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.warning(f"Failed to save KRS cache: {e}")

    def clear_cache(self):
        """Clear cache."""
        self.cache.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()
        self.logger.info("KRS cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.cache.maxsize,
            "ttl": self.cache.ttl,
            "cache_file": str(self.cache_file),
            "cache_file_exists": self.cache_file.exists(),
        }

    def _mock_krs_response(self, query: str, start_time: float) -> IntegrationResult:
        """Mock response dla testów."""
        # Generate mock data based on query
        mock_data = {
            "ACME": {
                "krs": "0000123456",
                "name": "ACME Corporation Sp. z o.o.",
                "nip": "1234567890",
                "regon": "123456789",
                "status": "Czynny",
                "registrationDate": "2020-01-15",
                "address": "ul. Przykładowa 123, 00-001 Warszawa",
                "legalForm": "Spółka z ograniczoną odpowiedzialnością",
            },
            "Test": {
                "krs": "0000654321",
                "name": "Test Company Ltd.",
                "nip": "9876543210",
                "regon": "987654321",
                "status": "Czynny",
                "registrationDate": "2019-06-20",
                "address": "ul. Testowa 456, 00-002 Kraków",
                "legalForm": "Spółka z ograniczoną odpowiedzialnością",
            },
        }

        # Find matching company
        company_data = None
        for key, data in mock_data.items():
            if key.lower() in query.lower():
                company_data = data
                break

        if not company_data:
            company_data = {
                "krs": "0000000000",
                "name": f"Company {query}",
                "nip": "0000000000",
                "regon": "000000000",
                "status": "Nieznany",
                "registrationDate": None,
                "address": "Adres nieznany",
                "legalForm": "Nieznana",
            }

        krs_entry = KRSEntry(
            krs_number=company_data["krs"],
            name=company_data["name"],
            nip=company_data["nip"],
            regon=company_data["regon"],
            status=company_data["status"],
            registration_date=(
                datetime.fromisoformat(company_data["registrationDate"])
                if company_data["registrationDate"]
                else None
            ),
            address=company_data["address"],
            legal_form=company_data["legalForm"],
        )

        return IntegrationResult(
            integration_type=IntegrationType.KRS,
            success=True,
            data=krs_entry,
            error_message=None,
            processing_time=time.time() - start_time,
        )


class PLIntegrationsManager:
    """Menedżer integracji PL-core."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Initialize integrations
        self.ksef = KSeFIntegration(
            api_key=self.config.get("ksef_api_key"),
            base_url=self.config.get("ksef_base_url"),
        )

        self.jpk = JPKIntegration()

        self.vat_whitelist = VATWhitelistIntegration(
            api_key=self.config.get("vat_whitelist_api_key"),
            base_url=self.config.get("vat_whitelist_base_url"),
        )

        self.krs = KRSIntegration(
            api_key=self.config.get("krs_api_key"),
            base_url=self.config.get("krs_base_url"),
        )

    def process_ksef_invoice(self, xml_content: str) -> IntegrationResult:
        """Przetwarzanie faktury KSeF."""
        return self.ksef.process_invoice(xml_content)

    def import_ksef_fa3_zip(self, zip_path: str) -> IntegrationResult:
        """Import faktur FA(3) z pliku ZIP."""
        return self.ksef.import_fa3_zip(zip_path)

    def import_ksef_fa3_from_bytes(self, zip_bytes: bytes) -> IntegrationResult:
        """Import faktur FA(3) z bytes ZIP."""
        return self.ksef.import_fa3_from_bytes(zip_bytes)

    def process_jpk_document(
        self, xml_content: str, jpk_type: str
    ) -> IntegrationResult:
        """Przetwarzanie dokumentu JPK."""
        return self.jpk.process_jpk(xml_content, jpk_type)

    def check_vat_whitelist(self, nip: str) -> IntegrationResult:
        """Sprawdzenie Białej listy VAT."""
        return self.vat_whitelist.check_nip(nip)

    def search_krs(self, query: str, search_type: str = "name") -> IntegrationResult:
        """Wyszukiwanie w KRS."""
        return self.krs.search_company(query, search_type)

    def batch_validate_contractors(
        self, nips: List[str]
    ) -> Dict[str, IntegrationResult]:
        """Walidacja wielu kontrahentów."""
        results = {}

        for nip in nips:
            # Check VAT whitelist
            vat_result = self.check_vat_whitelist(nip)
            results[f"{nip}_vat"] = vat_result

            # Search in KRS
            krs_result = self.search_krs(nip, "nip")
            results[f"{nip}_krs"] = krs_result

        return results

    def get_integration_status(self) -> Dict[str, Any]:
        """Status integracji."""
        return {
            "ksef": {
                "available": self.ksef.api_key is not None,
                "base_url": self.ksef.base_url,
            },
            "jpk": {
                "available": True,
                "supported_types": ["JPK_V7", "JPK_KR", "JPK_FA"],
            },
            "vat_whitelist": {
                "available": self.vat_whitelist.api_key is not None,
                "base_url": self.vat_whitelist.base_url,
            },
            "krs": {
                "available": self.krs.api_key is not None,
                "base_url": self.krs.base_url,
            },
        }
