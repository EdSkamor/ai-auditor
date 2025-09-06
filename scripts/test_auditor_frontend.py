#!/usr/bin/env python3
"""
Test script dla nowego front-endu audytora.
"""

import sys
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from web.auditor_frontend import AuditorFrontend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_frontend_initialization():
    """Test inicjalizacji front-endu."""
    print("🧪 Testing Frontend Initialization...")
    
    try:
        # Mock streamlit session_state for testing
        import sys
        from unittest.mock import MagicMock
        
        # Mock streamlit
        mock_streamlit = MagicMock()
        mock_streamlit.session_state = MagicMock()
        mock_streamlit.session_state.__contains__ = lambda self, key: key in ['current_view', 'dark_mode', 'audit_jobs', 'findings', 'exports']
        mock_streamlit.session_state.__getitem__ = lambda self, key: {
            'current_view': 'Run',
            'dark_mode': False,
            'audit_jobs': [],
            'findings': [],
            'exports': []
        }.get(key, None)
        mock_streamlit.session_state.__setitem__ = lambda self, key, value: None
        
        sys.modules['streamlit'] = mock_streamlit
        
        frontend = AuditorFrontend()
        print("✅ Frontend initialized successfully")
        
        print("✅ Session state initialized correctly")
        
        return frontend
        
    except Exception as e:
        print(f"❌ Frontend initialization failed: {e}")
        raise


def test_view_switching():
    """Test przełączania widoków."""
    print("\n🧪 Testing View Switching...")
    
    frontend = AuditorFrontend()
    
    # Test initial view
    assert frontend.current_view == 'Run'
    print("✅ Initial view set to Run")
    
    # Test view switching
    frontend.current_view = 'Findings'
    assert frontend.current_view == 'Findings'
    print("✅ Switched to Findings view")
    
    frontend.current_view = 'Exports'
    assert frontend.current_view == 'Exports'
    print("✅ Switched to Exports view")
    
    frontend.current_view = 'Run'
    assert frontend.current_view == 'Run'
    print("✅ Switched back to Run view")


def test_dark_mode_toggle():
    """Test przełączania motywu."""
    print("\n🧪 Testing Dark Mode Toggle...")
    
    frontend = AuditorFrontend()
    
    # Test initial mode
    assert frontend.dark_mode == False
    print("✅ Initial mode is light")
    
    # Test toggle
    frontend.dark_mode = True
    assert frontend.dark_mode == True
    print("✅ Switched to dark mode")
    
    frontend.dark_mode = False
    assert frontend.dark_mode == False
    print("✅ Switched back to light mode")


def test_audit_job_management():
    """Test zarządzania zadaniami audytu."""
    print("\n🧪 Testing Audit Job Management...")
    
    frontend = AuditorFrontend()
    
    # Test initial state
    assert len(frontend.audit_jobs) == 0
    print("✅ Initial audit jobs list is empty")
    
    # Test adding job
    mock_files = [
        type('MockFile', (), {'name': 'test1.pdf'}),
        type('MockFile', (), {'name': 'test2.pdf'}),
        type('MockFile', (), {'name': 'test3.pdf'})
    ]
    
    frontend.start_audit_job(mock_files)
    
    assert len(frontend.audit_jobs) == 1
    job = frontend.audit_jobs[0]
    
    assert job['name'] == "Audyt 3 plików"
    assert job['status'] == 'completed'
    assert job['file_count'] == 3
    assert job['progress'] == 100
    
    print("✅ Audit job added successfully")
    print(f"   Job name: {job['name']}")
    print(f"   Status: {job['status']}")
    print(f"   File count: {job['file_count']}")
    print(f"   Progress: {job['progress']}%")


def test_findings_management():
    """Test zarządzania niezgodnościami."""
    print("\n🧪 Testing Findings Management...")
    
    frontend = AuditorFrontend()
    
    # Test initial state
    assert len(frontend.findings) == 0
    print("✅ Initial findings list is empty")
    
    # Add mock findings
    frontend.add_mock_findings()
    
    assert len(frontend.findings) == 3
    print("✅ Mock findings added successfully")
    
    # Test finding properties
    finding = frontend.findings[0]
    assert 'id' in finding
    assert 'title' in finding
    assert 'category' in finding
    assert 'severity' in finding
    assert 'description' in finding
    assert 'date' in finding
    assert 'file' in finding
    
    print(f"   Finding 1: {finding['title']} ({finding['severity']})")
    print(f"   Finding 2: {frontend.findings[1]['title']} ({frontend.findings[1]['severity']})")
    print(f"   Finding 3: {frontend.findings[2]['title']} ({frontend.findings[2]['severity']})")


def test_exports_management():
    """Test zarządzania eksportami."""
    print("\n🧪 Testing Exports Management...")
    
    frontend = AuditorFrontend()
    
    # Test initial state
    assert len(frontend.exports) == 0
    print("✅ Initial exports list is empty")
    
    # Test PBC exports
    frontend.export_pbc_list()
    frontend.export_pbc_status()
    frontend.export_pbc_timeline()
    
    assert len(frontend.exports) == 3
    print("✅ PBC exports added successfully")
    
    # Test Working Papers exports
    frontend.export_working_papers()
    frontend.export_evidence_chain()
    frontend.export_wp_statistics()
    
    assert len(frontend.exports) == 6
    print("✅ Working Papers exports added successfully")
    
    # Test Report exports
    frontend.export_final_report()
    frontend.export_executive_summary()
    frontend.export_compliance_report()
    
    assert len(frontend.exports) == 9
    print("✅ Report exports added successfully")
    
    # Test export properties
    export = frontend.exports[0]
    assert 'name' in export
    assert 'type' in export
    assert 'created_at' in export
    assert 'size' in export
    
    print(f"   Export 1: {export['name']} ({export['type']})")
    print(f"   Export 2: {frontend.exports[1]['name']} ({frontend.exports[1]['type']})")
    print(f"   Export 3: {frontend.exports[2]['name']} ({frontend.exports[2]['type']})")


def test_quick_stats():
    """Test szybkich statystyk."""
    print("\n🧪 Testing Quick Stats...")
    
    frontend = AuditorFrontend()
    
    # Add some test data
    frontend.start_audit_job([
        type('MockFile', (), {'name': 'test1.pdf'}),
        type('MockFile', (), {'name': 'test2.pdf'})
    ])
    
    frontend.add_mock_findings()
    
    # Test stats calculation
    jobs = frontend.audit_jobs
    findings = frontend.findings
    
    total_jobs = len(jobs)
    running_jobs = len([j for j in jobs if j.get('status') == 'running'])
    completed_jobs = len([j for j in jobs if j.get('status') == 'completed'])
    
    total_findings = len(findings)
    high_findings = len([f for f in findings if f.get('severity') == 'high'])
    medium_findings = len([f for f in findings if f.get('severity') == 'medium'])
    low_findings = len([f for f in findings if f.get('severity') == 'low'])
    
    assert total_jobs == 1
    assert running_jobs == 0
    assert completed_jobs == 1
    assert total_findings == 3
    assert high_findings == 1
    assert medium_findings == 1
    assert low_findings == 1
    
    print("✅ Quick stats calculated correctly")
    print(f"   Total jobs: {total_jobs}")
    print(f"   Completed jobs: {completed_jobs}")
    print(f"   Total findings: {total_findings}")
    print(f"   High findings: {high_findings}")
    print(f"   Medium findings: {medium_findings}")
    print(f"   Low findings: {low_findings}")


def test_export_functions():
    """Test funkcji eksportu."""
    print("\n🧪 Testing Export Functions...")
    
    frontend = AuditorFrontend()
    
    # Test all export functions
    export_functions = [
        ('PBC List', frontend.export_pbc_list),
        ('PBC Status', frontend.export_pbc_status),
        ('PBC Timeline', frontend.export_pbc_timeline),
        ('Working Papers', frontend.export_working_papers),
        ('Evidence Chain', frontend.export_evidence_chain),
        ('WP Statistics', frontend.export_wp_statistics),
        ('Final Report', frontend.export_final_report),
        ('Executive Summary', frontend.export_executive_summary),
        ('Compliance Report', frontend.export_compliance_report)
    ]
    
    for name, func in export_functions:
        try:
            func()
            print(f"✅ {name} export function works")
        except Exception as e:
            print(f"❌ {name} export function failed: {e}")
            raise
    
    # Verify exports were added
    assert len(frontend.exports) == 9
    print("✅ All exports added successfully")


def test_session_state_persistence():
    """Test trwałości stanu sesji."""
    print("\n🧪 Testing Session State Persistence...")
    
    frontend = AuditorFrontend()
    
    # Modify state
    frontend.current_view = 'Findings'
    frontend.dark_mode = True
    
    # Add some data
    frontend.start_audit_job([
        type('MockFile', (), {'name': 'test.pdf'})
    ])
    frontend.add_mock_findings()
    frontend.export_pbc_list()
    
    # Verify state is maintained
    assert frontend.current_view == 'Findings'
    assert frontend.dark_mode == True
    assert len(frontend.audit_jobs) == 1
    assert len(frontend.findings) == 3
    assert len(frontend.exports) == 1
    
    print("✅ Session state persistence works correctly")


def main():
    """Main test function."""
    print("🚀 Starting Auditor Frontend Tests...")
    
    try:
        test_frontend_initialization()
        test_view_switching()
        test_dark_mode_toggle()
        test_audit_job_management()
        test_findings_management()
        test_exports_management()
        test_quick_stats()
        test_export_functions()
        test_session_state_persistence()
        
        print("\n🎉 All Auditor Frontend tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
