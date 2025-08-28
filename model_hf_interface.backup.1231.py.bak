from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

BASE = "meta-llama/Meta-Llama-3-8B-Instruct"
ADAPTER_DIR = (Path(__file__).resolve().parent / "outputs" / "lora-auditor").resolve()

SYSTEM_PROMPT = (
    "Jesteś ekspertem ds. audytu finansowego. "
    "Odpowiadasz wyłącznie po polsku, zwięźle i rzeczowo; gdy to pasuje – w punktach. "
    "Przy różnicach wartości podawaj p.p. (punkty procentowe), a nie %."
)

_tok = None
_model = None

def _load():
    global _tok, _model
    if _model is not None:
        return

    _tok = AutoTokenizer.from_pretrained(BASE, use_fast=False)
    if _tok.pad_token_id is None:
        _tok.pad_token = _tok.eos_token

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True
    )

    base = AutoModelForCausalLM.from_pretrained(
        BASE,
        quantization_config=bnb,
        device_map="auto",
    )

    # Spróbuj doładować LoRA, ale nie wysypuj jeśli się nie uda
    try:
        if (ADAPTER_DIR / "adapter_model.safetensors").exists():
            base = PeftModel.from_pretrained(base, str(ADAPTER_DIR), device_map="auto")
    except Exception as e:
        print("[WARN] Nie udało się załadować LoRA:", e)

    _model = base.eval()

def call_model(
    prompt: str,
    max_new_tokens: int = 220,
    do_sample: bool = False,
    temperature: float = 0.2,
    top_p: float = 0.9,
) -> str:
    _load()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    inputs = _tok.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt"
    ).to(_model.device)

    gen_kwargs = dict(
        max_new_tokens=max_new_tokens,
        do_sample=do_sample,
        pad_token_id=_tok.eos_token_id,
    )
    if do_sample:
        gen_kwargs.update(temperature=temperature, top_p=top_p)

    with torch.no_grad():
        out_ids = _model.generate(input_ids, attention_mask=attention_mask, max_new_tokens=max_new_tokens, do_sample=do_sample, temperature=temperature, top_p=top_p, pad_token_id=_tok.eos_token_id)

    out_text = _tok.decode(out_ids[0, inputs.shape[1]:], skip_special_tokens=True)
    return out_text.strip()
