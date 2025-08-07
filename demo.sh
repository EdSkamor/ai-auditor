#!/usr/bin/env bash
set -e
python3 prompt_generator.py | tee outputs/demo_output.txt
echo
echo "✅  Wynik zapisany w  outputs/demo_output.txt"
