"""
Web scraper dla oficjalnych stron rządowych i firm.
Pozyskiwanie informacji potrzebnych do audytu i oceny ryzyk.
"""

import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from .exceptions import FileProcessingError


class SourceType(Enum):
    """Typy źródeł danych."""

    GOVERNMENT = "government"
    COMPANY = "company"
    REGULATORY = "regulatory"
    FINANCIAL = "financial"
    LEGAL = "legal"


class DataType(Enum):
    """Typy danych."""

    COMPANY_INFO = "company_info"
    FINANCIAL_DATA = "financial_data"
    LEGAL_STATUS = "legal_status"
    REGULATORY_INFO = "regulatory_info"
    RISK_INDICATORS = "risk_indicators"
    NEWS = "news"
    SANCTIONS = "sanctions"


@dataclass
class ScrapedData:
    """Dane pozyskane ze scrapingu."""

    id: str
    source_url: str
    source_type: SourceType
    data_type: DataType
    title: str
    content: str
    extracted_data: Dict[str, Any]
    scraped_at: datetime
    confidence: float
    metadata: Dict[str, Any]


@dataclass
class CompanyInfo:
    """Informacje o firmie."""

    nip: str
    name: str
    regon: str
    krs: str
    address: str
    legal_form: str
    registration_date: Optional[datetime]
    status: str
    vat_status: str
    website: Optional[str]
    phone: Optional[str]
    email: Optional[str]


@dataclass
class RiskIndicator:
    """Wskaźnik ryzyka."""

    type: str
    description: str
    severity: str  # low, medium, high, critical
    source: str
    date: datetime
    details: Dict[str, Any]


class GovernmentScraper:
    """Scraper dla stron rządowych."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

        # Oficjalne strony rządowe
        self.government_sites = {
            "krs": "https://rejestr.io",
            "regon": "https://wyszukiwarkaregon.stat.gov.pl",
            "vat_whitelist": "https://www.podatki.gov.pl/wykaz-podatnikow-vat-wyszukiwarka",
            "gus": "https://stat.gov.pl",
            "krs_gov": "https://ekrs.ms.gov.pl",
            "sanctions": "https://www.gov.pl/web/mswia/lista-osob-i-podmiotow-objetych-sankcjami",
            "pep": "https://www.gov.pl/web/mswia/lista-osob-politically-exposed-persons",
        }

        # Rate limiting
        self.last_request_time = {}
        self.min_delay = 1.0  # Minimum delay between requests

    def _rate_limit(self, domain: str):
        """Rate limiting dla domeny."""
        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            if elapsed < self.min_delay:
                time.sleep(self.min_delay - elapsed)

        self.last_request_time[domain] = time.time()

    def scrape_company_info(self, nip: str) -> Optional[CompanyInfo]:
        """Scraping informacji o firmie."""
        try:
            self.logger.info(f"Scraping company info for NIP: {nip}")

            # Mock implementation - in real scenario, would scrape actual sites
            company_info = CompanyInfo(
                nip=nip,
                name=f"Company {nip}",
                regon="123456789",
                krs="0000123456",
                address="ul. Testowa 123, 00-001 Warszawa",
                legal_form="Sp. z o.o.",
                registration_date=datetime(2020, 1, 1),
                status="active",
                vat_status="active",
                website="https://example.com",
                phone="+48123456789",
                email="info@example.com",
            )

            return company_info

        except Exception as e:
            self.logger.error(f"Company info scraping failed: {e}")
            return None

    def scrape_vat_whitelist(self, nip: str) -> Dict[str, Any]:
        """Scraping białej listy VAT."""
        try:
            self.logger.info(f"Scraping VAT whitelist for NIP: {nip}")

            # Mock implementation
            return {
                "nip": nip,
                "status": "active",
                "name": f"Company {nip}",
                "account_numbers": ["PL1234567890123456789012345"],
                "last_updated": datetime.now().isoformat(),
                "is_valid": True,
            }

        except Exception as e:
            self.logger.error(f"VAT whitelist scraping failed: {e}")
            return {}

    def scrape_sanctions_list(self, company_name: str) -> List[Dict[str, Any]]:
        """Scraping listy sankcji."""
        try:
            self.logger.info(f"Scraping sanctions list for: {company_name}")

            # Mock implementation
            sanctions = []
            if "sanctions" in company_name.lower():
                sanctions.append(
                    {
                        "name": company_name,
                        "type": "sanctions",
                        "description": "Entity on sanctions list",
                        "date": datetime.now().isoformat(),
                        "source": "MSWiA sanctions list",
                    }
                )

            return sanctions

        except Exception as e:
            self.logger.error(f"Sanctions list scraping failed: {e}")
            return []

    def scrape_pep_list(self, company_name: str) -> List[Dict[str, Any]]:
        """Scraping listy PEP."""
        try:
            self.logger.info(f"Scraping PEP list for: {company_name}")

            # Mock implementation
            pep_entities = []
            if (
                "politician" in company_name.lower()
                or "government" in company_name.lower()
            ):
                pep_entities.append(
                    {
                        "name": company_name,
                        "type": "pep",
                        "description": "Politically Exposed Person",
                        "date": datetime.now().isoformat(),
                        "source": "MSWiA PEP list",
                    }
                )

            return pep_entities

        except Exception as e:
            self.logger.error(f"PEP list scraping failed: {e}")
            return []

    def scrape_financial_data(self, nip: str) -> Dict[str, Any]:
        """Scraping danych finansowych."""
        try:
            self.logger.info(f"Scraping financial data for NIP: {nip}")

            # Mock implementation
            return {
                "nip": nip,
                "revenue": 1000000.0,
                "profit": 100000.0,
                "employees": 50,
                "year": 2023,
                "source": "GUS financial data",
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Financial data scraping failed: {e}")
            return {}

    def scrape_news(
        self, company_name: str, days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """Scraping wiadomości o firmie."""
        try:
            self.logger.info(f"Scraping news for: {company_name}")

            # Mock implementation
            news = []
            if "news" in company_name.lower():
                news.append(
                    {
                        "title": f"News about {company_name}",
                        "content": f"Recent developments regarding {company_name}",
                        "date": datetime.now().isoformat(),
                        "source": "Business news",
                        "sentiment": "neutral",
                    }
                )

            return news

        except Exception as e:
            self.logger.error(f"News scraping failed: {e}")
            return []

    def analyze_risk_indicators(
        self, company_data: Dict[str, Any]
    ) -> List[RiskIndicator]:
        """Analiza wskaźników ryzyka."""
        try:
            risk_indicators = []

            # Check for various risk factors
            if company_data.get("status") == "inactive":
                risk_indicators.append(
                    RiskIndicator(
                        type="company_status",
                        description="Company is inactive",
                        severity="high",
                        source="KRS data",
                        date=datetime.now(),
                        details={"status": "inactive"},
                    )
                )

            if company_data.get("vat_status") == "inactive":
                risk_indicators.append(
                    RiskIndicator(
                        type="vat_status",
                        description="VAT status is inactive",
                        severity="medium",
                        source="VAT whitelist",
                        date=datetime.now(),
                        details={"vat_status": "inactive"},
                    )
                )

            # Check for sanctions
            sanctions = company_data.get("sanctions", [])
            if sanctions:
                risk_indicators.append(
                    RiskIndicator(
                        type="sanctions",
                        description=f"Entity on sanctions list: {len(sanctions)} entries",
                        severity="critical",
                        source="Sanctions list",
                        date=datetime.now(),
                        details={"sanctions_count": len(sanctions)},
                    )
                )

            # Check for PEP
            pep_entities = company_data.get("pep", [])
            if pep_entities:
                risk_indicators.append(
                    RiskIndicator(
                        type="pep",
                        description=f"PEP entity: {len(pep_entities)} entries",
                        severity="high",
                        source="PEP list",
                        date=datetime.now(),
                        details={"pep_count": len(pep_entities)},
                    )
                )

            return risk_indicators

        except Exception as e:
            self.logger.error(f"Risk analysis failed: {e}")
            return []


class WebScrapingManager:
    """Menedżer web scrapingu."""

    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path.home() / ".ai-auditor" / "scraping"

        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(__name__)
        self.scraper = GovernmentScraper()

        # Cache for scraped data
        self.cache = {}
        self.cache_file = self.data_dir / "scraping_cache.json"
        self._load_cache()

    def _load_cache(self):
        """Ładowanie cache."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
        except Exception as e:
            self.logger.error(f"Cache loading failed: {e}")
            self.cache = {}

    def _save_cache(self):
        """Zapisywanie cache."""
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Cache saving failed: {e}")

    def _get_cache_key(self, data_type: str, identifier: str) -> str:
        """Generowanie klucza cache."""
        return f"{data_type}:{identifier}"

    def _is_cache_valid(
        self, cache_entry: Dict[str, Any], max_age_hours: int = 24
    ) -> bool:
        """Sprawdzanie ważności cache."""
        try:
            cached_at = datetime.fromisoformat(cache_entry["cached_at"])
            age = datetime.now() - cached_at
            return age.total_seconds() < max_age_hours * 3600
        except:
            return False

    def get_company_comprehensive_data(
        self, nip: str, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Pobieranie kompletnych danych o firmie."""
        try:
            cache_key = self._get_cache_key("company", nip)

            # Check cache first
            if not force_refresh and cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if self._is_cache_valid(cache_entry):
                    self.logger.info(f"Using cached data for NIP: {nip}")
                    return cache_entry["data"]

            self.logger.info(f"Scraping comprehensive data for NIP: {nip}")

            # Scrape all available data
            company_info = self.scraper.scrape_company_info(nip)
            vat_data = self.scraper.scrape_vat_whitelist(nip)
            financial_data = self.scraper.scrape_financial_data(nip)

            # Get company name for additional searches
            company_name = company_info.name if company_info else f"Company {nip}"

            sanctions = self.scraper.scrape_sanctions_list(company_name)
            pep_entities = self.scraper.scrape_pep_list(company_name)
            news = self.scraper.scrape_news(company_name)

            # Combine all data
            comprehensive_data = {
                "nip": nip,
                "company_info": asdict(company_info) if company_info else {},
                "vat_data": vat_data,
                "financial_data": financial_data,
                "sanctions": sanctions,
                "pep": pep_entities,
                "news": news,
                "scraped_at": datetime.now().isoformat(),
            }

            # Analyze risk indicators
            risk_indicators = self.scraper.analyze_risk_indicators(comprehensive_data)
            comprehensive_data["risk_indicators"] = [
                asdict(ri) for ri in risk_indicators
            ]

            # Cache the data
            self.cache[cache_key] = {
                "data": comprehensive_data,
                "cached_at": datetime.now().isoformat(),
            }
            self._save_cache()

            return comprehensive_data

        except Exception as e:
            self.logger.error(f"Comprehensive data scraping failed: {e}")
            raise FileProcessingError(f"Comprehensive data scraping failed: {e}")

    def get_risk_assessment(self, nip: str) -> Dict[str, Any]:
        """Ocena ryzyka na podstawie scrapowanych danych."""
        try:
            data = self.get_company_comprehensive_data(nip)

            # Calculate overall risk score
            risk_score = 0
            risk_factors = []

            # Company status risk
            if data.get("company_info", {}).get("status") == "inactive":
                risk_score += 30
                risk_factors.append("Company inactive")

            # VAT status risk
            if data.get("vat_data", {}).get("status") == "inactive":
                risk_score += 20
                risk_factors.append("VAT inactive")

            # Sanctions risk
            sanctions_count = len(data.get("sanctions", []))
            if sanctions_count > 0:
                risk_score += 50
                risk_factors.append(f"{sanctions_count} sanctions entries")

            # PEP risk
            pep_count = len(data.get("pep", []))
            if pep_count > 0:
                risk_score += 40
                risk_factors.append(f"{pep_count} PEP entries")

            # Financial risk indicators
            financial_data = data.get("financial_data", {})
            if financial_data.get("revenue", 0) < 100000:
                risk_score += 10
                risk_factors.append("Low revenue")

            # Determine risk level
            if risk_score >= 70:
                risk_level = "critical"
            elif risk_score >= 50:
                risk_level = "high"
            elif risk_score >= 30:
                risk_level = "medium"
            else:
                risk_level = "low"

            return {
                "nip": nip,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "data_sources": [
                    "KRS",
                    "REGON",
                    "VAT Whitelist",
                    "Sanctions List",
                    "PEP List",
                    "Financial Data",
                    "News",
                ],
                "last_updated": datetime.now().isoformat(),
                "comprehensive_data": data,
            }

        except Exception as e:
            self.logger.error(f"Risk assessment failed: {e}")
            raise FileProcessingError(f"Risk assessment failed: {e}")

    def batch_scrape_companies(self, nip_list: List[str]) -> Dict[str, Dict[str, Any]]:
        """Scraping wielu firm jednocześnie."""
        try:
            results = {}

            for nip in nip_list:
                try:
                    self.logger.info(f"Scraping data for NIP: {nip}")
                    results[nip] = self.get_company_comprehensive_data(nip)

                    # Rate limiting between requests
                    time.sleep(1)

                except Exception as e:
                    self.logger.error(f"Failed to scrape NIP {nip}: {e}")
                    results[nip] = {"error": str(e)}

            return results

        except Exception as e:
            self.logger.error(f"Batch scraping failed: {e}")
            raise FileProcessingError(f"Batch scraping failed: {e}")

    def get_scraping_summary(self) -> Dict[str, Any]:
        """Podsumowanie scrapingu."""
        try:
            total_cached = len(self.cache)
            recent_scrapes = 0

            for cache_entry in self.cache.values():
                if self._is_cache_valid(cache_entry, max_age_hours=1):
                    recent_scrapes += 1

            return {
                "total_cached_entries": total_cached,
                "recent_scrapes": recent_scrapes,
                "cache_file_size": (
                    self.cache_file.stat().st_size if self.cache_file.exists() else 0
                ),
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Scraping summary failed: {e}")
            return {}
