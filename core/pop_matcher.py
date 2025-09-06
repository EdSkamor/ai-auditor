"""
Production POP (Population) matching and validation system.
Implements deterministic tie-breaker logic with confidence scoring.
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

import pandas as pd
import numpy as np
from rapidfuzz import fuzz

from .exceptions import ValidationError, FileProcessingError
from .data_processing import DataProcessor


class MatchStatus(Enum):
    """Match status enumeration."""
    FOUND = "znaleziono"
    NOT_FOUND = "brak"
    ERROR = "error"


class MatchCriteria(Enum):
    """Match criteria enumeration."""
    NUMBER = "numer"
    DATE_NET = "data+netto"
    NUMBER_FNAME = "numer+fname"
    NUMBER_SELLER = "numer+seller"
    FALLBACK = "fallback"


@dataclass
class MatchResult:
    """Structured match result."""
    status: MatchStatus
    criteria: MatchCriteria
    confidence: float
    pop_row_index: Optional[int]
    comparison_flags: Dict[str, str]  # TAK/NIE flags
    tie_breaker_score: float = 0.0
    seller_similarity: float = 0.0
    filename_hit: bool = False


class POPMatcher:
    """Production POP matching system with tie-breaker logic."""
    
    def __init__(self, 
                 tiebreak_weight_fname: float = 0.7,
                 tiebreak_min_seller: float = 0.4,
                 amount_tolerance: float = 0.01):
        self.tiebreak_weight_fname = tiebreak_weight_fname
        self.tiebreak_min_seller = tiebreak_min_seller
        self.amount_tolerance = amount_tolerance
        self.logger = logging.getLogger(__name__)
        self.data_processor = DataProcessor()
        
        # Column mapping for flexible headers
        self.column_mappings = {
            'invoice_number': [
                'numer', 'number', 'invoice', 'faktura', 'nr', 'no',
                'invoice_number', 'invoice_id', 'document_number'
            ],
            'date': [
                'data', 'date', 'data_dokumentu', 'issue_date', 'document_date'
            ],
            'amount_net': [
                'netto', 'net', 'total_net', 'amount_net', 'kwota_netto',
                'wartosc_netto', 'net_amount', 'net_value'
            ],
            'vendor': [
                'kontrahent', 'vendor', 'seller', 'supplier', 'dostawca',
                'sprzedawca', 'company', 'firma'
            ]
        }
    
    def _map_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Map flexible column headers to standard names."""
        mapped = {}
        for standard_name, candidates in self.column_mappings.items():
            for candidate in candidates:
                for col in df.columns:
                    if candidate.lower() in col.lower():
                        mapped[standard_name] = col
                        break
                if standard_name in mapped:
                    break
        
        return mapped
    
    def _normalize_invoice_number(self, number: str) -> str:
        """Normalize invoice number for matching."""
        if not number:
            return ""
        
        # Remove common prefixes and normalize
        normalized = str(number).strip().upper()
        normalized = re.sub(r'^(FV|INV|FAKTURA|INVOICE)\s*[#:]?\s*', '', normalized)
        normalized = re.sub(r'[^\w\-/]', '', normalized)
        
        return normalized
    
    def _normalize_vendor_name(self, vendor: str) -> str:
        """Normalize vendor name for matching."""
        if not vendor:
            return ""
        
        # Remove common suffixes and normalize
        normalized = str(vendor).strip().upper()
        normalized = re.sub(r'\s+(SP\.?\s*Z\s*O\.?O\.?|LTD\.?|LLC\.?|INC\.?)$', '', normalized)
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def _extract_invoice_number_from_filename(self, filename: str) -> Optional[str]:
        """Extract invoice number from filename."""
        if not filename:
            return None
        
        # Common patterns in filenames
        patterns = [
            r'([A-Z]{2,4}[0-9]{4,8})',  # ABC123456
            r'(FV[0-9\-/]+)',           # FV-123/2024
            r'(INV[0-9\-/]+)',          # INV-123/2024
            r'([0-9]{4,8})',            # 123456
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename.upper())
            if match:
                return match.group(1)
        
        return None
    
    def _calculate_seller_similarity(self, pop_vendor: str, pdf_seller: str) -> float:
        """Calculate similarity between POP vendor and PDF seller."""
        if not pop_vendor or not pdf_seller:
            return 0.0
        
        pop_norm = self._normalize_vendor_name(pop_vendor)
        pdf_norm = self._normalize_vendor_name(pdf_seller)
        
        if not pop_norm or not pdf_norm:
            return 0.0
        
        # Use rapidfuzz for fuzzy matching
        similarity = fuzz.ratio(pop_norm, pdf_norm) / 100.0
        
        # Boost exact matches
        if pop_norm == pdf_norm:
            similarity = 1.0
        
        return similarity
    
    def _calculate_tie_breaker_score(self, 
                                   seller_similarity: float, 
                                   filename_hit: bool) -> float:
        """Calculate tie-breaker score."""
        fname_score = 1.0 if filename_hit else 0.0
        seller_score = seller_similarity if seller_similarity >= self.tiebreak_min_seller else 0.0
        
        # Weighted combination
        tie_breaker_score = (
            self.tiebreak_weight_fname * fname_score +
            (1 - self.tiebreak_weight_fname) * seller_score
        )
        
        return tie_breaker_score
    
    def _match_by_number(self, invoice_data: Dict[str, Any], pop_df: pd.DataFrame, 
                        column_map: Dict[str, str]) -> List[Tuple[int, float]]:
        """Match by invoice number."""
        if 'invoice_number' not in column_map or not invoice_data.get('invoice_id'):
            return []
        
        pdf_number = self._normalize_invoice_number(invoice_data['invoice_id'])
        if not pdf_number:
            return []
        
        matches = []
        for idx, row in pop_df.iterrows():
            pop_number = self._normalize_invoice_number(str(row[column_map['invoice_number']]))
            if pop_number and pdf_number == pop_number:
                matches.append((idx, 1.0))  # Exact match
        
        return matches
    
    def _match_by_date_amount(self, invoice_data: Dict[str, Any], pop_df: pd.DataFrame,
                             column_map: Dict[str, str]) -> List[Tuple[int, float]]:
        """Match by date and amount."""
        if not all(key in column_map for key in ['date', 'amount_net']):
            return []
        
        pdf_date = invoice_data.get('issue_date')
        pdf_amount = invoice_data.get('total_net')
        
        if not pdf_date or pdf_amount is None:
            return []
        
        matches = []
        for idx, row in pop_df.iterrows():
            try:
                # Parse POP date
                pop_date_str = str(row[column_map['date']])
                pop_date = pd.to_datetime(pop_date_str, errors='coerce', dayfirst=True)
                
                if pd.isna(pop_date):
                    continue
                
                # Parse POP amount
                pop_amount = self.data_processor.parse_amount_series(
                    pd.Series([row[column_map['amount_net']]])
                ).iloc[0]
                
                if pd.isna(pop_amount):
                    continue
                
                # Check date match (within 1 day tolerance)
                date_diff = abs((pdf_date - pop_date).days)
                if date_diff > 1:
                    continue
                
                # Check amount match (within tolerance)
                amount_diff = abs(pdf_amount - pop_amount) / max(pdf_amount, pop_amount, 1)
                if amount_diff > self.amount_tolerance:
                    continue
                
                # Calculate confidence based on date and amount accuracy
                date_confidence = max(0, 1 - date_diff * 0.1)
                amount_confidence = max(0, 1 - amount_diff * 10)
                confidence = (date_confidence + amount_confidence) / 2
                
                matches.append((idx, confidence))
                
            except Exception as e:
                self.logger.warning(f"Error matching row {idx}: {e}")
                continue
        
        return matches
    
    def match_invoice(self, invoice_data: Dict[str, Any], pop_df: pd.DataFrame,
                     filename: str = "") -> MatchResult:
        """Match a single invoice against POP data."""
        try:
            # Map columns
            column_map = self._map_columns(pop_df)
            if not column_map:
                return MatchResult(
                    status=MatchStatus.ERROR,
                    criteria=MatchCriteria.FALLBACK,
                    confidence=0.0,
                    pop_row_index=None,
                    comparison_flags={},
                    error="No matching columns found in POP data"
                )
            
            # Try matching by invoice number first
            number_matches = self._match_by_number(invoice_data, pop_df, column_map)
            
            if number_matches:
                # Multiple matches by number - use tie-breaker
                if len(number_matches) > 1:
                    best_match = self._apply_tie_breaker(
                        number_matches, invoice_data, pop_df, column_map, filename
                    )
                    return MatchResult(
                        status=MatchStatus.FOUND,
                        criteria=MatchCriteria.NUMBER_FNAME if best_match[2] else MatchCriteria.NUMBER_SELLER,
                        confidence=best_match[1],
                        pop_row_index=best_match[0],
                        comparison_flags=self._generate_comparison_flags(
                            invoice_data, pop_df.iloc[best_match[0]], column_map
                        ),
                        tie_breaker_score=best_match[3],
                        seller_similarity=best_match[4],
                        filename_hit=best_match[2]
                    )
                else:
                    # Single match by number
                    idx, confidence = number_matches[0]
                    return MatchResult(
                        status=MatchStatus.FOUND,
                        criteria=MatchCriteria.NUMBER,
                        confidence=confidence,
                        pop_row_index=idx,
                        comparison_flags=self._generate_comparison_flags(
                            invoice_data, pop_df.iloc[idx], column_map
                        )
                    )
            
            # Try matching by date and amount
            date_amount_matches = self._match_by_date_amount(invoice_data, pop_df, column_map)
            
            if date_amount_matches:
                # Multiple matches by date+amount - use tie-breaker
                if len(date_amount_matches) > 1:
                    best_match = self._apply_tie_breaker(
                        date_amount_matches, invoice_data, pop_df, column_map, filename
                    )
                    return MatchResult(
                        status=MatchStatus.FOUND,
                        criteria=MatchCriteria.DATE_NET,
                        confidence=best_match[1],
                        pop_row_index=best_match[0],
                        comparison_flags=self._generate_comparison_flags(
                            invoice_data, pop_df.iloc[best_match[0]], column_map
                        ),
                        tie_breaker_score=best_match[3],
                        seller_similarity=best_match[4],
                        filename_hit=best_match[2]
                    )
                else:
                    # Single match by date+amount
                    idx, confidence = date_amount_matches[0]
                    return MatchResult(
                        status=MatchStatus.FOUND,
                        criteria=MatchCriteria.DATE_NET,
                        confidence=confidence,
                        pop_row_index=idx,
                        comparison_flags=self._generate_comparison_flags(
                            invoice_data, pop_df.iloc[idx], column_map
                        )
                    )
            
            # No matches found
            return MatchResult(
                status=MatchStatus.NOT_FOUND,
                criteria=MatchCriteria.FALLBACK,
                confidence=0.0,
                pop_row_index=None,
                comparison_flags={}
            )
            
        except Exception as e:
            self.logger.error(f"Error matching invoice: {e}")
            return MatchResult(
                status=MatchStatus.ERROR,
                criteria=MatchCriteria.FALLBACK,
                confidence=0.0,
                pop_row_index=None,
                comparison_flags={},
                error=str(e)
            )
    
    def _apply_tie_breaker(self, matches: List[Tuple[int, float]], 
                          invoice_data: Dict[str, Any], pop_df: pd.DataFrame,
                          column_map: Dict[str, str], filename: str) -> Tuple[int, float, bool, float, float]:
        """Apply tie-breaker logic to multiple matches."""
        best_match = None
        best_score = -1
        
        filename_invoice_id = self._extract_invoice_number_from_filename(filename)
        
        for idx, confidence in matches:
            pop_row = pop_df.iloc[idx]
            
            # Calculate seller similarity
            seller_similarity = 0.0
            if 'vendor' in column_map:
                pop_vendor = str(pop_row[column_map['vendor']])
                pdf_seller = invoice_data.get('seller_guess', '')
                seller_similarity = self._calculate_seller_similarity(pop_vendor, pdf_seller)
            
            # Check filename hit
            filename_hit = False
            if filename_invoice_id and 'invoice_number' in column_map:
                pop_number = self._normalize_invoice_number(str(pop_row[column_map['invoice_number']]))
                filename_hit = (pop_number == filename_invoice_id)
            
            # Calculate tie-breaker score
            tie_breaker_score = self._calculate_tie_breaker_score(seller_similarity, filename_hit)
            
            # Combined score: confidence + tie-breaker
            combined_score = confidence + tie_breaker_score * 0.5
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = (idx, confidence, filename_hit, tie_breaker_score, seller_similarity)
        
        return best_match
    
    def _generate_comparison_flags(self, invoice_data: Dict[str, Any], 
                                 pop_row: pd.Series, column_map: Dict[str, str]) -> Dict[str, str]:
        """Generate comparison flags (TAK/NIE)."""
        flags = {}
        
        # Number comparison
        if 'invoice_number' in column_map:
            pdf_number = self._normalize_invoice_number(invoice_data.get('invoice_id', ''))
            pop_number = self._normalize_invoice_number(str(pop_row[column_map['invoice_number']]))
            flags['number_match'] = "TAK" if pdf_number == pop_number else "NIE"
        
        # Date comparison
        if 'date' in column_map:
            pdf_date = invoice_data.get('issue_date')
            if pdf_date:
                try:
                    pop_date = pd.to_datetime(str(pop_row[column_map['date']]), errors='coerce', dayfirst=True)
                    if not pd.isna(pop_date):
                        date_diff = abs((pdf_date - pop_date).days)
                        flags['date_match'] = "TAK" if date_diff <= 1 else "NIE"
                    else:
                        flags['date_match'] = "NIE"
                except:
                    flags['date_match'] = "NIE"
            else:
                flags['date_match'] = "NIE"
        
        # Amount comparison
        if 'amount_net' in column_map:
            pdf_amount = invoice_data.get('total_net')
            if pdf_amount is not None:
                try:
                    pop_amount = self.data_processor.parse_amount_series(
                        pd.Series([pop_row[column_map['amount_net']]])
                    ).iloc[0]
                    if not pd.isna(pop_amount):
                        amount_diff = abs(pdf_amount - pop_amount) / max(pdf_amount, pop_amount, 1)
                        flags['amount_match'] = "TAK" if amount_diff <= self.amount_tolerance else "NIE"
                    else:
                        flags['amount_match'] = "NIE"
                except:
                    flags['amount_match'] = "NIE"
            else:
                flags['amount_match'] = "NIE"
        
        # Seller comparison
        if 'vendor' in column_map:
            pdf_seller = invoice_data.get('seller_guess', '')
            pop_vendor = str(pop_row[column_map['vendor']])
            seller_similarity = self._calculate_seller_similarity(pop_vendor, pdf_seller)
            flags['seller_match'] = "TAK" if seller_similarity >= self.tiebreak_min_seller else "NIE"
        
        return flags


# Global instance
_pop_matcher = POPMatcher()


def match_invoice(invoice_data: Dict[str, Any], pop_df: pd.DataFrame, 
                 filename: str = "") -> MatchResult:
    """Convenience function to match a single invoice."""
    return _pop_matcher.match_invoice(invoice_data, pop_df, filename)

