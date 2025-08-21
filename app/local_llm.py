import os
from functools import lru_cache
from llama_cpp import Llama

def _env_int(name, default):
    try:
        return int(os.getenv(name, default))
    except Exception:
        return default

@lru_cache(maxsize=1)
def get_llm():
    model = os.getenv("LLM_GGUF","")
    if not model or not os.path.isfile(model):
        raise FileNotFoundError("Ustaw zmienną LLM_GGUF na pełną ścieżkę do modelu .gguf")
    return Llama(
        model_path=model,
        n_ctx=_env_int("LLM_CTX", 8192),
        n_threads=_env_int("LLM_THREADS", 6),
        n_gpu_layers=_env_int("LLM_GPU_LAYERS", 0),
        chat_format=os.getenv("LLM_CHAT_FORMAT","llama-3"),
        verbose=False,
    )

def stream_chat(messages, **kw):
    llm = get_llm()
    for chunk in llm.create_chat_completion(messages=messages, stream=True, **kw):
        delta = chunk["choices"][0]["delta"].get("content","")
        if delta:
            yield delta

def reset():
    get_llm.cache_clear()
