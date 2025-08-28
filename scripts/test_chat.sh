#!/usr/bin/env bash
set -o pipefail; set +e
cd "$(dirname "$0")/.." || exit 1
source .venv/bin/activate
set -a; [ -f .env.local ] && source .env.local; set +a

python - <<'PY'
import os
from pathlib import Path
try:
    from llama_cpp import Llama
except Exception as e:
    raise SystemExit(f"[BŁĄD] brak 'llama_cpp' lub środowiska: {e}")

def run_once(model_path: str, prompt: str, label: str):
    print(f"\n== {label} ==")
    print(f"[MODEL] {Path(model_path).name}")
    llm = Llama(
        model_path=model_path,
        n_ctx=2048,
        n_threads=4,
        verbose=False
    )
    out = llm.create_completion(prompt, max_tokens=32, temperature=0.2)
    txt = (out.get("choices",[{}])[0] or {}).get("text","").strip()
    print("→", txt)

mp = os.getenv("LLM_GGUF","").strip()
if not mp or not Path(mp).is_file():
    raise SystemExit("[BŁĄD] LLM_GGUF nie ustawione lub plik nie istnieje.")

# 1) Polski
run_once(
    mp,
    "Instrukcja: Odpowiadaj po polsku.\nPytanie: Ile jest 2+2?\nOdpowiedź:",
    "PL test"
)

# 2) English
run_once(
    mp,
    "Instruction: Answer in English.\nQuestion: What is 3+5?\nAnswer:",
    "ENG test"
)

# 3) (opcjonalnie) drugi model
alt = os.getenv("LLM_GGUF_ALT","").strip()
if alt and Path(alt).is_file():
    run_once(
        alt,
        "Instruction: Answer in English.\nQuestion: Capital of France?\nAnswer:",
        "ALT model test"
    )
else:
    print("\n[ALT] Pominięto — brak LLM_GGUF_ALT lub plik nie istnieje.")
PY
