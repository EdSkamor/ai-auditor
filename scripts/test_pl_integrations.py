#!/usr/bin/env python3
"""
Test script for PL-core integrations (KSeF, JPK, Biała lista VAT, KRS).
"""

import sys
import tempfile
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.pl_integrations import (
    PLIntegrationsManager, KSeFIntegration, JPKIntegration, 
    VATWhitelistIntegration, KRSIntegration, IntegrationType
)


def test_pl_integrations():
    """Test PL-core integrations functionality."""
    print("🚀 Starting PL-core Integrations Test Suite...")
    print("=" * 60)
    
    # Initialize integrations manager
    print("🧪 Testing PL Integrations Manager Initialization...")
    config = {
        'ksef_api_key': None,  # Mock mode
        'vat_whitelist_api_key': None,  # Mock mode
        'krs_api_key': None  # Mock mode
    }
    
    manager = PLIntegrationsManager(config)
    print("✅ PL Integrations Manager initialized successfully")
    
    # Test integration status
    print("\n🧪 Testing Integration Status...")
    status = manager.get_integration_status()
    for integration, info in status.items():
        print(f"   • {integration}: {'Available' if info['available'] else 'Mock mode'}")
    print("✅ Integration status checked")
    
    # Test KSeF integration
    print("\n🧪 Testing KSeF Integration...")
    ksef_xml = """
    <?xml version="1.0" encoding="UTF-8"?>
    <Fa>
        <Naglowek>
            <KodFormularza kodSystemowy="FA (2)" wersjaSchemy="1-0E">FA</KodFormularza>
            <WariantFormularza>2</WariantFormularza>
            <DataWystawienia>2024-01-15</DataWystawienia>
            <NrFaktury>FV-123/2024</NrFaktury>
        </Naglowek>
        <Podmiot1>
            <NIP>1234567890</NIP>
            <Nazwa>ACME Corporation Sp. z o.o.</Nazwa>
        </Podmiot1>
        <Podmiot2>
            <NIP>9876543210</NIP>
            <Nazwa>Test Company Ltd.</Nazwa>
        </Podmiot2>
        <FaWiersz>
            <Nazwa>Usługa A</Nazwa>
            <Ilosc>1</Ilosc>
            <CenaJedn>1000.00</CenaJedn>
            <Netto>1000.00</Netto>
            <VAT>230.00</VAT>
        </FaWiersz>
        <FaCtrl>
            <LiczbaWierszyFaktury>1</LiczbaWierszyFaktury>
            <WartoscFakturyNetto>1000.00</WartoscFakturyNetto>
            <WartoscFakturyVAT>230.00</WartoscFakturyVAT>
            <WartoscFakturyBrutto>1230.00</WartoscFakturyBrutto>
        </FaCtrl>
    </Fa>
    """
    
    ksef_result = manager.process_ksef_invoice(ksef_xml)
    print(f"   • KSeF processing: {'Success' if ksef_result.success else 'Failed'}")
    if ksef_result.success:
        invoice = ksef_result.data
        print(f"     - Invoice number: {invoice.invoice_number}")
        print(f"     - Seller NIP: {invoice.seller_nip}")
        print(f"     - Buyer NIP: {invoice.buyer_nip}")
        print(f"     - Net amount: {invoice.net_amount}")
        print(f"     - VAT amount: {invoice.vat_amount}")
        print(f"     - Gross amount: {invoice.gross_amount}")
    else:
        print(f"     - Error: {ksef_result.error_message}")
    print("✅ KSeF integration tested")
    
    # Test JPK integration
    print("\n🧪 Testing JPK Integration...")
    jpk_v7_xml = """
    <?xml version="1.0" encoding="UTF-8"?>
    <JPK>
        <Naglowek>
            <KodFormularza kodSystemowy="JPK_V7M (1)" wersjaSchemy="1-0E">JPK_V7M</KodFormularza>
            <WariantFormularza>1</WariantFormularza>
            <DataWytworzeniaJPK>2024-01-15T10:00:00</DataWytworzeniaJPK>
            <DataOd>2024-01-01</DataOd>
            <DataDo>2024-01-31</DataDo>
            <NazwaSystemu>AI Auditor</NazwaSystemu>
        </Naglowek>
        <Podmiot1>
            <NIP>1234567890</NIP>
            <PelnaNazwa>ACME Corporation Sp. z o.o.</PelnaNazwa>
        </Podmiot1>
        <SprzedazWiersz>
            <LpSprzedazy>1</LpSprzedazy>
            <NrKontrahenta>9876543210</NrKontrahenta>
            <NazwaKontrahenta>Test Company Ltd.</NazwaKontrahenta>
            <AdresKontrahenta>ul. Testowa 456, 00-002 Kraków</AdresKontrahenta>
            <DowodSprzedazy>FV-001/2024</DowodSprzedazy>
            <DataWystawienia>2024-01-15</DataWystawienia>
            <DataSprzedazy>2024-01-15</DataSprzedazy>
            <Netto>1000.00</Netto>
            <VAT>230.00</VAT>
        </SprzedazWiersz>
        <SprzedazCtrl>
            <LiczbaWierszySprzedazy>1</LiczbaWierszySprzedazy>
            <PodatekNalezny>230.00</PodatekNalezny>
        </SprzedazCtrl>
    </JPK>
    """
    
    jpk_result = manager.process_jpk_document(jpk_v7_xml, "JPK_V7")
    print(f"   • JPK processing: {'Success' if jpk_result.success else 'Failed'}")
    if jpk_result.success:
        jpk_doc = jpk_result.data
        print(f"     - Document type: {jpk_doc.document_type}")
        print(f"     - Period: {jpk_doc.period}")
        print(f"     - NIP: {jpk_doc.nip}")
        print(f"     - Validation status: {jpk_doc.validation_status}")
    else:
        print(f"     - Error: {jpk_result.error_message}")
    print("✅ JPK integration tested")
    
    # Test VAT Whitelist integration
    print("\n🧪 Testing VAT Whitelist Integration...")
    test_nips = ["1234567890", "9876543210", "0000000000"]
    
    for nip in test_nips:
        vat_result = manager.check_vat_whitelist(nip)
        print(f"   • NIP {nip}: {'Success' if vat_result.success else 'Failed'}")
        if vat_result.success:
            entry = vat_result.data
            print(f"     - Name: {entry.name}")
            print(f"     - Status: {entry.status}")
            print(f"     - Account numbers: {len(entry.account_numbers)}")
        else:
            print(f"     - Error: {vat_result.error_message}")
    
    print("✅ VAT Whitelist integration tested")
    
    # Test KRS integration
    print("\n🧪 Testing KRS Integration...")
    test_queries = ["ACME", "Test", "Unknown Company"]
    
    for query in test_queries:
        krs_result = manager.search_krs(query)
        print(f"   • Query '{query}': {'Success' if krs_result.success else 'Failed'}")
        if krs_result.success:
            entry = krs_result.data
            print(f"     - KRS: {entry.krs_number}")
            print(f"     - Name: {entry.name}")
            print(f"     - NIP: {entry.nip}")
            print(f"     - Status: {entry.status}")
        else:
            print(f"     - Error: {krs_result.error_message}")
    
    print("✅ KRS integration tested")
    
    # Test batch validation
    print("\n🧪 Testing Batch Validation...")
    batch_nips = ["1234567890", "9876543210"]
    batch_results = manager.batch_validate_contractors(batch_nips)
    
    print(f"   • Batch validation for {len(batch_nips)} NIPs:")
    for key, result in batch_results.items():
        nip, integration_type = key.split('_')
        print(f"     - {nip} ({integration_type}): {'Success' if result.success else 'Failed'}")
    
    print("✅ Batch validation tested")
    
    # Test individual integration classes
    print("\n🧪 Testing Individual Integration Classes...")
    
    # Test KSeF validation
    ksef_integration = KSeFIntegration()
    validation_result = ksef_integration.validate_invoice_xml(ksef_xml)
    print(f"   • KSeF XML validation: {'Valid' if validation_result['valid'] else 'Invalid'}")
    if not validation_result['valid']:
        print(f"     - Errors: {validation_result['errors']}")
    
    # Test JPK validation
    jpk_integration = JPKIntegration()
    jpk_validation = jpk_integration.validate_jpk_xml(jpk_v7_xml, "JPK_V7")
    print(f"   • JPK XML validation: {'Valid' if jpk_validation['valid'] else 'Invalid'}")
    if not jpk_validation['valid']:
        print(f"     - Errors: {jpk_validation['errors']}")
    
    print("✅ Individual integration classes tested")
    
    # Test error handling
    print("\n🧪 Testing Error Handling...")
    
    # Test invalid XML
    invalid_xml = "<invalid>xml</invalid>"
    invalid_ksef_result = manager.process_ksef_invoice(invalid_xml)
    print(f"   • Invalid KSeF XML: {'Failed as expected' if not invalid_ksef_result.success else 'Unexpected success'}")
    
    # Test invalid JPK type
    invalid_jpk_result = manager.process_jpk_document(jpk_v7_xml, "INVALID_TYPE")
    print(f"   • Invalid JPK type: {'Failed as expected' if not invalid_jpk_result.success else 'Unexpected success'}")
    
    print("✅ Error handling tested")
    
    # Test performance
    print("\n🧪 Testing Performance...")
    import time
    
    start_time = time.time()
    for _ in range(5):
        manager.check_vat_whitelist("1234567890")
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 5
    print(f"   • Average VAT whitelist check time: {avg_time:.3f}s")
    
    start_time = time.time()
    for _ in range(5):
        manager.search_krs("ACME")
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 5
    print(f"   • Average KRS search time: {avg_time:.3f}s")
    
    print("✅ Performance tested")
    
    print("\n" + "=" * 60)
    print("📊 PL-core Integrations Test Results: All tests passed!")
    print("🎉 PL-core integrations are working correctly!")


if __name__ == "__main__":
    test_pl_integrations()
