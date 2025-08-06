from pathlib import Path
import subprocess, shlex, textwrap

LLAMA_BIN  = Path(__file__).parent / "third_party" / "llama.cpp" / "build" / "bin" / "llama-cli"
MODEL_PATH = Path.home() / "models" / "llama3" / "meta-llama-3-8b-instruct.Q4_K_M.gguf"

def call_model(prompt: str, n_predict: int = 120, ngl: int = 100) -> str:
    cmd = f'{LLAMA_BIN} -m {MODEL_PATH} -p {shlex.quote(prompt)} -n {n_predict} -ngl {ngl} --temp 0.2'
    proc = subprocess.run(shlex.split(str(cmd)), capture_output=True, text=True, timeout=180)
    if proc.returncode != 0:
        return f"[LLAMA ERROR] {proc.stderr.strip()}"
    return textwrap.dedent(proc.stdout).strip()
