#!/usr/bin/env python3
"""
Skrypt do wykrywania duplikatów funkcji w streamlit_app.py
"""
import ast
import hashlib
import pathlib


def main():
    p = pathlib.Path("streamlit_app.py")
    if not p.exists():
        print("❌ Plik streamlit_app.py nie istnieje")
        return

    code = p.read_text(encoding="utf-8")
    tree = ast.parse(code)

    by_name = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            s, e = node.lineno, node.end_lineno
            frag = "\n".join(code.splitlines()[s - 1 : e])
            sha = hashlib.sha1(frag.encode()).hexdigest()[:10]
            by_name.setdefault(node.name, []).append((s, e, sha))

    dupes = {k: v for k, v in by_name.items() if len(v) > 1}
    if not dupes:
        print("✅ Brak zduplikowanych funkcji 🎉")
        return

    print(f"🔍 Znaleziono {len(dupes)} zduplikowanych funkcji:")
    for name, items in dupes.items():
        print(f"\n=== {name} ===")
        for i, (s, e, sha) in enumerate(sorted(items), 1):
            print(f"{i}. linie {s}-{e}  sha:{sha}")


if __name__ == "__main__":
    main()
