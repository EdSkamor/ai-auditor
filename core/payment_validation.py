"""
Walidacja płatności/kontrahentów
System walidacji płatności, kontrahentów i AML/KYC.
"""

import json
import logging
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import requests
import time

from .exceptions import ValidationError, APIError, FileProcessingError


class ValidationStatus(Enum):
    """Statusy walidacji."""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    PENDING = "pending"
    ERROR = "error"


class PaymentType(Enum):
    """Typy płatności."""
    TRANSFER = "transfer"
    CARD = "card"
    CASH = "cash"
    CHECK = "check"
    CRYPTOCURRENCY = "cryptocurrency"


class AMLRiskLevel(Enum):
    """Poziomy ryzyka AML."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Payment:
    """Płatność."""
    id: str
    amount: float
    currency: str
    date: datetime
    payment_type: PaymentType
    sender_account: str
    receiver_account: str
    sender_name: str
    receiver_name: str
    description: str
    reference: str
    transaction_id: str
    bank_code: str
    country_code: str


@dataclass
class Contractor:
    """Kontrahent."""
    id: str
    name: str
    nip: str
    regon: str
    krs: str
    address: str
    city: str
    postal_code: str
    country: str
    phone: str
    email: str
    website: str
    legal_form: str
    registration_date: Optional[datetime]
    status: str
    vat_status: str
    account_numbers: List[str]


@dataclass
class ValidationResult:
    """Wynik walidacji."""
    id: str
    entity_type: str  # payment, contractor
    entity_id: str
    validation_status: ValidationStatus
    confidence: float
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]
    validated_at: datetime
    validator_name: str


@dataclass
class AMLAlert:
    """Alert AML."""
    id: str
    entity_id: str
    entity_type: str
    risk_level: AMLRiskLevel
    alert_type: str
    description: str
    detected_at: datetime
    details: Dict[str, Any]
    status: str  # new, reviewed, resolved
    assigned_to: Optional[str]


class PaymentValidator:
    """Walidator płatności."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_validators()
    
    def _initialize_validators(self):
        """Inicjalizacja walidatorów."""
        self.validators = {
            'iban_validation': self._validate_iban,
            'amount_validation': self._validate_amount,
            'currency_validation': self._validate_currency,
            'date_validation': self._validate_date,
            'description_validation': self._validate_description,
            'reference_validation': self._validate_reference
        }
    
    def validate_payment(self, payment: Payment) -> ValidationResult:
        """Walidacja płatności."""
        errors = []
        warnings = []
        details = {}
        
        # Run all validators
        for validator_name, validator_func in self.validators.items():
            try:
                result = validator_func(payment)
                if result['status'] == 'error':
                    errors.extend(result['errors'])
                elif result['status'] == 'warning':
                    warnings.extend(result['warnings'])
                details[validator_name] = result
            except Exception as e:
                self.logger.error(f"Validator {validator_name} failed: {e}")
                errors.append(f"Validator {validator_name} failed: {str(e)}")
        
        # Determine overall status
        if errors:
            status = ValidationStatus.INVALID
        elif warnings:
            status = ValidationStatus.WARNING
        else:
            status = ValidationStatus.VALID
        
        # Calculate confidence
        confidence = self._calculate_confidence(errors, warnings, details)
        
        return ValidationResult(
            id=f"PV_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            entity_type="payment",
            entity_id=payment.id,
            validation_status=status,
            confidence=confidence,
            errors=errors,
            warnings=warnings,
            details=details,
            validated_at=datetime.now(),
            validator_name="PaymentValidator"
        )
    
    def _validate_iban(self, payment: Payment) -> Dict[str, Any]:
        """Walidacja numeru IBAN."""
        result = {'status': 'valid', 'errors': [], 'warnings': []}
        
        # Validate sender account
        if not self._is_valid_iban(payment.sender_account):
            result['errors'].append(f"Invalid sender IBAN: {payment.sender_account}")
            result['status'] = 'error'
        
        # Validate receiver account
        if not self._is_valid_iban(payment.receiver_account):
            result['errors'].append(f"Invalid receiver IBAN: {payment.receiver_account}")
            result['status'] = 'error'
        
        # Check for same account
        if payment.sender_account == payment.receiver_account:
            result['warnings'].append("Sender and receiver accounts are the same")
            if result['status'] == 'valid':
                result['status'] = 'warning'
        
        return result
    
    def _validate_amount(self, payment: Payment) -> Dict[str, Any]:
        """Walidacja kwoty."""
        result = {'status': 'valid', 'errors': [], 'warnings': []}
        
        # Check amount is positive
        if payment.amount <= 0:
            result['errors'].append(f"Amount must be positive: {payment.amount}")
            result['status'] = 'error'
        
        # Check for suspicious amounts
        if payment.amount > 1000000:  # 1M
            result['warnings'].append(f"Large amount: {payment.amount:,.2f}")
            if result['status'] == 'valid':
                result['status'] = 'warning'
        
        # Check for round amounts
        if payment.amount % 1000 == 0 and payment.amount >= 10000:
            result['warnings'].append(f"Round amount: {payment.amount:,.2f}")
            if result['status'] == 'valid':
                result['status'] = 'warning'
        
        return result
    
    def _validate_currency(self, payment: Payment) -> Dict[str, Any]:
        """Walidacja waluty."""
        result = {'status': 'valid', 'errors': [], 'warnings': []}
        
        # Check currency code
        valid_currencies = ['PLN', 'EUR', 'USD', 'GBP', 'CHF']
        if payment.currency not in valid_currencies:
            result['errors'].append(f"Invalid currency: {payment.currency}")
            result['status'] = 'error'
        
        # Check for currency mismatch with country
        if payment.country_code == 'PL' and payment.currency != 'PLN':
            result['warnings'].append(f"Non-PLN currency for Polish transaction: {payment.currency}")
            if result['status'] == 'valid':
                result['status'] = 'warning'
        
        return result
    
    def _validate_date(self, payment: Payment) -> Dict[str, Any]:
        """Walidacja daty."""
        result = {'status': 'valid', 'errors': [], 'warnings': []}
        
        # Check date is not in future
        if payment.date > datetime.now():
            result['errors'].append(f"Payment date in future: {payment.date}")
            result['status'] = 'error'
        
        # Check date is not too old
        if payment.date < datetime.now() - timedelta(days=365):
            result['warnings'].append(f"Old payment date: {payment.date}")
            if result['status'] == 'valid':
                result['status'] = 'warning'
        
        # Check for weekend payments
        if payment.date.weekday() >= 5:
            result['warnings'].append(f"Weekend payment: {payment.date.strftime('%A')}")
            if result['status'] == 'valid':
                result['status'] = 'warning'
        
        return result
    
    def _validate_description(self, payment: Payment) -> Dict[str, Any]:
        """Walidacja opisu."""
        result = {'status': 'valid', 'errors': [], 'warnings': []}
        
        # Check description length
        if len(payment.description) < 5:
            result['warnings'].append("Description too short")
            if result['status'] == 'valid':
                result['status'] = 'warning'
        
        # Check for suspicious keywords
        suspicious_keywords = ['cash', 'bitcoin', 'crypto', 'anonymous', 'urgent']
        description_lower = payment.description.lower()
        for keyword in suspicious_keywords:
            if keyword in description_lower:
                result['warnings'].append(f"Suspicious keyword in description: {keyword}")
                if result['status'] == 'valid':
                    result['status'] = 'warning'
        
        return result
    
    def _validate_reference(self, payment: Payment) -> Dict[str, Any]:
        """Walidacja referencji."""
        result = {'status': 'valid', 'errors': [], 'warnings': []}
        
        # Check reference format
        if not re.match(r'^[A-Z0-9\-/]+$', payment.reference):
            result['warnings'].append(f"Invalid reference format: {payment.reference}")
            if result['status'] == 'valid':
                result['status'] = 'warning'
        
        return result
    
    def _is_valid_iban(self, iban: str) -> bool:
        """Walidacja numeru IBAN."""
        if not iban:
            return False
        
        # Remove spaces and convert to uppercase
        iban = iban.replace(' ', '').upper()
        
        # Check length (PL: 28, DE: 22, etc.)
        if len(iban) < 15 or len(iban) > 34:
            return False
        
        # Check format (2 letters + 2 digits + alphanumeric)
        if not re.match(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]+$', iban):
            return False
        
        # Mock validation - in real implementation, use proper IBAN validation
        return True
    
    def _calculate_confidence(self, errors: List[str], warnings: List[str], details: Dict[str, Any]) -> float:
        """Obliczenie pewności walidacji."""
        base_confidence = 1.0
        
        # Reduce confidence for errors
        base_confidence -= len(errors) * 0.2
        
        # Reduce confidence for warnings
        base_confidence -= len(warnings) * 0.1
        
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, base_confidence))


class ContractorValidator:
    """Walidator kontrahentów."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_validators()
    
    def _initialize_validators(self):
        """Inicjalizacja walidatorów."""
        self.validators = {
            'nip_validation': self._validate_nip,
            'regon_validation': self._validate_regon,
            'krs_validation': self._validate_krs,
            'address_validation': self._validate_address,
            'email_validation': self._validate_email,
            'phone_validation': self._validate_phone,
            'account_validation': self._validate_accounts
        }
    
    def validate_contractor(self, contractor: Contractor) -> ValidationResult:
        """Walidacja kontrahenta."""
        errors = []
        warnings = []
        details = {}
        
        # Run all validators
        for validator_name, validator_func in self.validators.items():
            try:
                result = validator_func(contractor)
                if result['status'] == 'error':
                    errors.extend(result['errors'])
                elif result['status'] == 'warning':
                    warnings.extend(result['warnings'])
                details[validator_name] = result
            except Exception as e:
                self.logger.error(f"Validator {validator_name} failed: {e}")
                errors.append(f"Validator {validator_name} failed: {str(e)}")
        
        # Determine overall status
        if errors:
            status = ValidationStatus.INVALID
        elif warnings:
            status = ValidationStatus.WARNING
        else:
            status = ValidationStatus.VALID
        
        # Calculate confidence
        confidence = self._calculate_confidence(errors, warnings, details)
        
        return ValidationResult(
            id=f"CV_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            entity_type="contractor",
            entity_id=contractor.id,
            validation_status=status,
            confidence=confidence,
            errors=errors,
            warnings=warnings,
            details=details,
            validated_at=datetime.now(),
            validator_name="ContractorValidator"
        )
    
    def _validate_nip(self, contractor: Contractor) -> Dict[str, Any]:
        """Walidacja NIP."""
        result = {'status': 'valid', 'errors': [], 'warnings': []}
        
        if not contractor.nip:
            result['errors'].append("NIP is required")
            result['status'] = 'error'
        elif not self._is_valid_nip(contractor.nip):
            result['errors'].append(f"Invalid NIP format: {contractor.nip}")
            result['status'] = 'error'
        
        return result
    
    def _validate_regon(self, contractor: Contractor) -> Dict[str, Any]:
        """Walidacja REGON."""
        result = {'status': 'valid', 'errors': [], 'warnings': []}
        
        if contractor.regon and not self._is_valid_regon(contractor.regon):
            result['warnings'].append(f"Invalid REGON format: {contractor.regon}")
            if result['status'] == 'valid':
                result['status'] = 'warning'
        
        return result
    
    def _validate_krs(self, contractor: Contractor) -> Dict[str, Any]:
        """Walidacja KRS."""
        result = {'status': 'valid', 'errors': [], 'warnings': []}
        
        if contractor.krs and not self._is_valid_krs(contractor.krs):
            result['warnings'].append(f"Invalid KRS format: {contractor.krs}")
            if result['status'] == 'valid':
                result['status'] = 'warning'
        
        return result
    
    def _validate_address(self, contractor: Contractor) -> Dict[str, Any]:
        """Walidacja adresu."""
        result = {'status': 'valid', 'errors': [], 'warnings': []}
        
        if not contractor.address:
            result['errors'].append("Address is required")
            result['status'] = 'error'
        elif len(contractor.address) < 10:
            result['warnings'].append("Address seems too short")
            if result['status'] == 'valid':
                result['status'] = 'warning'
        
        if not contractor.city:
            result['errors'].append("City is required")
            result['status'] = 'error'
        
        if not contractor.postal_code:
            result['errors'].append("Postal code is required")
            result['status'] = 'error'
        elif not self._is_valid_postal_code(contractor.postal_code):
            result['warnings'].append(f"Invalid postal code format: {contractor.postal_code}")
            if result['status'] == 'valid':
                result['status'] = 'warning'
        
        return result
    
    def _validate_email(self, contractor: Contractor) -> Dict[str, Any]:
        """Walidacja email."""
        result = {'status': 'valid', 'errors': [], 'warnings': []}
        
        if contractor.email and not self._is_valid_email(contractor.email):
            result['warnings'].append(f"Invalid email format: {contractor.email}")
            if result['status'] == 'valid':
                result['status'] = 'warning'
        
        return result
    
    def _validate_phone(self, contractor: Contractor) -> Dict[str, Any]:
        """Walidacja telefonu."""
        result = {'status': 'valid', 'errors': [], 'warnings': []}
        
        if contractor.phone and not self._is_valid_phone(contractor.phone):
            result['warnings'].append(f"Invalid phone format: {contractor.phone}")
            if result['status'] == 'valid':
                result['status'] = 'warning'
        
        return result
    
    def _validate_accounts(self, contractor: Contractor) -> Dict[str, Any]:
        """Walidacja kont bankowych."""
        result = {'status': 'valid', 'errors': [], 'warnings': []}
        
        if not contractor.account_numbers:
            result['warnings'].append("No bank accounts provided")
            if result['status'] == 'valid':
                result['status'] = 'warning'
        else:
            for account in contractor.account_numbers:
                if not self._is_valid_iban(account):
                    result['warnings'].append(f"Invalid account number: {account}")
                    if result['status'] == 'valid':
                        result['status'] = 'warning'
        
        return result
    
    def _is_valid_nip(self, nip: str) -> bool:
        """Walidacja NIP."""
        if not nip:
            return False
        
        # Remove spaces and dashes
        nip = nip.replace(' ', '').replace('-', '')
        
        # Check length
        if len(nip) != 10:
            return False
        
        # Check if all digits
        if not nip.isdigit():
            return False
        
        # Mock validation - in real implementation, use proper NIP validation
        return True
    
    def _is_valid_regon(self, regon: str) -> bool:
        """Walidacja REGON."""
        if not regon:
            return False
        
        # Remove spaces and dashes
        regon = regon.replace(' ', '').replace('-', '')
        
        # Check length (9 or 14 digits)
        if len(regon) not in [9, 14]:
            return False
        
        # Check if all digits
        if not regon.isdigit():
            return False
        
        return True
    
    def _is_valid_krs(self, krs: str) -> bool:
        """Walidacja KRS."""
        if not krs:
            return False
        
        # Remove spaces and dashes
        krs = krs.replace(' ', '').replace('-', '')
        
        # Check length (10 digits)
        if len(krs) != 10:
            return False
        
        # Check if all digits
        if not krs.isdigit():
            return False
        
        return True
    
    def _is_valid_postal_code(self, postal_code: str) -> bool:
        """Walidacja kodu pocztowego."""
        if not postal_code:
            return False
        
        # Polish postal code format: XX-XXX
        return re.match(r'^\d{2}-\d{3}$', postal_code) is not None
    
    def _is_valid_email(self, email: str) -> bool:
        """Walidacja email."""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Walidacja telefonu."""
        if not phone:
            return False
        
        # Remove spaces, dashes, parentheses
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Check if starts with + or country code
        if phone.startswith('+'):
            return len(phone) >= 10
        elif phone.startswith('48'):
            return len(phone) >= 11
        else:
            return len(phone) >= 9
    
    def _is_valid_iban(self, iban: str) -> bool:
        """Walidacja numeru IBAN."""
        if not iban:
            return False
        
        # Remove spaces and convert to uppercase
        iban = iban.replace(' ', '').upper()
        
        # Check length
        if len(iban) < 15 or len(iban) > 34:
            return False
        
        # Check format
        if not re.match(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]+$', iban):
            return False
        
        return True
    
    def _calculate_confidence(self, errors: List[str], warnings: List[str], details: Dict[str, Any]) -> float:
        """Obliczenie pewności walidacji."""
        base_confidence = 1.0
        
        # Reduce confidence for errors
        base_confidence -= len(errors) * 0.2
        
        # Reduce confidence for warnings
        base_confidence -= len(warnings) * 0.1
        
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, base_confidence))


class AMLMonitor:
    """Monitor AML/KYC."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_aml_rules()
    
    def _initialize_aml_rules(self):
        """Inicjalizacja reguł AML."""
        self.aml_rules = {
            'large_transaction': self._check_large_transaction,
            'frequent_transactions': self._check_frequent_transactions,
            'suspicious_patterns': self._check_suspicious_patterns,
            'sanctions_list': self._check_sanctions_list,
            'pep_list': self._check_pep_list
        }
    
    def monitor_payment(self, payment: Payment) -> List[AMLAlert]:
        """Monitoring płatności pod kątem AML."""
        alerts = []
        
        for rule_name, rule_func in self.aml_rules.items():
            try:
                rule_alerts = rule_func(payment)
                alerts.extend(rule_alerts)
            except Exception as e:
                self.logger.error(f"AML rule {rule_name} failed: {e}")
        
        return alerts
    
    def monitor_contractor(self, contractor: Contractor) -> List[AMLAlert]:
        """Monitoring kontrahenta pod kątem AML."""
        alerts = []
        
        # Check sanctions list
        sanctions_alerts = self._check_sanctions_list_contractor(contractor)
        alerts.extend(sanctions_alerts)
        
        # Check PEP list
        pep_alerts = self._check_pep_list_contractor(contractor)
        alerts.extend(pep_alerts)
        
        return alerts
    
    def _check_large_transaction(self, payment: Payment) -> List[AMLAlert]:
        """Sprawdzenie dużych transakcji."""
        alerts = []
        
        # Large transaction threshold
        if payment.amount > 100000:  # 100K
            alert = AMLAlert(
                id=f"AML_LARGE_{payment.id}",
                entity_id=payment.id,
                entity_type="payment",
                risk_level=AMLRiskLevel.HIGH,
                alert_type="large_transaction",
                description=f"Large transaction: {payment.amount:,.2f} {payment.currency}",
                detected_at=datetime.now(),
                details={
                    'amount': payment.amount,
                    'currency': payment.currency,
                    'threshold': 100000
                },
                status="new",
                assigned_to=None
            )
            alerts.append(alert)
        
        return alerts
    
    def _check_frequent_transactions(self, payment: Payment) -> List[AMLAlert]:
        """Sprawdzenie częstych transakcji."""
        alerts = []
        
        # This would require historical data - mock implementation
        if payment.amount > 50000 and payment.payment_type == PaymentType.TRANSFER:
            alert = AMLAlert(
                id=f"AML_FREQUENT_{payment.id}",
                entity_id=payment.id,
                entity_type="payment",
                risk_level=AMLRiskLevel.MEDIUM,
                alert_type="frequent_transactions",
                description="Potential frequent transaction pattern",
                detected_at=datetime.now(),
                details={
                    'amount': payment.amount,
                    'payment_type': payment.payment_type.value
                },
                status="new",
                assigned_to=None
            )
            alerts.append(alert)
        
        return alerts
    
    def _check_suspicious_patterns(self, payment: Payment) -> List[AMLAlert]:
        """Sprawdzenie podejrzanych wzorców."""
        alerts = []
        
        # Check for suspicious keywords in description
        suspicious_keywords = ['cash', 'bitcoin', 'crypto', 'anonymous', 'urgent', 'secret']
        description_lower = payment.description.lower()
        
        for keyword in suspicious_keywords:
            if keyword in description_lower:
                alert = AMLAlert(
                    id=f"AML_SUSPICIOUS_{payment.id}",
                    entity_id=payment.id,
                    entity_type="payment",
                    risk_level=AMLRiskLevel.MEDIUM,
                    alert_type="suspicious_patterns",
                    description=f"Suspicious keyword in description: {keyword}",
                    detected_at=datetime.now(),
                    details={
                        'keyword': keyword,
                        'description': payment.description
                    },
                    status="new",
                    assigned_to=None
                )
                alerts.append(alert)
        
        return alerts
    
    def _check_sanctions_list(self, payment: Payment) -> List[AMLAlert]:
        """Sprawdzenie listy sankcji."""
        alerts = []
        
        # Mock sanctions list
        sanctions_list = ['TERRORIST_ORG', 'SANCTIONS_ENTITY', 'BLACKLISTED']
        
        sender_lower = payment.sender_name.lower()
        receiver_lower = payment.receiver_name.lower()
        
        for sanction in sanctions_list:
            if sanction.lower() in sender_lower or sanction.lower() in receiver_lower:
                alert = AMLAlert(
                    id=f"AML_SANCTIONS_{payment.id}",
                    entity_id=payment.id,
                    entity_type="payment",
                    risk_level=AMLRiskLevel.CRITICAL,
                    alert_type="sanctions_list",
                    description=f"Entity on sanctions list: {sanction}",
                    detected_at=datetime.now(),
                    details={
                        'sanction': sanction,
                        'sender': payment.sender_name,
                        'receiver': payment.receiver_name
                    },
                    status="new",
                    assigned_to=None
                )
                alerts.append(alert)
        
        return alerts
    
    def _check_pep_list(self, payment: Payment) -> List[AMLAlert]:
        """Sprawdzenie listy PEP."""
        alerts = []
        
        # Mock PEP list
        pep_list = ['POLITICIAN', 'GOVERNMENT_OFFICIAL', 'PUBLIC_FIGURE']
        
        sender_lower = payment.sender_name.lower()
        receiver_lower = payment.receiver_name.lower()
        
        for pep in pep_list:
            if pep.lower() in sender_lower or pep.lower() in receiver_lower:
                alert = AMLAlert(
                    id=f"AML_PEP_{payment.id}",
                    entity_id=payment.id,
                    entity_type="payment",
                    risk_level=AMLRiskLevel.HIGH,
                    alert_type="pep_list",
                    description=f"PEP entity: {pep}",
                    detected_at=datetime.now(),
                    details={
                        'pep': pep,
                        'sender': payment.sender_name,
                        'receiver': payment.receiver_name
                    },
                    status="new",
                    assigned_to=None
                )
                alerts.append(alert)
        
        return alerts
    
    def _check_sanctions_list_contractor(self, contractor: Contractor) -> List[AMLAlert]:
        """Sprawdzenie listy sankcji dla kontrahenta."""
        alerts = []
        
        # Mock sanctions list
        sanctions_list = ['TERRORIST_ORG', 'SANCTIONS_ENTITY', 'BLACKLISTED']
        
        name_lower = contractor.name.lower()
        
        for sanction in sanctions_list:
            if sanction.lower() in name_lower:
                alert = AMLAlert(
                    id=f"AML_SANCTIONS_CONTRACTOR_{contractor.id}",
                    entity_id=contractor.id,
                    entity_type="contractor",
                    risk_level=AMLRiskLevel.CRITICAL,
                    alert_type="sanctions_list",
                    description=f"Contractor on sanctions list: {sanction}",
                    detected_at=datetime.now(),
                    details={
                        'sanction': sanction,
                        'contractor_name': contractor.name
                    },
                    status="new",
                    assigned_to=None
                )
                alerts.append(alert)
        
        return alerts
    
    def _check_pep_list_contractor(self, contractor: Contractor) -> List[AMLAlert]:
        """Sprawdzenie listy PEP dla kontrahenta."""
        alerts = []
        
        # Mock PEP list
        pep_list = ['POLITICIAN', 'GOVERNMENT_OFFICIAL', 'PUBLIC_FIGURE']
        
        name_lower = contractor.name.lower()
        
        for pep in pep_list:
            if pep.lower() in name_lower:
                alert = AMLAlert(
                    id=f"AML_PEP_CONTRACTOR_{contractor.id}",
                    entity_id=contractor.id,
                    entity_type="contractor",
                    risk_level=AMLRiskLevel.HIGH,
                    alert_type="pep_list",
                    description=f"PEP contractor: {pep}",
                    detected_at=datetime.now(),
                    details={
                        'pep': pep,
                        'contractor_name': contractor.name
                    },
                    status="new",
                    assigned_to=None
                )
                alerts.append(alert)
        
        return alerts


class PaymentValidationManager:
    """Menedżer walidacji płatności i kontrahentów."""
    
    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path.home() / '.ai-auditor' / 'payment_validation'
        
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.payment_validator = PaymentValidator()
        self.contractor_validator = ContractorValidator()
        self.aml_monitor = AMLMonitor()
        
        # Results storage
        self.validation_results: List[ValidationResult] = []
        self.aml_alerts: List[AMLAlert] = []
    
    def validate_payment(self, payment: Payment) -> ValidationResult:
        """Walidacja płatności."""
        try:
            result = self.payment_validator.validate_payment(payment)
            self.validation_results.append(result)
            
            # Save to file
            self._save_validation_result(result)
            
            self.logger.info(f"Payment validation completed: {result.id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Payment validation failed: {e}")
            raise FileProcessingError(f"Payment validation failed: {e}")
    
    def validate_contractor(self, contractor: Contractor) -> ValidationResult:
        """Walidacja kontrahenta."""
        try:
            result = self.contractor_validator.validate_contractor(contractor)
            self.validation_results.append(result)
            
            # Save to file
            self._save_validation_result(result)
            
            self.logger.info(f"Contractor validation completed: {result.id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Contractor validation failed: {e}")
            raise FileProcessingError(f"Contractor validation failed: {e}")
    
    def monitor_aml(self, entity: Union[Payment, Contractor]) -> List[AMLAlert]:
        """Monitoring AML."""
        try:
            if isinstance(entity, Payment):
                alerts = self.aml_monitor.monitor_payment(entity)
            elif isinstance(entity, Contractor):
                alerts = self.aml_monitor.monitor_contractor(entity)
            else:
                raise ValueError(f"Unsupported entity type: {type(entity)}")
            
            self.aml_alerts.extend(alerts)
            
            # Save to file
            self._save_aml_alerts(alerts)
            
            self.logger.info(f"AML monitoring completed: {len(alerts)} alerts")
            return alerts
            
        except Exception as e:
            self.logger.error(f"AML monitoring failed: {e}")
            raise FileProcessingError(f"AML monitoring failed: {e}")
    
    def batch_validate_payments(self, payments: List[Payment]) -> List[ValidationResult]:
        """Walidacja wielu płatności."""
        results = []
        
        for payment in payments:
            try:
                result = self.validate_payment(payment)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to validate payment {payment.id}: {e}")
                continue
        
        return results
    
    def batch_validate_contractors(self, contractors: List[Contractor]) -> List[ValidationResult]:
        """Walidacja wielu kontrahentów."""
        results = []
        
        for contractor in contractors:
            try:
                result = self.validate_contractor(contractor)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to validate contractor {contractor.id}: {e}")
                continue
        
        return results
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Podsumowanie walidacji."""
        return {
            'total_validations': len(self.validation_results),
            'valid_count': len([r for r in self.validation_results if r.validation_status == ValidationStatus.VALID]),
            'invalid_count': len([r for r in self.validation_results if r.validation_status == ValidationStatus.INVALID]),
            'warning_count': len([r for r in self.validation_results if r.validation_status == ValidationStatus.WARNING]),
            'payment_validations': len([r for r in self.validation_results if r.entity_type == 'payment']),
            'contractor_validations': len([r for r in self.validation_results if r.entity_type == 'contractor']),
            'total_aml_alerts': len(self.aml_alerts),
            'critical_aml_alerts': len([a for a in self.aml_alerts if a.risk_level == AMLRiskLevel.CRITICAL]),
            'high_aml_alerts': len([a for a in self.aml_alerts if a.risk_level == AMLRiskLevel.HIGH]),
            'average_confidence': sum(r.confidence for r in self.validation_results) / len(self.validation_results) if self.validation_results else 0
        }
    
    def _save_validation_result(self, result: ValidationResult):
        """Zapisanie wyniku walidacji."""
        try:
            file_path = self.data_dir / f"validation_{result.id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(result), f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save validation result: {e}")
    
    def _save_aml_alerts(self, alerts: List[AMLAlert]):
        """Zapisanie alertów AML."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = self.data_dir / f"aml_alerts_{timestamp}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([asdict(alert) for alert in alerts], f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save AML alerts: {e}")
