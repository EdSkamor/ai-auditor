#!/usr/bin/env python3
"""
WSAD Test Script: Demo Validation
Tests single file validation functionality.
"""

import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.validate import ValidateCLI
from cli.base import CLIError


def test_demo_validation():
    """Test demo validation functionality."""
    print("🧪 Testing Demo Validation...")
    
    # Create test data
    test_data = """Company,Amount,Date
ACME Corp,1000,2023-01-01
Test Inc,2000,2023-01-02
Sample Ltd,1500,2023-01-03"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(test_data)
        test_file = Path(f.name)
    
    try:
        # Test CLI with demo mode
        cli = ValidateCLI()
        
        # Test argument validation
        args = cli.parser.parse_args([
            "--demo",
            "--file", str(test_file),
            "--dry-run"
        ])
        
        cli._validate_args(args)
        print("✅ Argument validation passed")
        
        # Test dry run
        exit_code = cli._run_demo_validation(args, {})
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}"
        print("✅ Demo validation dry run passed")
        
        print("🎉 Demo validation test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Demo validation test failed: {e}")
        return False
    
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


def test_validation_errors():
    """Test validation error handling."""
    print("🧪 Testing Validation Error Handling...")
    
    cli = ValidateCLI()
    
    try:
        # Test missing file
        args = cli.parser.parse_args(["--demo", "--file", "nonexistent.csv"])
        cli._validate_args(args)
        print("❌ Should have failed with missing file")
        return False
        
    except CLIError as e:
        if e.exit_code.value == 3:  # FILE_NOT_FOUND
            print("✅ Correctly caught missing file error")
        else:
            print(f"❌ Wrong error type: {e}")
            return False
    
    try:
        # Test missing mode
        args = cli.parser.parse_args(["--file", "test.csv"])
        cli._validate_args(args)
        print("❌ Should have failed with missing mode")
        return False
        
    except CLIError as e:
        if e.exit_code.value == 2:  # INVALID_ARGS
            print("✅ Correctly caught missing mode error")
        else:
            print(f"❌ Wrong error type: {e}")
            return False
    
    print("🎉 Validation error handling test completed successfully!")
    return True


if __name__ == "__main__":
    print("🚀 Starting Validation Demo Tests...")
    
    success = True
    success &= test_demo_validation()
    success &= test_validation_errors()
    
    if success:
        print("\n🎉 All validation demo tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some validation demo tests failed!")
        sys.exit(1)
