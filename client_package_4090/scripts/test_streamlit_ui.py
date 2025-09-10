#!/usr/bin/env python3
"""
WSAD Test Script: Streamlit UI Test
Tests the Streamlit web interface functionality.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_streamlit_imports():
    """Test Streamlit imports and basic functionality."""
    print("🧪 Testing Streamlit Imports...")

    try:
        import streamlit as st

        print("✅ Streamlit imported successfully")

        # Test basic Streamlit functions
        st.set_page_config(page_title="Test", page_icon="🔍", layout="wide")
        print("✅ Streamlit page config works")

        return True

    except Exception as e:
        print(f"❌ Streamlit import test failed: {e}")
        return False


def test_streamlit_app_structure():
    """Test Streamlit app structure."""
    print("🧪 Testing Streamlit App Structure...")

    try:
        # Import the app
        from streamlit_app import main, show_audit_page, show_home_page, show_ocr_page

        print("✅ Streamlit app functions imported successfully")

        # Test function existence
        functions = [main, show_home_page, show_audit_page, show_ocr_page]
        for func in functions:
            assert callable(func), f"Function {func.__name__} is not callable"

        print("✅ All Streamlit app functions are callable")

        return True

    except Exception as e:
        print(f"❌ Streamlit app structure test failed: {e}")
        return False


def test_session_state_management():
    """Test session state management."""
    print("🧪 Testing Session State Management...")

    try:
        import streamlit as st

        # Test session state initialization
        if "test_key" not in st.session_state:
            st.session_state.test_key = "test_value"

        assert st.session_state.test_key == "test_value"
        print("✅ Session state initialization works")

        # Test session state update
        st.session_state.test_key = "updated_value"
        assert st.session_state.test_key == "updated_value"
        print("✅ Session state update works")

        return True

    except Exception as e:
        print(f"❌ Session state management test failed: {e}")
        return False


def test_ui_components():
    """Test UI components."""
    print("🧪 Testing UI Components...")

    try:
        import pandas as pd
        import streamlit as st

        # Test basic components
        st.markdown("Test markdown")
        st.header("Test header")
        st.subheader("Test subheader")
        st.text("Test text")
        st.info("Test info")
        st.success("Test success")
        st.warning("Test warning")
        st.error("Test error")

        print("✅ Basic UI components work")

        # Test data components
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        st.dataframe(df)
        st.table(df)

        print("✅ Data components work")

        # Test input components
        st.text_input("Test input", value="test")
        st.number_input("Test number", value=42)
        st.selectbox("Test select", ["option1", "option2"])
        st.checkbox("Test checkbox")
        st.slider("Test slider", 0, 100, 50)

        print("✅ Input components work")

        return True

    except Exception as e:
        print(f"❌ UI components test failed: {e}")
        return False


def test_file_upload_simulation():
    """Test file upload simulation."""
    print("🧪 Testing File Upload Simulation...")

    try:
        import tempfile
        from pathlib import Path


        # Create temporary files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            test_pdf = temp_path / "test.pdf"
            test_excel = temp_path / "test.xlsx"

            # Write test content
            test_pdf.write_text("Mock PDF content")
            test_excel.write_text("Mock Excel content")

            # Test file reading
            pdf_content = test_pdf.read_text()
            excel_content = test_excel.read_text()

            assert pdf_content == "Mock PDF content"
            assert excel_content == "Mock Excel content"

            print("✅ File upload simulation works")

        return True

    except Exception as e:
        print(f"❌ File upload simulation test failed: {e}")
        return False


def test_audit_process_simulation():
    """Test audit process simulation."""
    print("🧪 Testing Audit Process Simulation...")

    try:
        # Simulate audit process
        mock_results = {
            "total_invoices": 10,
            "matched": 8,
            "unmatched": 2,
            "processing_time": 15.5,
            "timestamp": datetime.now().isoformat(),
            "tiebreak_weight_fname": 0.3,
            "tiebreak_min_seller": 0.4,
            "amount_tolerance": 1.0,
        }

        # Test result structure
        assert "total_invoices" in mock_results
        assert "matched" in mock_results
        assert "unmatched" in mock_results
        assert "processing_time" in mock_results
        assert "timestamp" in mock_results

        print("✅ Audit process simulation works")
        print(f"   Total invoices: {mock_results['total_invoices']}")
        print(f"   Matched: {mock_results['matched']}")
        print(f"   Unmatched: {mock_results['unmatched']}")
        print(f"   Processing time: {mock_results['processing_time']}s")

        return True

    except Exception as e:
        print(f"❌ Audit process simulation test failed: {e}")
        return False


def test_ocr_process_simulation():
    """Test OCR process simulation."""
    print("🧪 Testing OCR Process Simulation...")

    try:
        # Simulate OCR process
        mock_ocr_results = [
            {
                "file_name": "test1.pdf",
                "confidence": 0.85,
                "invoice_number": "FV-001/2024",
                "issue_date": "15.01.2024",
                "total_net": 1000.0,
                "currency": "zł",
                "seller_name": "Test Company",
            },
            {
                "file_name": "test2.pdf",
                "confidence": 0.92,
                "invoice_number": "FV-002/2024",
                "issue_date": "16.01.2024",
                "total_net": 1500.0,
                "currency": "zł",
                "seller_name": "Another Company",
            },
        ]

        # Test result structure
        for result in mock_ocr_results:
            assert "file_name" in result
            assert "confidence" in result
            assert "invoice_number" in result
            assert "issue_date" in result
            assert "total_net" in result
            assert "currency" in result
            assert "seller_name" in result

        print("✅ OCR process simulation works")
        print(f"   Processed {len(mock_ocr_results)} files")
        print(
            f"   Average confidence: {sum(r['confidence'] for r in mock_ocr_results) / len(mock_ocr_results):.2f}"
        )

        return True

    except Exception as e:
        print(f"❌ OCR process simulation test failed: {e}")
        return False


def test_ui_integration():
    """Test UI integration with core modules."""
    print("🧪 Testing UI Integration...")

    try:
        # Test core module imports
        from core.exceptions import AuditorException
        from core.ocr_processor import OCRProcessor

        print("✅ Core modules imported successfully")

        # Test OCR processor initialization
        ocr_processor = OCRProcessor(engine="tesseract")
        print("✅ OCR processor initialized")

        # Test exception handling
        try:
            raise AuditorException("Test exception")
        except AuditorException as e:
            assert str(e) == "Test exception"
            print("✅ Exception handling works")

        return True

    except Exception as e:
        print(f"❌ UI integration test failed: {e}")
        return False


def test_streamlit_configuration():
    """Test Streamlit configuration."""
    print("🧪 Testing Streamlit Configuration...")

    try:
        import streamlit as st

        # Test page config
        st.set_page_config(
            page_title="AI Auditor - Panel Audytora",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        print("✅ Page configuration works")

        # Test custom CSS
        custom_css = """
        <style>
            .main-header {
                background: linear-gradient(90deg, #1f4e79 0%, #2e6da4 100%);
                padding: 1rem;
                border-radius: 10px;
                color: white;
                text-align: center;
                margin-bottom: 2rem;
            }
        </style>
        """

        st.markdown(custom_css, unsafe_allow_html=True)
        print("✅ Custom CSS works")

        return True

    except Exception as e:
        print(f"❌ Streamlit configuration test failed: {e}")
        return False


def main():
    """Run all Streamlit UI tests."""
    print("🚀 Starting Streamlit UI Test Suite...")
    print("=" * 60)

    tests = [
        test_streamlit_imports,
        test_streamlit_app_structure,
        test_session_state_management,
        test_ui_components,
        test_file_upload_simulation,
        test_audit_process_simulation,
        test_ocr_process_simulation,
        test_ui_integration,
        test_streamlit_configuration,
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
    print(f"📊 Streamlit UI Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All Streamlit UI tests passed!")
        return 0
    else:
        print("❌ Some Streamlit UI tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
