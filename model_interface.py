from pathlib import Path
import subprocess, shlex, textwrap, os

LLAMA_BIN    = Path(__file__).parent / "third_party" / "llama.cpp" / "build" / "bin" / "llama-cli"
MODEL_PATH   = Path.home() / "models" / "llama3" / "meta-llama-3-8b-instruct.Q4_K_M.gguf"
LORA_ADAPTER = Path(__file__).parent / "outputs" / "lora-auditor"

def call_model(prompt: str,
               n_predict: int = 80,
               ngl: int = 100,
               timeout_s: int = 900) -> str:
    threads = os.cpu_count() or 8
    cmd = [
        str(LLAMA_BIN),
        "-no-cnv",                     # <— pojedynczy dash
        "--lora", str(LORA_ADAPTER),
        "-m", str(MODEL_PATH),
        "-p", prompt,
        "-n", str(n_predict),
        "-ngl", str(ngl),
        "-t", str(threads),
        "--temp", "0.2"
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
    if proc.returncode != 0:
        return f"[LLAMA ERROR] {proc.stderr.strip()}"
    return textwrap.dedent(proc.stdout).strip()
