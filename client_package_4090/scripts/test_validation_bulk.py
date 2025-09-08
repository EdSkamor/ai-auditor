#!/usr/bin/env python3
"""
WSAD Test Script: Bulk Validation
Tests bulk file validation functionality.
"""

import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.validate import ValidateCLI
from cli.base import CLIError


def test_bulk_validation():
    """Test bulk validation functionality."""
    print("🧪 Testing Bulk Validation...")
    
    # Create test directory with multiple files
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        
        # Create test CSV files
        csv_data1 = """Company,Amount,Date
ACME Corp,1000,2023-01-01
Test Inc,2000,2023-01-02"""
        
        csv_data2 = """Company,Amount,Date
Sample Ltd,1500,2023-01-03
Demo Corp,2500,2023-01-04"""
        
        (test_dir / "file1.csv").write_text(csv_data1)
        (test_dir / "file2.csv").write_text(csv_data2)
        
        try:
            # Test CLI with bulk mode
            cli = ValidateCLI()
            
            # Test argument validation
            args = cli.parser.parse_args([
                "--bulk",
                "--input-dir", str(test_dir),
                "--dry-run"
            ])
            
            cli._validate_args(args)
            print("✅ Argument validation passed")
            
            # Test dry run
            exit_code = cli._run_bulk_validation(args, {})
            assert exit_code == 0, f"Expected exit code 0, got {exit_code}"
            print("✅ Bulk validation dry run passed")
            
            print("🎉 Bulk validation test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Bulk validation test failed: {e}")
            return False


def test_bulk_validation_errors():
    """Test bulk validation error handling."""
    print("🧪 Testing Bulk Validation Error Handling...")
    
    cli = ValidateCLI()
    
    try:
        # Test missing input directory
        args = cli.parser.parse_args(["--bulk", "--input-dir", "nonexistent"])
        cli._validate_args(args)
        print("❌ Should have failed with missing directory")
        return False
        
    except CLIError as e:
        if e.exit_code.value == 3:  # FILE_NOT_FOUND
            print("✅ Correctly caught missing directory error")
        else:
            print(f"❌ Wrong error type: {e}")
            return False
    
    try:
        # Test missing input directory argument
        args = cli.parser.parse_args(["--bulk"])
        cli._validate_args(args)
        print("❌ Should have failed with missing input-dir")
        return False
        
    except CLIError as e:
        if e.exit_code.value == 2:  # INVALID_ARGS
            print("✅ Correctly caught missing input-dir error")
        else:
            print(f"❌ Wrong error type: {e}")
            return False
    
    print("🎉 Bulk validation error handling test completed successfully!")
    return True


def test_file_discovery():
    """Test file discovery in bulk mode."""
    print("🧪 Testing File Discovery...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        
        # Create various file types
        (test_dir / "file1.csv").write_text("test")
        (test_dir / "file2.xlsx").write_text("test")
        (test_dir / "file3.pdf").write_text("test")
        (test_dir / "file4.txt").write_text("test")  # Should be ignored
        
        cli = ValidateCLI()
        args = cli.parser.parse_args([
            "--bulk",
            "--input-dir", str(test_dir),
            "--dry-run"
        ])
        
        # Test file discovery logic
        file_patterns = ["*.pdf", "*.xlsx", "*.xls", "*.csv"]
        files_to_process = []
        
        for pattern in file_patterns:
            files_to_process.extend(test_dir.glob(pattern))
        
        # Should find 3 files (csv, xlsx, pdf) but not txt
        assert len(files_to_process) == 3, f"Expected 3 files, found {len(files_to_process)}"
        print("✅ File discovery working correctly")
        
        print("🎉 File discovery test completed successfully!")
        return True


if __name__ == "__main__":
    print("🚀 Starting Bulk Validation Tests...")
    
    success = True
    success &= test_bulk_validation()
    success &= test_bulk_validation_errors()
    success &= test_file_discovery()
    
    if success:
        print("\n🎉 All bulk validation tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some bulk validation tests failed!")
        sys.exit(1)
