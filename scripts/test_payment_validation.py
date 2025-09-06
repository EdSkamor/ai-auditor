#!/usr/bin/env python3
"""
Test script dla walidacji płatności/kontrahentów.
"""

import sys
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.payment_validation import (
    PaymentValidationManager, Payment, Contractor, PaymentType, 
    ValidationStatus, AMLRiskLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_payment_validation():
    """Test walidacji płatności."""
    print("🧪 Testing Payment Validation...")
    
    # Initialize manager
    manager = PaymentValidationManager()
    
    # Test valid payment
    valid_payment = Payment(
        id="PAY_001",
        amount=1500.00,
        currency="PLN",
        date=datetime.now() - timedelta(days=1),
        payment_type=PaymentType.TRANSFER,
        sender_account="PL1234567890123456789012345",
        receiver_account="PL9876543210987654321098765",
        sender_name="ACME Corporation",
        receiver_name="Test Company",
        description="Payment for services",
        reference="REF-001",
        transaction_id="TXN-001",
        bank_code="123",
        country_code="PL"
    )
    
    result = manager.validate_payment(valid_payment)
    print(f"✅ Valid payment validation: {result.validation_status.value}")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Warnings: {len(result.warnings)}")
    
    # Test invalid payment
    invalid_payment = Payment(
        id="PAY_002",
        amount=-100.00,  # Negative amount
        currency="INVALID",  # Invalid currency
        date=datetime.now() + timedelta(days=1),  # Future date
        payment_type=PaymentType.TRANSFER,
        sender_account="INVALID_IBAN",
        receiver_account="INVALID_IBAN",
        sender_name="",
        receiver_name="",
        description="",  # Empty description
        reference="",
        transaction_id="TXN-002",
        bank_code="123",
        country_code="PL"
    )
    
    result = manager.validate_payment(invalid_payment)
    print(f"❌ Invalid payment validation: {result.validation_status.value}")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Warnings: {len(result.warnings)}")
    
    # Test suspicious payment
    suspicious_payment = Payment(
        id="PAY_003",
        amount=150000.00,  # Large amount
        currency="EUR",
        date=datetime.now() - timedelta(days=1),
        payment_type=PaymentType.TRANSFER,
        sender_account="PL1234567890123456789012345",
        receiver_account="PL9876543210987654321098765",
        sender_name="ACME Corporation",
        receiver_name="Test Company",
        description="Urgent cash transfer for bitcoin",  # Suspicious keywords
        reference="REF-003",
        transaction_id="TXN-003",
        bank_code="123",
        country_code="PL"
    )
    
    result = manager.validate_payment(suspicious_payment)
    print(f"⚠️ Suspicious payment validation: {result.validation_status.value}")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Warnings: {len(result.warnings)}")
    
    print("✅ Payment validation tests completed!")


def test_contractor_validation():
    """Test walidacji kontrahentów."""
    print("\n🧪 Testing Contractor Validation...")
    
    # Initialize manager
    manager = PaymentValidationManager()
    
    # Test valid contractor
    valid_contractor = Contractor(
        id="CONTRACTOR_001",
        name="ACME Corporation Sp. z o.o.",
        nip="1234567890",
        regon="123456789",
        krs="0000123456",
        address="ul. Testowa 123",
        city="Warszawa",
        postal_code="00-001",
        country="Poland",
        phone="+48123456789",
        email="test@acme.com",
        website="https://acme.com",
        legal_form="Sp. z o.o.",
        registration_date=datetime(2020, 1, 1),
        status="active",
        vat_status="active",
        account_numbers=["PL1234567890123456789012345"]
    )
    
    result = manager.validate_contractor(valid_contractor)
    print(f"✅ Valid contractor validation: {result.validation_status.value}")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Warnings: {len(result.warnings)}")
    
    # Test invalid contractor
    invalid_contractor = Contractor(
        id="CONTRACTOR_002",
        name="",  # Empty name
        nip="INVALID",  # Invalid NIP
        regon="INVALID",  # Invalid REGON
        krs="INVALID",  # Invalid KRS
        address="",  # Empty address
        city="",  # Empty city
        postal_code="INVALID",  # Invalid postal code
        country="Poland",
        phone="INVALID",  # Invalid phone
        email="INVALID",  # Invalid email
        website="",
        legal_form="",
        registration_date=None,
        status="",
        vat_status="",
        account_numbers=["INVALID_IBAN"]
    )
    
    result = manager.validate_contractor(invalid_contractor)
    print(f"❌ Invalid contractor validation: {result.validation_status.value}")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Warnings: {len(result.warnings)}")
    
    print("✅ Contractor validation tests completed!")


def test_aml_monitoring():
    """Test monitoringu AML."""
    print("\n🧪 Testing AML Monitoring...")
    
    # Initialize manager
    manager = PaymentValidationManager()
    
    # Test large transaction
    large_payment = Payment(
        id="PAY_LARGE",
        amount=150000.00,  # Large amount
        currency="PLN",
        date=datetime.now() - timedelta(days=1),
        payment_type=PaymentType.TRANSFER,
        sender_account="PL1234567890123456789012345",
        receiver_account="PL9876543210987654321098765",
        sender_name="ACME Corporation",
        receiver_name="Test Company",
        description="Large transaction",
        reference="REF-LARGE",
        transaction_id="TXN-LARGE",
        bank_code="123",
        country_code="PL"
    )
    
    alerts = manager.monitor_aml(large_payment)
    print(f"🚨 Large transaction AML alerts: {len(alerts)}")
    for alert in alerts:
        print(f"   - {alert.alert_type}: {alert.risk_level.value} - {alert.description}")
    
    # Test suspicious payment
    suspicious_payment = Payment(
        id="PAY_SUSPICIOUS",
        amount=50000.00,
        currency="PLN",
        date=datetime.now() - timedelta(days=1),
        payment_type=PaymentType.TRANSFER,
        sender_account="PL1234567890123456789012345",
        receiver_account="PL9876543210987654321098765",
        sender_name="TERRORIST_ORG",  # Suspicious name
        receiver_name="Test Company",
        description="Urgent cash transfer for bitcoin",  # Suspicious keywords
        reference="REF-SUSPICIOUS",
        transaction_id="TXN-SUSPICIOUS",
        bank_code="123",
        country_code="PL"
    )
    
    alerts = manager.monitor_aml(suspicious_payment)
    print(f"🚨 Suspicious payment AML alerts: {len(alerts)}")
    for alert in alerts:
        print(f"   - {alert.alert_type}: {alert.risk_level.value} - {alert.description}")
    
    # Test PEP contractor
    pep_contractor = Contractor(
        id="CONTRACTOR_PEP",
        name="POLITICIAN Corporation",  # PEP name
        nip="1234567890",
        regon="123456789",
        krs="0000123456",
        address="ul. Testowa 123",
        city="Warszawa",
        postal_code="00-001",
        country="Poland",
        phone="+48123456789",
        email="test@politician.com",
        website="https://politician.com",
        legal_form="Sp. z o.o.",
        registration_date=datetime(2020, 1, 1),
        status="active",
        vat_status="active",
        account_numbers=["PL1234567890123456789012345"]
    )
    
    alerts = manager.monitor_aml(pep_contractor)
    print(f"🚨 PEP contractor AML alerts: {len(alerts)}")
    for alert in alerts:
        print(f"   - {alert.alert_type}: {alert.risk_level.value} - {alert.description}")
    
    print("✅ AML monitoring tests completed!")


def test_batch_validation():
    """Test walidacji wsadowej."""
    print("\n🧪 Testing Batch Validation...")
    
    # Initialize manager
    manager = PaymentValidationManager()
    
    # Create test payments
    payments = []
    for i in range(5):
        payment = Payment(
            id=f"PAY_BATCH_{i:03d}",
            amount=1000.00 + i * 100,
            currency="PLN",
            date=datetime.now() - timedelta(days=i),
            payment_type=PaymentType.TRANSFER,
            sender_account="PL1234567890123456789012345",
            receiver_account="PL9876543210987654321098765",
            sender_name=f"Sender {i}",
            receiver_name=f"Receiver {i}",
            description=f"Payment {i}",
            reference=f"REF-{i:03d}",
            transaction_id=f"TXN-{i:03d}",
            bank_code="123",
            country_code="PL"
        )
        payments.append(payment)
    
    # Batch validate payments
    results = manager.batch_validate_payments(payments)
    print(f"📊 Batch payment validation: {len(results)} results")
    
    valid_count = len([r for r in results if r.validation_status == ValidationStatus.VALID])
    invalid_count = len([r for r in results if r.validation_status == ValidationStatus.INVALID])
    warning_count = len([r for r in results if r.validation_status == ValidationStatus.WARNING])
    
    print(f"   Valid: {valid_count}")
    print(f"   Invalid: {invalid_count}")
    print(f"   Warnings: {warning_count}")
    
    # Create test contractors
    contractors = []
    for i in range(3):
        contractor = Contractor(
            id=f"CONTRACTOR_BATCH_{i:03d}",
            name=f"Contractor {i} Sp. z o.o.",
            nip=f"123456789{i}",
            regon=f"12345678{i}",
            krs=f"000012345{i}",
            address=f"ul. Testowa {i}",
            city="Warszawa",
            postal_code="00-001",
            country="Poland",
            phone=f"+4812345678{i}",
            email=f"test{i}@contractor.com",
            website=f"https://contractor{i}.com",
            legal_form="Sp. z o.o.",
            registration_date=datetime(2020, 1, 1),
            status="active",
            vat_status="active",
            account_numbers=[f"PL123456789012345678901234{i}"]
        )
        contractors.append(contractor)
    
    # Batch validate contractors
    results = manager.batch_validate_contractors(contractors)
    print(f"📊 Batch contractor validation: {len(results)} results")
    
    valid_count = len([r for r in results if r.validation_status == ValidationStatus.VALID])
    invalid_count = len([r for r in results if r.validation_status == ValidationStatus.INVALID])
    warning_count = len([r for r in results if r.validation_status == ValidationStatus.WARNING])
    
    print(f"   Valid: {valid_count}")
    print(f"   Invalid: {invalid_count}")
    print(f"   Warnings: {warning_count}")
    
    print("✅ Batch validation tests completed!")


def test_validation_summary():
    """Test podsumowania walidacji."""
    print("\n🧪 Testing Validation Summary...")
    
    # Initialize manager
    manager = PaymentValidationManager()
    
    # Create some test data
    payment = Payment(
        id="PAY_SUMMARY",
        amount=1000.00,
        currency="PLN",
        date=datetime.now() - timedelta(days=1),
        payment_type=PaymentType.TRANSFER,
        sender_account="PL1234567890123456789012345",
        receiver_account="PL9876543210987654321098765",
        sender_name="ACME Corporation",
        receiver_name="Test Company",
        description="Payment for services",
        reference="REF-SUMMARY",
        transaction_id="TXN-SUMMARY",
        bank_code="123",
        country_code="PL"
    )
    
    contractor = Contractor(
        id="CONTRACTOR_SUMMARY",
        name="ACME Corporation Sp. z o.o.",
        nip="1234567890",
        regon="123456789",
        krs="0000123456",
        address="ul. Testowa 123",
        city="Warszawa",
        postal_code="00-001",
        country="Poland",
        phone="+48123456789",
        email="test@acme.com",
        website="https://acme.com",
        legal_form="Sp. z o.o.",
        registration_date=datetime(2020, 1, 1),
        status="active",
        vat_status="active",
        account_numbers=["PL1234567890123456789012345"]
    )
    
    # Validate entities
    manager.validate_payment(payment)
    manager.validate_contractor(contractor)
    
    # Monitor AML
    manager.monitor_aml(payment)
    manager.monitor_aml(contractor)
    
    # Get summary
    summary = manager.get_validation_summary()
    print("📊 Validation Summary:")
    print(f"   Total validations: {summary['total_validations']}")
    print(f"   Valid: {summary['valid_count']}")
    print(f"   Invalid: {summary['invalid_count']}")
    print(f"   Warnings: {summary['warning_count']}")
    print(f"   Payment validations: {summary['payment_validations']}")
    print(f"   Contractor validations: {summary['contractor_validations']}")
    print(f"   Total AML alerts: {summary['total_aml_alerts']}")
    print(f"   Critical AML alerts: {summary['critical_aml_alerts']}")
    print(f"   High AML alerts: {summary['high_aml_alerts']}")
    print(f"   Average confidence: {summary['average_confidence']:.2f}")
    
    print("✅ Validation summary tests completed!")


def main():
    """Main test function."""
    print("🚀 Starting Payment Validation Tests...")
    
    try:
        test_payment_validation()
        test_contractor_validation()
        test_aml_monitoring()
        test_batch_validation()
        test_validation_summary()
        
        print("\n🎉 All Payment Validation tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
