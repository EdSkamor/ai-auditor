#!/usr/bin/env python3
"""
Test script dla web scrapingu stron rządowych.
"""

import sys
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.government_scraper import (
    WebScrapingManager, GovernmentScraper, SourceType, DataType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_government_scraper():
    """Test scrapera rządowego."""
    print("🧪 Testing Government Scraper...")
    
    scraper = GovernmentScraper()
    
    # Test company info scraping
    company_info = scraper.scrape_company_info("1234567890")
    assert company_info is not None
    assert company_info.nip == "1234567890"
    assert company_info.name is not None
    print("✅ Company info scraping works")
    
    # Test VAT whitelist scraping
    vat_data = scraper.scrape_vat_whitelist("1234567890")
    assert vat_data is not None
    assert 'nip' in vat_data
    assert 'status' in vat_data
    print("✅ VAT whitelist scraping works")
    
    # Test sanctions list scraping
    sanctions = scraper.scrape_sanctions_list("Test Company")
    assert isinstance(sanctions, list)
    print("✅ Sanctions list scraping works")
    
    # Test PEP list scraping
    pep_entities = scraper.scrape_pep_list("Politician Company")
    assert isinstance(pep_entities, list)
    print("✅ PEP list scraping works")
    
    # Test financial data scraping
    financial_data = scraper.scrape_financial_data("1234567890")
    assert financial_data is not None
    assert 'nip' in financial_data
    assert 'revenue' in financial_data
    print("✅ Financial data scraping works")
    
    # Test news scraping
    news = scraper.scrape_news("News Company")
    assert isinstance(news, list)
    print("✅ News scraping works")
    
    print("✅ All government scraper tests passed!")


def test_web_scraping_manager():
    """Test menedżera web scrapingu."""
    print("\n🧪 Testing Web Scraping Manager...")
    
    # Use temporary directory for testing
    test_dir = Path("/tmp/test_scraping")
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    manager = WebScrapingManager(test_dir)
    
    # Test comprehensive data scraping
    comprehensive_data = manager.get_company_comprehensive_data("1234567890")
    assert comprehensive_data is not None
    assert 'nip' in comprehensive_data
    assert 'company_info' in comprehensive_data
    assert 'vat_data' in comprehensive_data
    assert 'financial_data' in comprehensive_data
    assert 'sanctions' in comprehensive_data
    assert 'pep' in comprehensive_data
    assert 'news' in comprehensive_data
    assert 'risk_indicators' in comprehensive_data
    print("✅ Comprehensive data scraping works")
    
    # Test risk assessment
    risk_assessment = manager.get_risk_assessment("1234567890")
    assert risk_assessment is not None
    assert 'nip' in risk_assessment
    assert 'risk_score' in risk_assessment
    assert 'risk_level' in risk_assessment
    assert 'risk_factors' in risk_assessment
    assert 'data_sources' in risk_assessment
    print("✅ Risk assessment works")
    
    # Test batch scraping
    nip_list = ["1234567890", "0987654321", "1122334455"]
    batch_results = manager.batch_scrape_companies(nip_list)
    assert len(batch_results) == 3
    for nip in nip_list:
        assert nip in batch_results
    print("✅ Batch scraping works")
    
    # Test scraping summary
    summary = manager.get_scraping_summary()
    assert 'total_cached_entries' in summary
    assert 'recent_scrapes' in summary
    assert 'cache_file_size' in summary
    print("✅ Scraping summary works")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
    print("✅ All web scraping manager tests passed!")


def test_risk_analysis():
    """Test analizy ryzyk."""
    print("\n🧪 Testing Risk Analysis...")
    
    scraper = GovernmentScraper()
    
    # Test with inactive company
    inactive_company_data = {
        'status': 'inactive',
        'vat_status': 'active',
        'sanctions': [],
        'pep': []
    }
    
    risk_indicators = scraper.analyze_risk_indicators(inactive_company_data)
    assert len(risk_indicators) > 0
    assert any(ri.type == 'company_status' for ri in risk_indicators)
    print("✅ Inactive company risk analysis works")
    
    # Test with sanctions
    sanctions_company_data = {
        'status': 'active',
        'vat_status': 'active',
        'sanctions': [{'name': 'Test Company', 'type': 'sanctions'}],
        'pep': []
    }
    
    risk_indicators = scraper.analyze_risk_indicators(sanctions_company_data)
    assert len(risk_indicators) > 0
    assert any(ri.type == 'sanctions' for ri in risk_indicators)
    print("✅ Sanctions risk analysis works")
    
    # Test with PEP
    pep_company_data = {
        'status': 'active',
        'vat_status': 'active',
        'sanctions': [],
        'pep': [{'name': 'Politician Company', 'type': 'pep'}]
    }
    
    risk_indicators = scraper.analyze_risk_indicators(pep_company_data)
    assert len(risk_indicators) > 0
    assert any(ri.type == 'pep' for ri in risk_indicators)
    print("✅ PEP risk analysis works")
    
    print("✅ All risk analysis tests passed!")


def test_data_types():
    """Test typów danych."""
    print("\n🧪 Testing Data Types...")
    
    # Test source types
    source_types = [SourceType.GOVERNMENT, SourceType.COMPANY, SourceType.REGULATORY, 
                   SourceType.FINANCIAL, SourceType.LEGAL]
    
    for source_type in source_types:
        assert source_type.value in ['government', 'company', 'regulatory', 'financial', 'legal']
        print(f"✅ Source type {source_type.value} works")
    
    # Test data types
    data_types = [DataType.COMPANY_INFO, DataType.FINANCIAL_DATA, DataType.LEGAL_STATUS,
                 DataType.REGULATORY_INFO, DataType.RISK_INDICATORS, DataType.NEWS, DataType.SANCTIONS]
    
    for data_type in data_types:
        assert data_type.value in ['company_info', 'financial_data', 'legal_status', 
                                  'regulatory_info', 'risk_indicators', 'news', 'sanctions']
        print(f"✅ Data type {data_type.value} works")
    
    print("✅ All data type tests passed!")


def test_workflow():
    """Test przepływu pracy scrapingu."""
    print("\n🧪 Testing Scraping Workflow...")
    
    # Use temporary directory for testing
    test_dir = Path("/tmp/test_workflow_scraping")
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    manager = WebScrapingManager(test_dir)
    
    # 1. Scrape single company
    nip = "1234567890"
    data = manager.get_company_comprehensive_data(nip)
    assert data['nip'] == nip
    print("✅ Step 1: Single company scraping works")
    
    # 2. Risk assessment
    risk = manager.get_risk_assessment(nip)
    assert risk['nip'] == nip
    assert risk['risk_score'] >= 0
    assert risk['risk_level'] in ['low', 'medium', 'high', 'critical']
    print("✅ Step 2: Risk assessment works")
    
    # 3. Batch scraping
    nip_list = ["1111111111", "2222222222", "3333333333"]
    batch_data = manager.batch_scrape_companies(nip_list)
    assert len(batch_data) == 3
    print("✅ Step 3: Batch scraping works")
    
    # 4. Cache verification
    summary = manager.get_scraping_summary()
    assert summary['total_cached_entries'] >= 4  # 1 + 3 from batch
    print("✅ Step 4: Cache verification works")
    
    # 5. Data integrity
    for nip in [nip] + nip_list:
        cached_data = manager.get_company_comprehensive_data(nip)
        assert cached_data['nip'] == nip
        assert 'scraped_at' in cached_data
    print("✅ Step 5: Data integrity works")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
    print("✅ Complete scraping workflow test passed!")


def main():
    """Main test function."""
    print("🚀 Starting Government Scraper Tests...")
    
    try:
        test_government_scraper()
        test_web_scraping_manager()
        test_risk_analysis()
        test_data_types()
        test_workflow()
        
        print("\n🎉 All Government Scraper tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
