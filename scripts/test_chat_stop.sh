#!/usr/bin/env bash
set -o pipefail; set +e
cd "$(dirname "$0")/.." || exit 1
source .venv/bin/activate
set -a; [ -f .env.local ] && source .env.local; set +a

python - <<'PY'
import os, re, sys
from pathlib import Path
from llama_cpp import Llama

mp = os.getenv("LLM_GGUF","").strip()
if not mp or not Path(mp).is_file():
    print("[BŁĄD] LLM_GGUF nie ustawione lub plik nie istnieje.")
    sys.exit(2)

def ask_num(llm, prompt):
    out = llm.create_completion(
        prompt,
        max_tokens=8,
        temperature=0.1,
        stop=["\n","Question:","Pytanie:"]
    )
    txt = (out.get("choices",[{}])[0] or {}).get("text","")
    txt = txt.strip()
    # wyciągnij pierwszą liczbę całkowitą/zmiennoprzecinkową
    m = re.search(r"[-+]?\d+(?:[.,]\d+)?", txt)
    return txt, (m.group(0).replace(",","." ) if m else None)

print(f"[MODEL] {Path(mp).name}")
llm = Llama(model_path=mp, n_ctx=2048, n_threads=4, verbose=False)

tests = [
    ("Instrukcja: Odpowiadaj po polsku. Zwracaj tylko wynik.\nPytanie: Ile jest 2+2?\nOdpowiedź:", "4", "PL 2+2"),
    ("Instruction: Answer in English. Return only the result.\nQuestion: What is 3+5?\nAnswer:", "8", "ENG 3+5"),
]

fail = 0
for prompt, expect, label in tests:
    txt, num = ask_num(llm, prompt)
    ok = (num == expect)
    print(f"\n== {label} ==")
    print("RAW:", repr(txt))
    print("PARSED:", num, " EXPECT:", expect, " =>", "PASS" if ok else "FAIL")
    if not ok: fail += 1

alt = os.getenv("LLM_GGUF_ALT","").strip()
if alt and Path(alt).is_file():
    llm2 = Llama(model_path=alt, n_ctx=2048, n_threads=4, verbose=False)
    txt, num = ask_num(llm2, "Instruction: English. Return only the result.\nQuestion: 7-2?\nAnswer:")
    ok = (num == "5")
    print(f"\n== ALT model ({Path(alt).name}) ==")
    print("RAW:", repr(txt))
    print("PARSED:", num, " EXPECT: 5  =>", "PASS" if ok else "FAIL")
    if not ok: fail += 1
else:
    print("\n[ALT] Pominięto — brak LLM_GGUF_ALT lub plik nie istnieje.")

sys.exit(1 if fail else 0)
PY
rc=$?
echo
if [ $rc -eq 0 ]; then
  echo "[OK] Wszystkie asercje zaliczone."
else
  echo "[FAIL] Coś poszło nie tak (kod $rc)."
fi
exit $rc
