#!/usr/bin/env python3
import sys, re, ast
from pathlib import Path

P = Path("app/pages/02_Przeglad.py")
if not P.exists():
    print(f"[ERR] Brak pliku: {P}")
    sys.exit(1)

src = P.read_text(encoding="utf-8")
try:
    ast.parse(src)
except SyntaxError as e:
    print(f"[ERR] SyntaxError w {P}: {e}")
    sys.exit(2)

def need(pattern, desc):
    if not re.search(pattern, src, re.S):
        print(f"[ERR] Brak wzorca: {desc}")
        sys.exit(3)

need(r"def\s+save_decisions\(", "save_decisions()")
need(r"def\s+export_with_decisions\(", "export_with_decisions()")
need(r"def\s+summarize_current\(", "summarize_current()")
need(r"\.fillna\(\s*\"\"\s*\)", 'fillna("") na kolumnie decision')
need(r"st\.data_editor\(", "UI: data_editor")
need(r"Zaznacz wszystko", "UI: przycisk Zaznacz wszystko")

print("[OK] 02_Przeglad.py istnieje i wygląda poprawnie.")
sys.exit(0)
