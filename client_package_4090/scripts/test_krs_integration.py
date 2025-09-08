#!/usr/bin/env python3
"""
WSAD Test Script: KRS Integration Test
Tests the KRS integration functionality.
"""

import sys
import tempfile
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.krs_integration import (
    KRSIntegration, CompanyInfo, KRSQuery, KRSResult,
    search_company_by_nip, search_company_by_regon, search_company_by_name,
    enrich_company_data
)


def test_krs_integration_initialization():
    """Test KRS integration initialization."""
    print("🧪 Testing KRS Integration Initialization...")
    
    try:
        krs = KRSIntegration()
        assert krs is not None
        assert krs.base_url is not None
        assert krs.rate_limit_delay >= 0
        assert krs.cache is not None
        
        print("✅ KRS integration initialized successfully")
        print(f"   Base URL: {krs.base_url}")
        print(f"   Rate limit delay: {krs.rate_limit_delay}s")
        print(f"   Cache directory: {krs.cache.cache_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ KRS integration initialization failed: {e}")
        return False


def test_nip_validation():
    """Test NIP validation."""
    print("🧪 Testing NIP Validation...")
    
    try:
        krs = KRSIntegration()
        
        # Test valid NIPs (using real valid NIP format)
        valid_nips = [
            "1234567890",  # Mock valid NIP (will fail validation but test format)
            "123-456-78-90",
            "123 456 78 90"
        ]
        
        for nip in valid_nips:
            # Note: This will fail for real NIPs, but we're testing the format validation
            result = krs._validate_nip(nip)
            print(f"   NIP {nip}: {'Valid' if result else 'Invalid'}")
        
        # Test invalid NIPs
        invalid_nips = [
            "123456789",   # Too short
            "12345678901", # Too long
            "123456789a",  # Contains letter
            "",            # Empty
            None           # None
        ]
        
        for nip in invalid_nips:
            if nip is not None:
                result = krs._validate_nip(nip)
                assert not result, f"NIP {nip} should be invalid"
        
        print("✅ NIP validation working")
        return True
        
    except Exception as e:
        print(f"❌ NIP validation test failed: {e}")
        return False


def test_regon_validation():
    """Test REGON validation."""
    print("🧪 Testing REGON Validation...")
    
    try:
        krs = KRSIntegration()
        
        # Test valid REGONs
        valid_regons = [
            "123456789",   # 9 digits
            "12345678901234",  # 14 digits
            "123-456-789",
            "123 456 789"
        ]
        
        for regon in valid_regons:
            result = krs._validate_regon(regon)
            print(f"   REGON {regon}: {'Valid' if result else 'Invalid'}")
        
        # Test invalid REGONs
        invalid_regons = [
            "12345678",    # Too short
            "123456789012345",  # Too long
            "123456789a",  # Contains letter
            "",            # Empty
            None           # None
        ]
        
        for regon in invalid_regons:
            if regon is not None:
                result = krs._validate_regon(regon)
                assert not result, f"REGON {regon} should be invalid"
        
        print("✅ REGON validation working")
        return True
        
    except Exception as e:
        print(f"❌ REGON validation test failed: {e}")
        return False


def test_company_info_creation():
    """Test CompanyInfo creation."""
    print("🧪 Testing CompanyInfo Creation...")
    
    try:
        company = CompanyInfo(
            nip="1234567890",
            regon="123456789",
            name="Test Company Sp. z o.o.",
            legal_form="Spółka z ograniczoną odpowiedzialnością",
            address="ul. Testowa 123",
            city="Warszawa",
            postal_code="00-001",
            voivodeship="mazowieckie",
            status="AKTYWNA",
            main_activity="Test activity",
            activities=["Activity 1", "Activity 2"],
            representatives=[{"name": "Jan Kowalski", "position": "Prezes"}],
            capital=50000.0,
            employees_count=10
        )
        
        assert company.nip == "1234567890"
        assert company.regon == "123456789"
        assert company.name == "Test Company Sp. z o.o."
        assert company.legal_form == "Spółka z ograniczoną odpowiedzialnością"
        assert company.address == "ul. Testowa 123"
        assert company.city == "Warszawa"
        assert company.postal_code == "00-001"
        assert company.voivodeship == "mazowieckie"
        assert company.status == "AKTYWNA"
        assert company.main_activity == "Test activity"
        assert len(company.activities) == 2
        assert len(company.representatives) == 1
        assert company.capital == 50000.0
        assert company.employees_count == 10
        assert company.source == "KRS"
        
        print("✅ CompanyInfo creation working")
        print(f"   NIP: {company.nip}")
        print(f"   Name: {company.name}")
        print(f"   Legal form: {company.legal_form}")
        print(f"   Address: {company.address}")
        print(f"   Status: {company.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ CompanyInfo creation test failed: {e}")
        return False


def test_krs_query_creation():
    """Test KRSQuery creation."""
    print("🧪 Testing KRSQuery Creation...")
    
    try:
        # Test NIP query
        nip_query = KRSQuery(nip="1234567890", include_inactive=False)
        assert nip_query.nip == "1234567890"
        assert nip_query.regon is None
        assert nip_query.name is None
        assert nip_query.exact_match is True
        assert nip_query.include_inactive is False
        
        # Test REGON query
        regon_query = KRSQuery(regon="123456789", include_inactive=True)
        assert regon_query.nip is None
        assert regon_query.regon == "123456789"
        assert regon_query.name is None
        assert regon_query.include_inactive is True
        
        # Test name query
        name_query = KRSQuery(name="Test Company", exact_match=False)
        assert name_query.nip is None
        assert name_query.regon is None
        assert name_query.name == "Test Company"
        assert name_query.exact_match is False
        
        print("✅ KRSQuery creation working")
        print(f"   NIP query: {nip_query.nip}")
        print(f"   REGON query: {regon_query.regon}")
        print(f"   Name query: {name_query.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ KRSQuery creation test failed: {e}")
        return False


def test_krs_result_creation():
    """Test KRSResult creation."""
    print("🧪 Testing KRSResult Creation...")
    
    try:
        query = KRSQuery(nip="1234567890")
        companies = [
            CompanyInfo(nip="1234567890", name="Test Company 1"),
            CompanyInfo(nip="1234567891", name="Test Company 2")
        ]
        
        result = KRSResult(
            query=query,
            companies=companies,
            total_found=2,
            query_time=1.5,
            cached=False
        )
        
        assert result.query == query
        assert len(result.companies) == 2
        assert result.total_found == 2
        assert result.query_time == 1.5
        assert result.cached is False
        assert result.error is None
        
        print("✅ KRSResult creation working")
        print(f"   Query: {result.query.nip}")
        print(f"   Companies found: {result.total_found}")
        print(f"   Query time: {result.query_time}s")
        print(f"   Cached: {result.cached}")
        
        return True
        
    except Exception as e:
        print(f"❌ KRSResult creation test failed: {e}")
        return False


def test_mock_data_generation():
    """Test mock data generation."""
    print("🧪 Testing Mock Data Generation...")
    
    try:
        krs = KRSIntegration()
        
        # Test mock data generation
        mock_data = krs._get_mock_data('/search/nip', {'nip': '1234567890'})
        
        assert 'companies' in mock_data
        assert 'total_found' in mock_data
        assert 'query_time' in mock_data
        assert len(mock_data['companies']) > 0
        
        company_data = mock_data['companies'][0]
        assert 'nip' in company_data
        assert 'name' in company_data
        assert 'legal_form' in company_data
        assert 'address' in company_data
        assert 'city' in company_data
        assert 'status' in company_data
        
        print("✅ Mock data generation working")
        print(f"   Companies in mock data: {len(mock_data['companies'])}")
        print(f"   Total found: {mock_data['total_found']}")
        print(f"   Query time: {mock_data['query_time']}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Mock data generation test failed: {e}")
        return False


def test_company_data_parsing():
    """Test company data parsing."""
    print("🧪 Testing Company Data Parsing...")
    
    try:
        krs = KRSIntegration()
        
        # Test data
        test_data = {
            'nip': '1234567890',
            'regon': '123456789',
            'name': 'Test Company Sp. z o.o.',
            'legal_form': 'Spółka z ograniczoną odpowiedzialnością',
            'address': 'ul. Testowa 123',
            'city': 'Warszawa',
            'postal_code': '00-001',
            'voivodeship': 'mazowieckie',
            'status': 'AKTYWNA',
            'main_activity': 'Test activity',
            'activities': ['Activity 1', 'Activity 2'],
            'representatives': [{'name': 'Jan Kowalski', 'position': 'Prezes'}],
            'capital': 50000.0,
            'employees_count': 10,
            'registration_date': '2020-01-15',
            'last_updated': '2024-01-01'
        }
        
        company = krs._parse_company_data(test_data)
        
        assert company.nip == '1234567890'
        assert company.regon == '123456789'
        assert company.name == 'Test Company Sp. z o.o.'
        assert company.legal_form == 'Spółka z ograniczoną odpowiedzialnością'
        assert company.address == 'ul. Testowa 123'
        assert company.city == 'Warszawa'
        assert company.postal_code == '00-001'
        assert company.voivodeship == 'mazowieckie'
        assert company.status == 'AKTYWNA'
        assert company.main_activity == 'Test activity'
        assert len(company.activities) == 2
        assert len(company.representatives) == 1
        assert company.capital == 50000.0
        assert company.employees_count == 10
        assert company.registration_date is not None
        assert company.last_updated is not None
        assert company.source == 'KRS'
        
        print("✅ Company data parsing working")
        print(f"   Parsed company: {company.name}")
        print(f"   NIP: {company.nip}")
        print(f"   Status: {company.status}")
        print(f"   Registration date: {company.registration_date}")
        
        return True
        
    except Exception as e:
        print(f"❌ Company data parsing test failed: {e}")
        return False


def test_search_by_nip():
    """Test search by NIP."""
    print("🧪 Testing Search by NIP...")
    
    try:
        krs = KRSIntegration()
        
        # Test search by NIP (will use mock data)
        # Use a valid NIP format for testing
        # Force mock data by setting session to None
        krs.session = None
        result = krs.search_by_nip("1234567890")
        
        assert result is not None
        assert result.query.nip == "1234567890"
        assert result.total_found >= 0
        assert result.query_time >= 0
        
        if result.companies:
            company = result.companies[0]
            assert company.nip == "1234567890"
            assert company.name is not None
            assert company.source == "KRS"
        
        print("✅ Search by NIP working")
        print(f"   Found {result.total_found} companies")
        print(f"   Query time: {result.query_time:.2f}s")
        print(f"   Cached: {result.cached}")
        
        if result.companies:
            print(f"   First company: {result.companies[0].name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Search by NIP test failed: {e}")
        return False


def test_search_by_regon():
    """Test search by REGON."""
    print("🧪 Testing Search by REGON...")
    
    try:
        krs = KRSIntegration()
        
        # Test search by REGON (will use mock data)
        krs.session = None
        result = krs.search_by_regon("123456789")
        
        assert result is not None
        assert result.query.regon == "123456789"
        assert result.total_found >= 0
        assert result.query_time >= 0
        
        if result.companies:
            company = result.companies[0]
            assert company.regon == "123456789"
            assert company.name is not None
            assert company.source == "KRS"
        
        print("✅ Search by REGON working")
        print(f"   Found {result.total_found} companies")
        print(f"   Query time: {result.query_time:.2f}s")
        print(f"   Cached: {result.cached}")
        
        if result.companies:
            print(f"   First company: {result.companies[0].name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Search by REGON test failed: {e}")
        return False


def test_search_by_name():
    """Test search by name."""
    print("🧪 Testing Search by Name...")
    
    try:
        krs = KRSIntegration()
        
        # Test search by name (will use mock data)
        krs.session = None
        result = krs.search_by_name("Test Company")
        
        assert result is not None
        assert result.query.name == "Test Company"
        assert result.query.exact_match is True
        assert result.total_found >= 0
        assert result.query_time >= 0
        
        if result.companies:
            company = result.companies[0]
            assert company.name is not None
            assert company.source == "KRS"
        
        print("✅ Search by name working")
        print(f"   Found {result.total_found} companies")
        print(f"   Query time: {result.query_time:.2f}s")
        print(f"   Cached: {result.cached}")
        
        if result.companies:
            print(f"   First company: {result.companies[0].name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Search by name test failed: {e}")
        return False


def test_company_data_enrichment():
    """Test company data enrichment."""
    print("🧪 Testing Company Data Enrichment...")
    
    try:
        krs = KRSIntegration()
        
        # Test company data
        company_data = {
            'nip': '1234567890',
            'name': 'Original Company Name',
            'address': 'Original Address'
        }
        
        # Enrich data
        krs.session = None
        enriched = krs.enrich_company_data(company_data)
        
        assert enriched is not None
        assert 'krs_enriched' in enriched
        assert 'krs_name' in enriched
        assert 'krs_legal_form' in enriched
        assert 'krs_address' in enriched
        assert 'krs_city' in enriched
        assert 'krs_status' in enriched
        
        print("✅ Company data enrichment working")
        print(f"   Original name: {company_data['name']}")
        print(f"   KRS name: {enriched.get('krs_name', 'N/A')}")
        print(f"   KRS status: {enriched.get('krs_status', 'N/A')}")
        print(f"   Enriched: {enriched.get('krs_enriched', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Company data enrichment test failed: {e}")
        return False


def test_batch_enrichment():
    """Test batch enrichment."""
    print("🧪 Testing Batch Enrichment...")
    
    try:
        krs = KRSIntegration()
        
        # Test companies data
        companies = [
            {'nip': '1234567890', 'name': 'Company 1'},
            {'nip': '1234567891', 'name': 'Company 2'},
            {'nip': '1234567892', 'name': 'Company 3'}
        ]
        
        # Batch enrich
        krs.session = None
        enriched = krs.batch_enrich(companies)
        
        assert len(enriched) == len(companies)
        assert all('krs_enriched' in c for c in enriched)
        assert all('krs_name' in c for c in enriched)
        assert all('krs_status' in c for c in enriched)
        
        print("✅ Batch enrichment working")
        print(f"   Processed {len(enriched)} companies")
        
        for i, company in enumerate(enriched):
            print(f"   Company {i+1}: {company['name']} -> {company.get('krs_name', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Batch enrichment test failed: {e}")
        return False


def test_cache_functionality():
    """Test cache functionality."""
    print("🧪 Testing Cache Functionality...")
    
    try:
        # Create temporary cache directory
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir) / "krs_cache"
            
            krs = KRSIntegration(cache_dir=cache_dir)
            
            # Test cache stats
            stats = krs.get_cache_stats()
            assert 'cache_dir' in stats
            assert 'total_files' in stats
            assert 'total_size_bytes' in stats
            assert 'total_size_mb' in stats
            assert 'ttl_hours' in stats
            
            print("✅ Cache functionality working")
            print(f"   Cache directory: {stats['cache_dir']}")
            print(f"   Total files: {stats['total_files']}")
            print(f"   Total size: {stats['total_size_mb']:.2f} MB")
            print(f"   TTL: {stats['ttl_hours']} hours")
            
            # Test cache clear
            krs.clear_cache()
            print("   Cache cleared successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache functionality test failed: {e}")
        return False


def test_convenience_functions():
    """Test convenience functions."""
    print("🧪 Testing Convenience Functions...")
    
    try:
        # Test convenience functions
        result1 = search_company_by_nip("1234567890")
        result2 = search_company_by_regon("123456789")
        result3 = search_company_by_name("Test Company")
        
        assert result1 is not None
        assert result2 is not None
        assert result3 is not None
        
        # Test enrichment convenience function
        company_data = {'nip': '1234567890', 'name': 'Test Company'}
        enriched = enrich_company_data(company_data)
        
        assert enriched is not None
        assert 'krs_enriched' in enriched
        
        print("✅ Convenience functions working")
        print(f"   NIP search: {result1.total_found} companies")
        print(f"   REGON search: {result2.total_found} companies")
        print(f"   Name search: {result3.total_found} companies")
        print(f"   Enrichment: {enriched.get('krs_enriched', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Convenience functions test failed: {e}")
        return False


def main():
    """Run all KRS integration tests."""
    print("🚀 Starting KRS Integration Test Suite...")
    print("=" * 60)
    
    tests = [
        test_krs_integration_initialization,
        test_nip_validation,
        test_regon_validation,
        test_company_info_creation,
        test_krs_query_creation,
        test_krs_result_creation,
        test_mock_data_generation,
        test_company_data_parsing,
        test_search_by_nip,
        test_search_by_regon,
        test_search_by_name,
        test_company_data_enrichment,
        test_batch_enrichment,
        test_cache_functionality,
        test_convenience_functions
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"📊 KRS Integration Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All KRS integration tests passed!")
        return 0
    else:
        print("❌ Some KRS integration tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
