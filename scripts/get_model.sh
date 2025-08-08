#!/usr/bin/env bash
# Pobierz plik .gguf (4.6 GB) i umieść w ~/models/llama3/
set -e
mkdir -p ~/models/llama3
echo "🔗 Otwórz w przeglądarce i zaloguj się na HuggingFace:"
echo "   https://huggingface.co/meta-llama/Llama-3-8b-Instruct-GGUF"
echo
echo "⬇️  Pobierz plik  »  meta-llama-3-8b-instruct.Q4_K_M.gguf  «"
echo "📂  Skopiuj go do:  ~/models/llama3/"
echo
echo "✅ Gotowe. Plik powinien mieć ok. 4,6 GB."
