#!/usr/bin/env python3
"""
Test Sphinx documentation build.
"""

import subprocess
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_sphinx_build():
    """Test Sphinx documentation build."""
    print("🧪 Testing Sphinx Documentation Build...")

    try:
        docs_dir = Path(__file__).parent.parent / "docs"

        if not docs_dir.exists():
            print("❌ Documentation directory not found")
            return False

        # Test HTML build
        print("   Building HTML documentation...")
        result = subprocess.run(
            ["make", "-C", str(docs_dir), "html"], capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"❌ HTML build failed: {result.stderr}")
            return False

        # Check if build directory exists
        build_dir = docs_dir / "build" / "html"
        if not build_dir.exists():
            print("❌ HTML build directory not found")
            return False

        # Check if index.html exists
        index_file = build_dir / "index.html"
        if not index_file.exists():
            print("❌ index.html not found")
            return False

        print("✅ HTML documentation build successful")
        print(f"   Build directory: {build_dir}")
        print(f"   Index file: {index_file}")

        return True

    except Exception as e:
        print(f"❌ Documentation build test failed: {e}")
        return False


def test_sphinx_config():
    """Test Sphinx configuration."""
    print("🧪 Testing Sphinx Configuration...")

    try:
        docs_dir = Path(__file__).parent.parent / "docs"
        conf_file = docs_dir / "source" / "conf.py"

        if not conf_file.exists():
            print("❌ conf.py not found")
            return False

        # Test configuration syntax
        print("   Testing configuration syntax...")
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                f"import sys; sys.path.insert(0, '{docs_dir}'); exec(open('{conf_file}').read())",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"❌ Configuration syntax error: {result.stderr}")
            return False

        print("✅ Sphinx configuration is valid")
        return True

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_documentation_structure():
    """Test documentation structure."""
    print("🧪 Testing Documentation Structure...")

    try:
        docs_dir = Path(__file__).parent.parent / "docs"
        source_dir = docs_dir / "source"

        required_files = [
            "index.rst",
            "quickstart.rst",
            "installation.rst",
            "troubleshooting.rst",
            "changelog.rst",
            "conf.py",
        ]

        required_dirs = [
            "user_guide",
            "api",
            "howto",
            "architecture",
            "_static",
            "_templates",
        ]

        # Check required files
        for file_name in required_files:
            file_path = source_dir / file_name
            if not file_path.exists():
                print(f"❌ Required file not found: {file_name}")
                return False

        # Check required directories
        for dir_name in required_dirs:
            dir_path = source_dir / dir_name
            if not dir_path.exists():
                print(f"❌ Required directory not found: {dir_name}")
                return False

        print("✅ Documentation structure is complete")
        print(f"   Source directory: {source_dir}")
        print(f"   Required files: {len(required_files)}")
        print(f"   Required directories: {len(required_dirs)}")

        return True

    except Exception as e:
        print(f"❌ Structure test failed: {e}")
        return False


def test_sphinx_extensions():
    """Test Sphinx extensions."""
    print("🧪 Testing Sphinx Extensions...")

    try:
        # Test if required extensions are available
        extensions = [
            "sphinx.ext.autodoc",
            "sphinx.ext.doctest",
            "sphinx.ext.intersphinx",
            "sphinx.ext.todo",
            "sphinx.ext.coverage",
            "sphinx.ext.mathjax",
            "sphinx.ext.ifconfig",
            "sphinx.ext.viewcode",
            "sphinx.ext.githubpages",
            "sphinx.ext.napoleon",
            "sphinx.ext.autosummary",
            "sphinx_rtd_theme",
        ]

        print("   Testing extension availability...")
        for extension in extensions:
            try:
                __import__(extension)
                print(f"   ✅ {extension}")
            except ImportError:
                print(f"   ❌ {extension} not available")
                return False

        print("✅ All Sphinx extensions are available")
        return True

    except Exception as e:
        print(f"❌ Extensions test failed: {e}")
        return False


def test_documentation_content():
    """Test documentation content."""
    print("🧪 Testing Documentation Content...")

    try:
        docs_dir = Path(__file__).parent.parent / "docs"
        source_dir = docs_dir / "source"

        # Test main index file
        index_file = source_dir / "index.rst"
        if index_file.exists():
            content = index_file.read_text(encoding="utf-8")
            if "AI Auditor" in content and "Dokumentacja" in content:
                print("   ✅ Index file content is valid")
            else:
                print("   ❌ Index file content is invalid")
                return False

        # Test quickstart file
        quickstart_file = source_dir / "quickstart.rst"
        if quickstart_file.exists():
            content = quickstart_file.read_text(encoding="utf-8")
            if "Szybki start" in content and "Instalacja" in content:
                print("   ✅ Quickstart file content is valid")
            else:
                print("   ❌ Quickstart file content is invalid")
                return False

        # Test installation file
        installation_file = source_dir / "installation.rst"
        if installation_file.exists():
            content = installation_file.read_text(encoding="utf-8")
            if "Wymagania systemowe" in content and "Instalacja" in content:
                print("   ✅ Installation file content is valid")
            else:
                print("   ❌ Installation file content is invalid")
                return False

        print("✅ Documentation content is valid")
        return True

    except Exception as e:
        print(f"❌ Content test failed: {e}")
        return False


def main():
    """Run all documentation tests."""
    print("🚀 Starting Documentation Test Suite...")
    print("=" * 60)

    tests = [
        test_sphinx_config,
        test_sphinx_extensions,
        test_documentation_structure,
        test_documentation_content,
        test_sphinx_build,
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
    print(f"📊 Documentation Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All documentation tests passed!")
        return 0
    else:
        print("❌ Some documentation tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
