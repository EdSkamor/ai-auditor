from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

BASE = "meta-llama/Meta-Llama-3-8B-Instruct"
ADAPTER = str((Path(__file__).resolve().parent / "outputs" / "lora-auditor").resolve())

SYSTEM_PROMPT = (
    "Jesteś ekspertem ds. audytu finansowego. "
    "Odpowiadasz wyłącznie po polsku, zwięźle i rzeczowo; gdy to pasuje – w punktach. "
    "Przy różnicach wartości podawaj p.p. (punkty procentowe), a nie %."
)

_tok = None
_base = None
_model = None

def _load():
    global _tok, _base, _model
    if _model is not None:
        return

    _tok = AutoTokenizer.from_pretrained(BASE, use_fast=False)
    _tok.pad_token = _tok.eos_token

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True
    )
    _base = AutoModelForCausalLM.from_pretrained(
        BASE,
        quantization_config=bnb,
        device_map="auto",
    )

    # jeśli jest LoRA – ładujemy; jeśli nie – jedziemy na bazie
    if (Path(ADAPTER) / "adapter_model.safetensors").exists():
        _model = PeftModel.from_pretrained(_base, ADAPTER, device_map="auto")
    else:
        _model = _base

def call_model(prompt: str,
               max_new_tokens: int = 160,
               do_sample: bool = False,
               temperature: float = 0.2,
               top_p: float = 0.9) -> str:
    _load()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": prompt},
    ]

    if hasattr(_tok, "apply_chat_template"):
        text = _tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    else:
        text = f"{SYSTEM_PROMPT}\n\nUżytkownik: {prompt}\nAsystent:"

    inputs = _tok(text, return_tensors="pt")
    inputs = {k: v.to(_model.device) for k, v in inputs.items()}

    gen_kwargs = dict(
        max_new_tokens=max_new_tokens,
        pad_token_id=_tok.eos_token_id,
        do_sample=do_sample,
    )
    if do_sample:
        gen_kwargs.update(temperature=temperature, top_p=top_p)

    with torch.inference_mode():
        out_ids = _model.generate(**inputs, **gen_kwargs)

    out = _tok.decode(out_ids[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return out.strip()
