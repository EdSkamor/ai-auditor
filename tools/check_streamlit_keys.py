#!/usr/bin/env python3
"""
Check for duplicate Streamlit keys in Python files.
Used as pre-commit hook to prevent key conflicts.
"""

import ast
import sys
from collections import defaultdict
from pathlib import Path


def check_streamlit_keys(filename):
    """Check for duplicate Streamlit keys in a file."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        keys = defaultdict(list)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if hasattr(node.func, "attr") and node.func.attr in [
                    "button",
                    "selectbox",
                    "text_input",
                    "checkbox",
                    "slider",
                    "file_uploader",
                ]:
                    for keyword in node.keywords:
                        if keyword.arg == "key" and isinstance(
                            keyword.value, ast.Constant
                        ):
                            key_value = keyword.value.value
                            keys[key_value].append(node.lineno)

        duplicates = {k: lines for k, lines in keys.items() if len(lines) > 1}
        if duplicates:
            print(f"❌ Duplicate Streamlit keys in {filename}:")
            for key, lines in duplicates.items():
                print(f'  Key "{key}" used on lines: {lines}')
            return False
        return True
    except Exception as e:
        print(f"Error checking {filename}: {e}")
        return True


def main():
    """Main function."""
    files = sys.argv[1:] if len(sys.argv) > 1 else ["streamlit_app.py"]
    all_good = True

    for file in files:
        if file.endswith(".py") and Path(file).exists():
            if not check_streamlit_keys(file):
                all_good = False

    if all_good:
        print("✅ No duplicate Streamlit keys found")

    sys.exit(0 if all_good else 1)


if __name__ == "__main__":
    main()
