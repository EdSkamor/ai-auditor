"""
Analityka audytowa - ryzyka, journal-entry testing, sampling
System analizy ryzyk audytowych i testów szczegółowych.
"""

import json
import logging
import hashlib
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import random
import math

try:
    import pandas as pd
    import numpy as np
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None
    np = None

from .exceptions import ValidationError, FileProcessingError


class RiskLevel(Enum):
    """Poziomy ryzyka."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(Enum):
    """Kategorie ryzyka."""
    INHERENT = "inherent"
    CONTROL = "control"
    DETECTION = "detection"
    BUSINESS = "business"
    COMPLIANCE = "compliance"


class SamplingMethod(Enum):
    """Metody doboru próby."""
    MUS = "mus"  # Monetary Unit Sampling
    STATISTICAL = "statistical"
    NON_STATISTICAL = "non_statistical"
    JUDGMENTAL = "judgmental"


@dataclass
class RiskFactor:
    """Czynnik ryzyka."""
    id: str
    name: str
    category: RiskCategory
    level: RiskLevel
    description: str
    impact: float  # 1-5 scale
    likelihood: float  # 1-5 scale
    controls: List[str]
    mitigation: str
    owner: str
    last_review: datetime
    next_review: datetime


@dataclass
class JournalEntry:
    """Zapis księgowy."""
    id: str
    date: datetime
    account_code: str
    account_name: str
    debit: float
    credit: float
    description: str
    reference: str
    user_id: str
    batch_id: str
    amount: float
    currency: str = "PLN"


@dataclass
class Anomaly:
    """Anomalia w zapisach księgowych."""
    id: str
    entry_id: str
    anomaly_type: str
    severity: RiskLevel
    description: str
    detected_at: datetime
    confidence: float
    details: Dict[str, Any]


@dataclass
class SamplingResult:
    """Wynik doboru próby."""
    method: SamplingMethod
    population_size: int
    sample_size: int
    confidence_level: float
    tolerable_error: float
    expected_error: float
    selected_items: List[Dict[str, Any]]
    sampling_interval: float
    upper_error_limit: float


@dataclass
class RiskAssessment:
    """Ocena ryzyka."""
    id: str
    title: str
    assessment_date: datetime
    risk_factors: List[RiskFactor]
    overall_risk_level: RiskLevel
    key_risks: List[str]
    recommendations: List[str]
    next_assessment: datetime


class RiskAnalyzer:
    """Analizator ryzyk audytowych."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_risk_factors()
    
    def _initialize_risk_factors(self):
        """Inicjalizacja standardowych czynników ryzyka."""
        self.standard_risks = [
            RiskFactor(
                id="risk_001",
                name="Ryzyko inherentne - przychody",
                category=RiskCategory.INHERENT,
                level=RiskLevel.MEDIUM,
                description="Ryzyko związane z ujmowaniem przychodów",
                impact=4.0,
                likelihood=3.0,
                controls=["Kontrola dokumentów sprzedaży", "Weryfikacja faktur"],
                mitigation="Testy szczegółowe przychodów",
                owner="Audytor",
                last_review=datetime.now(),
                next_review=datetime.now() + timedelta(days=30)
            ),
            RiskFactor(
                id="risk_002",
                name="Ryzyko kontroli - proces sprzedaży",
                category=RiskCategory.CONTROL,
                level=RiskLevel.LOW,
                description="Ryzyko związane z kontrolami procesu sprzedaży",
                impact=3.0,
                likelihood=2.0,
                controls=["Autoryzacja sprzedaży", "Kontrola limitów"],
                mitigation="Testy kontroli",
                owner="Kontroler",
                last_review=datetime.now(),
                next_review=datetime.now() + timedelta(days=60)
            ),
            RiskFactor(
                id="risk_003",
                name="Ryzyko wykrycia - zapisy księgowe",
                category=RiskCategory.DETECTION,
                level=RiskLevel.MEDIUM,
                description="Ryzyko związane z wykryciem błędów w zapisach",
                impact=3.0,
                likelihood=3.0,
                controls=["Przegląd zapisów", "Testy analityczne"],
                mitigation="Testy szczegółowe",
                owner="Audytor",
                last_review=datetime.now(),
                next_review=datetime.now() + timedelta(days=45)
            )
        ]
    
    def assess_risk(self, risk_factors: List[RiskFactor] = None) -> RiskAssessment:
        """Ocena ryzyka audytowego."""
        if risk_factors is None:
            risk_factors = self.standard_risks
        
        # Calculate overall risk level
        risk_scores = []
        for factor in risk_factors:
            score = factor.impact * factor.likelihood
            risk_scores.append(score)
        
        avg_risk_score = statistics.mean(risk_scores)
        
        if avg_risk_score >= 16:
            overall_level = RiskLevel.CRITICAL
        elif avg_risk_score >= 12:
            overall_level = RiskLevel.HIGH
        elif avg_risk_score >= 8:
            overall_level = RiskLevel.MEDIUM
        else:
            overall_level = RiskLevel.LOW
        
        # Identify key risks
        key_risks = []
        for factor in risk_factors:
            if factor.impact * factor.likelihood >= 12:
                key_risks.append(factor.name)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_factors, overall_level)
        
        return RiskAssessment(
            id=f"RA_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title="Ocena ryzyka audytowego",
            assessment_date=datetime.now(),
            risk_factors=risk_factors,
            overall_risk_level=overall_level,
            key_risks=key_risks,
            recommendations=recommendations,
            next_assessment=datetime.now() + timedelta(days=90)
        )
    
    def _generate_recommendations(self, risk_factors: List[RiskFactor], overall_level: RiskLevel) -> List[str]:
        """Generowanie rekomendacji na podstawie ryzyk."""
        recommendations = []
        
        if overall_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "Wymagane natychmiastowe działania naprawcze",
                "Zwiększenie częstotliwości testów kontroli",
                "Rozszerzenie zakresu testów szczegółowych",
                "Dodatkowe procedury audytowe"
            ])
        elif overall_level == RiskLevel.HIGH:
            recommendations.extend([
                "Zwiększenie częstotliwości testów",
                "Rozszerzenie zakresu audytu",
                "Dodatkowe testy kontroli"
            ])
        elif overall_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "Standardowe procedury audytowe",
                "Regularne testy kontroli",
                "Monitoring kluczowych procesów"
            ])
        else:
            recommendations.extend([
                "Standardowe procedury audytowe",
                "Podstawowe testy kontroli"
            ])
        
        # Add specific recommendations based on risk factors
        for factor in risk_factors:
            if factor.level == RiskLevel.HIGH or factor.level == RiskLevel.CRITICAL:
                recommendations.append(f"Szczególna uwaga na: {factor.name}")
        
        return recommendations


class JournalEntryAnalyzer:
    """Analizator zapisów księgowych."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_anomaly_detectors()
    
    def _initialize_anomaly_detectors(self):
        """Inicjalizacja detektorów anomalii."""
        self.anomaly_detectors = {
            'weekend_entries': self._detect_weekend_entries,
            'round_amounts': self._detect_round_amounts,
            'large_amounts': self._detect_large_amounts,
            'suspicious_users': self._detect_suspicious_users,
            'duplicate_entries': self._detect_duplicate_entries,
            'cut_off_issues': self._detect_cut_off_issues
        }
    
    def analyze_entries(self, entries: List[JournalEntry]) -> List[Anomaly]:
        """Analiza zapisów księgowych pod kątem anomalii."""
        anomalies = []
        
        for detector_name, detector_func in self.anomaly_detectors.items():
            try:
                detector_anomalies = detector_func(entries)
                anomalies.extend(detector_anomalies)
            except Exception as e:
                self.logger.error(f"Error in detector {detector_name}: {e}")
        
        # Sort by severity and confidence
        anomalies.sort(key=lambda x: (x.severity.value, x.confidence), reverse=True)
        
        return anomalies
    
    def _detect_weekend_entries(self, entries: List[JournalEntry]) -> List[Anomaly]:
        """Wykrywanie zapisów w weekendy."""
        anomalies = []
        
        for entry in entries:
            if entry.date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                anomaly = Anomaly(
                    id=f"weekend_{entry.id}",
                    entry_id=entry.id,
                    anomaly_type="weekend_entry",
                    severity=RiskLevel.MEDIUM,
                    description=f"Zapis księgowy w weekend: {entry.date.strftime('%Y-%m-%d')}",
                    detected_at=datetime.now(),
                    confidence=0.9,
                    details={
                        'date': entry.date.isoformat(),
                        'weekday': entry.date.strftime('%A'),
                        'amount': entry.amount,
                        'description': entry.description
                    }
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_round_amounts(self, entries: List[JournalEntry]) -> List[Anomaly]:
        """Wykrywanie okrągłych kwot."""
        anomalies = []
        
        for entry in entries:
            amount = abs(entry.amount)
            if amount > 0:
                # Check if amount is round (ends with 000)
                if amount % 1000 == 0 and amount >= 10000:
                    anomaly = Anomaly(
                        id=f"round_{entry.id}",
                        entry_id=entry.id,
                        anomaly_type="round_amount",
                        severity=RiskLevel.LOW,
                        description=f"Okrągła kwota: {entry.amount:,.2f}",
                        detected_at=datetime.now(),
                        confidence=0.7,
                        details={
                            'amount': entry.amount,
                            'description': entry.description,
                            'account': entry.account_name
                        }
                    )
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_large_amounts(self, entries: List[JournalEntry]) -> List[Anomaly]:
        """Wykrywanie dużych kwot."""
        anomalies = []
        
        # Calculate threshold (e.g., 95th percentile)
        amounts = [abs(entry.amount) for entry in entries if entry.amount != 0]
        if amounts:
            threshold = statistics.quantiles(amounts, n=20)[18]  # 95th percentile
            
            for entry in entries:
                if abs(entry.amount) > threshold:
                    anomaly = Anomaly(
                        id=f"large_{entry.id}",
                        entry_id=entry.id,
                        anomaly_type="large_amount",
                        severity=RiskLevel.HIGH,
                        description=f"Duża kwota: {entry.amount:,.2f} (próg: {threshold:,.2f})",
                        detected_at=datetime.now(),
                        confidence=0.8,
                        details={
                            'amount': entry.amount,
                            'threshold': threshold,
                            'description': entry.description,
                            'account': entry.account_name
                        }
                    )
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_suspicious_users(self, entries: List[JournalEntry]) -> List[Anomaly]:
        """Wykrywanie podejrzanych użytkowników."""
        anomalies = []
        
        # Count entries per user
        user_counts = {}
        user_amounts = {}
        
        for entry in entries:
            user_id = entry.user_id
            if user_id not in user_counts:
                user_counts[user_id] = 0
                user_amounts[user_id] = 0
            user_counts[user_id] += 1
            user_amounts[user_id] += abs(entry.amount)
        
        # Find users with unusual activity
        if user_counts:
            avg_entries = statistics.mean(user_counts.values())
            avg_amount = statistics.mean(user_amounts.values())
            
            for user_id, count in user_counts.items():
                if count > avg_entries * 2 or user_amounts[user_id] > avg_amount * 3:
                    anomaly = Anomaly(
                        id=f"suspicious_user_{user_id}",
                        entry_id="",
                        anomaly_type="suspicious_user",
                        severity=RiskLevel.MEDIUM,
                        description=f"Podejrzana aktywność użytkownika: {user_id}",
                        detected_at=datetime.now(),
                        confidence=0.6,
                        details={
                            'user_id': user_id,
                            'entry_count': count,
                            'total_amount': user_amounts[user_id],
                            'avg_entries': avg_entries,
                            'avg_amount': avg_amount
                        }
                    )
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_duplicate_entries(self, entries: List[JournalEntry]) -> List[Anomaly]:
        """Wykrywanie duplikatów zapisów."""
        anomalies = []
        
        # Group entries by key fields
        entry_groups = {}
        for entry in entries:
            key = f"{entry.date.date()}_{entry.account_code}_{entry.amount}_{entry.description[:50]}"
            if key not in entry_groups:
                entry_groups[key] = []
            entry_groups[key].append(entry)
        
        # Find duplicates
        for key, group in entry_groups.items():
            if len(group) > 1:
                for entry in group:
                    anomaly = Anomaly(
                        id=f"duplicate_{entry.id}",
                        entry_id=entry.id,
                        anomaly_type="duplicate_entry",
                        severity=RiskLevel.HIGH,
                        description=f"Prawdopodobny duplikat zapisu",
                        detected_at=datetime.now(),
                        confidence=0.8,
                        details={
                            'duplicate_count': len(group),
                            'date': entry.date.isoformat(),
                            'account': entry.account_name,
                            'amount': entry.amount,
                            'description': entry.description
                        }
                    )
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_cut_off_issues(self, entries: List[JournalEntry]) -> List[Anomaly]:
        """Wykrywanie problemów z cut-off."""
        anomalies = []
        
        # Check for entries near period end
        period_end = datetime.now().replace(day=31, hour=23, minute=59, second=59)
        period_start = period_end.replace(day=1, hour=0, minute=0, second=0)
        
        for entry in entries:
            if period_start <= entry.date <= period_end:
                # Check for unusual timing
                if entry.date.hour >= 22 or entry.date.hour <= 6:
                    anomaly = Anomaly(
                        id=f"cutoff_{entry.id}",
                        entry_id=entry.id,
                        anomaly_type="cut_off_issue",
                        severity=RiskLevel.MEDIUM,
                        description=f"Zapis w nietypowej porze: {entry.date.strftime('%Y-%m-%d %H:%M')}",
                        detected_at=datetime.now(),
                        confidence=0.7,
                        details={
                            'date': entry.date.isoformat(),
                            'hour': entry.date.hour,
                            'amount': entry.amount,
                            'description': entry.description
                        }
                    )
                    anomalies.append(anomaly)
        
        return anomalies


class SamplingEngine:
    """Silnik doboru próby."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def mus_sampling(self, 
                    population: List[Dict[str, Any]], 
                    confidence_level: float = 0.95,
                    tolerable_error: float = 0.05,
                    expected_error: float = 0.01) -> SamplingResult:
        """Monetary Unit Sampling (MUS)."""
        try:
            # Calculate total monetary value
            total_value = sum(item.get('amount', 0) for item in population)
            
            if total_value == 0:
                raise ValidationError("Population total value cannot be zero")
            
            # Calculate sample size
            sample_size = self._calculate_mus_sample_size(
                total_value, confidence_level, tolerable_error, expected_error
            )
            
            # Calculate sampling interval
            sampling_interval = total_value / sample_size
            
            # Select items using systematic sampling
            selected_items = self._systematic_sampling(population, sampling_interval)
            
            # Calculate upper error limit
            upper_error_limit = self._calculate_upper_error_limit(
                selected_items, sampling_interval, confidence_level
            )
            
            return SamplingResult(
                method=SamplingMethod.MUS,
                population_size=len(population),
                sample_size=len(selected_items),
                confidence_level=confidence_level,
                tolerable_error=tolerable_error,
                expected_error=expected_error,
                selected_items=selected_items,
                sampling_interval=sampling_interval,
                upper_error_limit=upper_error_limit
            )
            
        except Exception as e:
            self.logger.error(f"MUS sampling failed: {e}")
            raise FileProcessingError(f"MUS sampling failed: {e}")
    
    def statistical_sampling(self, 
                           population: List[Dict[str, Any]], 
                           confidence_level: float = 0.95,
                           margin_of_error: float = 0.05) -> SamplingResult:
        """Statystyczny dobór próby."""
        try:
            population_size = len(population)
            
            # Calculate sample size using standard formula
            z_score = self._get_z_score(confidence_level)
            sample_size = int((z_score ** 2 * 0.25) / (margin_of_error ** 2))
            
            # Adjust for finite population
            if sample_size > population_size:
                sample_size = population_size
            
            # Random sampling
            selected_items = random.sample(population, sample_size)
            
            return SamplingResult(
                method=SamplingMethod.STATISTICAL,
                population_size=population_size,
                sample_size=sample_size,
                confidence_level=confidence_level,
                tolerable_error=margin_of_error,
                expected_error=0.0,
                selected_items=selected_items,
                sampling_interval=0.0,
                upper_error_limit=0.0
            )
            
        except Exception as e:
            self.logger.error(f"Statistical sampling failed: {e}")
            raise FileProcessingError(f"Statistical sampling failed: {e}")
    
    def _calculate_mus_sample_size(self, 
                                 total_value: float, 
                                 confidence_level: float,
                                 tolerable_error: float, 
                                 expected_error: float) -> int:
        """Obliczenie wielkości próby dla MUS."""
        z_score = self._get_z_score(confidence_level)
        
        # MUS sample size formula
        sample_size = (z_score ** 2 * total_value * (1 + expected_error)) / (tolerable_error * total_value)
        
        return max(int(sample_size), 1)
    
    def _systematic_sampling(self, 
                           population: List[Dict[str, Any]], 
                           sampling_interval: float) -> List[Dict[str, Any]]:
        """Systematyczny dobór próby."""
        selected_items = []
        cumulative_value = 0
        
        # Sort population by amount (descending)
        sorted_population = sorted(population, key=lambda x: x.get('amount', 0), reverse=True)
        
        # Select items
        for item in sorted_population:
            cumulative_value += item.get('amount', 0)
            if cumulative_value >= sampling_interval:
                selected_items.append(item)
                cumulative_value = 0
        
        return selected_items
    
    def _calculate_upper_error_limit(self, 
                                   selected_items: List[Dict[str, Any]], 
                                   sampling_interval: float,
                                   confidence_level: float) -> float:
        """Obliczenie górnej granicy błędu."""
        if not selected_items:
            return 0.0
        
        # Count errors (items with amount > sampling_interval)
        error_count = sum(1 for item in selected_items if item.get('amount', 0) > sampling_interval)
        
        # Calculate upper error limit
        z_score = self._get_z_score(confidence_level)
        upper_error_limit = (error_count + 1) * sampling_interval * z_score
        
        return upper_error_limit
    
    def _get_z_score(self, confidence_level: float) -> float:
        """Pobranie wartości Z dla danego poziomu ufności."""
        z_scores = {
            0.90: 1.645,
            0.95: 1.96,
            0.99: 2.576
        }
        return z_scores.get(confidence_level, 1.96)


class AuditAnalytics:
    """Główna klasa analityki audytowej."""
    
    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path.home() / '.ai-auditor' / 'audit_analytics'
        
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.risk_analyzer = RiskAnalyzer()
        self.journal_analyzer = JournalEntryAnalyzer()
        self.sampling_engine = SamplingEngine()
        
        # Results storage
        self.risk_assessments: List[RiskAssessment] = []
        self.anomalies: List[Anomaly] = []
        self.sampling_results: List[SamplingResult] = []
    
    def perform_risk_assessment(self, custom_risks: List[RiskFactor] = None) -> RiskAssessment:
        """Przeprowadzenie oceny ryzyka."""
        try:
            assessment = self.risk_analyzer.assess_risk(custom_risks)
            self.risk_assessments.append(assessment)
            
            # Save to file
            self._save_risk_assessment(assessment)
            
            self.logger.info(f"Risk assessment completed: {assessment.id}")
            return assessment
            
        except Exception as e:
            self.logger.error(f"Risk assessment failed: {e}")
            raise FileProcessingError(f"Risk assessment failed: {e}")
    
    def analyze_journal_entries(self, entries: List[JournalEntry]) -> List[Anomaly]:
        """Analiza zapisów księgowych."""
        try:
            anomalies = self.journal_analyzer.analyze_entries(entries)
            self.anomalies.extend(anomalies)
            
            # Save to file
            self._save_anomalies(anomalies)
            
            self.logger.info(f"Journal entry analysis completed: {len(anomalies)} anomalies found")
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Journal entry analysis failed: {e}")
            raise FileProcessingError(f"Journal entry analysis failed: {e}")
    
    def perform_sampling(self, 
                        population: List[Dict[str, Any]], 
                        method: SamplingMethod,
                        **kwargs) -> SamplingResult:
        """Przeprowadzenie doboru próby."""
        try:
            if method == SamplingMethod.MUS:
                result = self.sampling_engine.mus_sampling(population, **kwargs)
            elif method == SamplingMethod.STATISTICAL:
                result = self.sampling_engine.statistical_sampling(population, **kwargs)
            else:
                raise ValueError(f"Unsupported sampling method: {method}")
            
            self.sampling_results.append(result)
            
            # Save to file
            self._save_sampling_result(result)
            
            self.logger.info(f"Sampling completed: {method.value}, {result.sample_size} items selected")
            return result
            
        except Exception as e:
            self.logger.error(f"Sampling failed: {e}")
            raise FileProcessingError(f"Sampling failed: {e}")
    
    def generate_risk_table(self, assessment: RiskAssessment) -> Dict[str, Any]:
        """Generowanie tabeli ryzyk."""
        try:
            risk_table = {
                'assessment_id': assessment.id,
                'title': assessment.title,
                'assessment_date': assessment.assessment_date.isoformat(),
                'overall_risk_level': assessment.overall_risk_level.value,
                'key_risks': assessment.key_risks,
                'recommendations': assessment.recommendations,
                'next_assessment': assessment.next_assessment.isoformat(),
                'risk_factors': []
            }
            
            for factor in assessment.risk_factors:
                risk_table['risk_factors'].append({
                    'id': factor.id,
                    'name': factor.name,
                    'category': factor.category.value,
                    'level': factor.level.value,
                    'description': factor.description,
                    'impact': factor.impact,
                    'likelihood': factor.likelihood,
                    'risk_score': factor.impact * factor.likelihood,
                    'controls': factor.controls,
                    'mitigation': factor.mitigation,
                    'owner': factor.owner,
                    'last_review': factor.last_review.isoformat(),
                    'next_review': factor.next_review.isoformat()
                })
            
            return risk_table
            
        except Exception as e:
            self.logger.error(f"Risk table generation failed: {e}")
            raise FileProcessingError(f"Risk table generation failed: {e}")
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Podsumowanie analityki audytowej."""
        return {
            'risk_assessments_count': len(self.risk_assessments),
            'anomalies_count': len(self.anomalies),
            'sampling_results_count': len(self.sampling_results),
            'high_risk_anomalies': len([a for a in self.anomalies if a.severity == RiskLevel.HIGH]),
            'critical_risk_anomalies': len([a for a in self.anomalies if a.severity == RiskLevel.CRITICAL]),
            'latest_assessment': self.risk_assessments[-1].id if self.risk_assessments else None,
            'latest_assessment_date': self.risk_assessments[-1].assessment_date.isoformat() if self.risk_assessments else None
        }
    
    def _save_risk_assessment(self, assessment: RiskAssessment):
        """Zapisanie oceny ryzyka."""
        try:
            file_path = self.data_dir / f"risk_assessment_{assessment.id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(assessment), f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save risk assessment: {e}")
    
    def _save_anomalies(self, anomalies: List[Anomaly]):
        """Zapisanie anomalii."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = self.data_dir / f"anomalies_{timestamp}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([asdict(anomaly) for anomaly in anomalies], f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save anomalies: {e}")
    
    def _save_sampling_result(self, result: SamplingResult):
        """Zapisanie wyniku doboru próby."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = self.data_dir / f"sampling_{result.method.value}_{timestamp}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(result), f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save sampling result: {e}")
