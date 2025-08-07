from pathlib import Path
import subprocess, shlex, textwrap, os

LLAMA_BIN  = Path(__file__).parent / "third_party" / "llama.cpp" / "build" / "bin" / "llama-cli"
MODEL_PATH = Path.home() / "models" / "llama3" / "meta-llama-3-8b-instruct.Q4_K_M.gguf"

def call_model(prompt: str, n_predict: int = 80, ngl: int = 100, timeout_s: int = 900):
    threads = os.cpu_count() or 8
    cmd = (
        f"{LLAMA_BIN} "
        f"-no-cnv "                          # wyłącza tryb rozmowy / interaktywny
        f"-p {shlex.quote(prompt)} "
        f"-n {n_predict} "
        f"-ngl {ngl} -t {threads} --temp 0.2 "
        f"-m {MODEL_PATH}"
    )
    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=timeout_s)
    if proc.returncode != 0:
        return f"[LLAMA ERROR] {proc.stderr.strip()}"
    return textwrap.dedent(proc.stdout).strip()
