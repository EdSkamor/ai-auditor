from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

BASE = "meta-llama/Meta-Llama-3-8B-Instruct"
ADAPTER = str((Path(__file__).resolve().parent / "outputs" / "lora-auditor").resolve())

SYSTEM_PROMPT = (
    "Jesteś ekspertem ds. audytu finansowego. "
    "Odpowiadasz po polsku, zwięźle i rzeczowo; gdy to pasuje – w punktach. "
    "Unikaj dygresji."
)

_tok = None
_base = None
_model = None

def _load():
    global _tok, _base, _model
    if _tok is None:
        _tok = AutoTokenizer.from_pretrained(BASE, use_fast=False)
        _tok.pad_token = _tok.eos_token
    if _base is None:
        bnb = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.float16,
        )
        _base = AutoModelForCausalLM.from_pretrained(
            BASE,
            quantization_config=bnb,
            device_map="auto",
        )
    if _model is None:
        _model = PeftModel.from_pretrained(_base, ADAPTER, device_map="auto")
        _model.eval()
    return _tok, _model

def call_model(text: str, max_new_tokens: int = 160, temperature: float | None = None,
               top_p: float | None = None, do_sample: bool = False) -> str:
    tok, model = _load()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": text},
    ]
    prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tok([prompt], return_tensors="pt").to(model.device)

    gen_kwargs = {
        "max_new_tokens": max_new_tokens,
        "do_sample": do_sample,
        "pad_token_id": tok.eos_token_id,
    }
    if do_sample:
        if temperature is not None:
            gen_kwargs["temperature"] = float(temperature)
        if top_p is not None:
            gen_kwargs["top_p"] = float(top_p)

    with torch.inference_mode():
        out = model.generate(**inputs, **gen_kwargs)

    gen_text = tok.decode(out[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return gen_text.strip()
