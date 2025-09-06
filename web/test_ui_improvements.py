#!/usr/bin/env python3
"""
Test script for UI improvements - language switching and dark mode.
"""

import sys
import os
from pathlib import Path

# Add the web directory to Python path
web_dir = Path(__file__).parent
sys.path.insert(0, str(web_dir))

def test_translations():
    """Test the translations system."""
    print("🧪 Testing translations system...")
    
    try:
        from translations import t, get_language_switcher, translations
        
        # Test Polish translations
        translations.set_language('pl')
        assert t('app_title') == 'AI Auditor - Panel Audytora'
        assert t('dark_mode') == 'Ciemny'
        assert t('language') == 'Język'
        print("✅ Polish translations working")
        
        # Test English translations
        translations.set_language('en')
        assert t('app_title') == 'AI Auditor - Auditor Panel'
        assert t('dark_mode') == 'Dark'
        assert t('language') == 'Language'
        print("✅ English translations working")
        
        # Test available languages
        langs = translations.get_available_languages()
        assert 'pl' in langs
        assert 'en' in langs
        print("✅ Available languages working")
        
        return True
        
    except Exception as e:
        print(f"❌ Translations test failed: {e}")
        return False

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing module imports...")
    
    try:
        # Test auditor_frontend import
        import auditor_frontend
        print("✅ auditor_frontend imported successfully")
        
        # Test modern_ui import
        import modern_ui
        print("✅ modern_ui imported successfully")
        
        # Test translations import
        import translations
        print("✅ translations imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_html_file():
    """Test that HTML file exists and has required elements."""
    print("🧪 Testing HTML file...")
    
    try:
        html_file = web_dir / "index.html"
        if not html_file.exists():
            print("❌ index.html not found")
            return False
        
        content = html_file.read_text(encoding='utf-8')
        
        # Check for required elements
        required_elements = [
            'theme-toggle',
            'lang-toggle',
            'translations',
            'toggleTheme',
            'toggleLanguage',
            'data-theme="dark"'
        ]
        
        for element in required_elements:
            if element not in content:
                print(f"❌ Missing element: {element}")
                return False
        
        print("✅ HTML file has all required elements")
        return True
        
    except Exception as e:
        print(f"❌ HTML test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting UI improvements tests...\n")
    
    tests = [
        test_imports,
        test_translations,
        test_html_file
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! UI improvements are working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
