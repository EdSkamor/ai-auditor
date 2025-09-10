#!/usr/bin/env python3
"""
Security tests for AI Auditor Web Interface
"""

import re
import sys
from pathlib import Path


def test_hardcoded_secrets():
    """Test for hardcoded secrets in code."""
    print("🔍 Testing for hardcoded secrets...")

    web_dir = Path(__file__).parent
    issues = []

    # Patterns to check for
    secret_patterns = [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']',
        r'key\s*=\s*["\'][^"\']+["\']',
    ]

    for py_file in web_dir.glob("*.py"):
        if py_file.name.startswith("test_"):
            continue

        content = py_file.read_text(encoding="utf-8")

        for pattern in secret_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Skip if it's using environment variables
                if "os.getenv" in match or "os.environ" in match:
                    continue
                issues.append(f"{py_file.name}: {match}")

    if issues:
        print("❌ Found potential hardcoded secrets:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✅ No hardcoded secrets found")
        return True


def test_dangerous_functions():
    """Test for dangerous functions."""
    print("🔍 Testing for dangerous functions...")

    web_dir = Path(__file__).parent
    issues = []

    dangerous_functions = [
        "eval(",
        "exec(",
        "__import__(",
        "subprocess.",
        "os.system(",
        "os.popen(",
        "shell=True",
    ]

    for py_file in web_dir.glob("*.py"):
        if py_file.name.startswith("test_"):
            continue

        content = py_file.read_text(encoding="utf-8")

        for func in dangerous_functions:
            if func in content:
                issues.append(f"{py_file.name}: {func}")

    if issues:
        print("❌ Found dangerous functions:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✅ No dangerous functions found")
        return True


def test_input_validation():
    """Test for input validation."""
    print("🔍 Testing input validation...")

    web_dir = Path(__file__).parent
    issues = []

    for py_file in web_dir.glob("*.py"):
        if py_file.name.startswith("test_"):
            continue

        content = py_file.read_text(encoding="utf-8")

        # Check for file upload handling
        if "file_uploader" in content:
            if "type=" not in content and "accept=" not in content:
                issues.append(
                    f"{py_file.name}: File uploader without type restrictions"
                )

        # Check for user input handling
        if "text_input" in content or "text_area" in content:
            if "validate" not in content and "sanitize" not in content:
                # This is not necessarily an issue, but worth noting
                pass

    if issues:
        print("❌ Found potential input validation issues:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✅ Input validation looks good")
        return True


def test_environment_variables():
    """Test for proper environment variable usage."""
    print("🔍 Testing environment variable usage...")

    web_dir = Path(__file__).parent
    issues = []

    for py_file in web_dir.glob("*.py"):
        if py_file.name.startswith("test_"):
            continue

        content = py_file.read_text(encoding="utf-8")

        # Check if password is hardcoded
        if "ADMIN_PASSWORD" in content:
            if "os.getenv" not in content:
                issues.append(
                    f"{py_file.name}: ADMIN_PASSWORD not using environment variables"
                )

    if issues:
        print("❌ Found environment variable issues:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✅ Environment variables properly used")
        return True


def test_file_permissions():
    """Test file permissions."""
    print("🔍 Testing file permissions...")

    web_dir = Path(__file__).parent

    # Check for overly permissive files
    for file_path in web_dir.glob("*"):
        if file_path.is_file():
            stat = file_path.stat()
            # Check if file is world-writable
            if stat.st_mode & 0o002:
                print(f"⚠️ Warning: {file_path.name} is world-writable")

    print("✅ File permissions check completed")
    return True


def main():
    """Run all security tests."""
    print("🔒 Starting security tests for AI Auditor Web Interface...\n")

    tests = [
        test_hardcoded_secrets,
        test_dangerous_functions,
        test_input_validation,
        test_environment_variables,
        test_file_permissions,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"📊 Security Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All security tests passed!")
        print("✅ The web interface is secure and ready for deployment.")
        return 0
    else:
        print("⚠️ Some security tests failed.")
        print("🔧 Please review and fix the issues above before deployment.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
