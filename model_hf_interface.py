from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import torch

bnb = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.float16
)

BASE    = "meta-llama/Meta-Llama-3-8B-Instruct"
ADAPTER = "outputs/lora-auditor"

_tok = None
_model = None

def call_model(prompt: str, max_new_tokens: int = 180, temperature: float = 0.1) -> str:
    global _tok, _model
    if _tok is None:
        _tok = AutoTokenizer.from_pretrained(BASE, use_fast=False)
        _tok.pad_token = _tok.eos_token
    if _model is None:
        base = AutoModelForCausalLM.from_pretrained(
            BASE,
            quantization_config=bnb,
            device_map="auto",
        )
        _model = PeftModel.from_pretrained(base, ADAPTER, device_map="auto")
        _model.eval()

    inputs = _tok(prompt, return_tensors="pt").to(_model.device)
    out_ids = _model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=False,                 # greedy -> stabilne, „bez fantazji”
        temperature=temperature,         # ignorowane, ale zostawiamy w API
        pad_token_id=_tok.eos_token_id,
        eos_token_id=_tok.eos_token_id
    )
    gen_ids = out_ids[0, inputs["input_ids"].shape[-1]:]
    return _tok.decode(gen_ids, skip_special_tokens=True).strip()
