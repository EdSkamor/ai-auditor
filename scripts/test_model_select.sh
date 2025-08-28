#!/usr/bin/env bash
set -o pipefail; set +e
cd "$(dirname "$0")/.." || exit 1
source .venv/bin/activate

python - <<'PY'
import os, sys
from pathlib import Path
from llama_cpp import Llama

# identyczna logika wyszukiwania jak w UI
roots = [os.path.expanduser("~/models"), os.path.expanduser("~/Downloads"), os.path.join(os.getcwd(),"models")]
cand = []
for r in roots:
    if os.path.isdir(r):
        cand += [str(p.resolve()) for p in Path(r).rglob("*.gguf")]
env_default = os.getenv("LLM_GGUF","")
if env_default and Path(env_default).is_file() and env_default not in cand:
    cand.insert(0, env_default)

if not cand:
    print("[FAIL] Brak .gguf w standardowych lokalizacjach.")
    sys.exit(1)

print("[MODELS]")
for i,p in enumerate(cand[:10]):
    print(f"{i:2d} | {p}")

model = cand[0]
print(f"\n[LOAD] {Path(model).name}")
llm = Llama(model_path=model, n_ctx=2048, n_threads=int(os.getenv("LLAMA_THREADS","4")), verbose=False)

def ask(prompt, stop=None):
    out = llm.create_completion(prompt, max_tokens=16, temperature=0.2, stop=stop)
    return (out.get("choices",[{}])[0] or {}).get("text","").strip()

pl = ask("Instrukcja: Odpowiadaj po polsku. Zwracaj tylko wynik.\nPytanie: Ile jest 2+2?\nOdpowiedź:", stop=["\n","Question:","Pytanie:"])
en = ask("Instruction: Answer in English. Return only the result.\nQuestion: What is 3+5?\nAnswer:", stop=["\n","Question:","Pytanie:"])

ok = (pl=="4" and en=="8")
print("\n[RESULTS] PL:", pl, " | ENG:", en)
print("[", "PASS" if ok else "FAIL", "]")
sys.exit(0 if ok else 2)
PY
