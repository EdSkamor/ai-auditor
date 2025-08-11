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
    if _tok is not None and _model is not None:
        return

    _tok = AutoTokenizer.from_pretrained(BASE, use_fast=False)
    if _tok.pad_token_id is None:
        _tok.pad_token = _tok.eos_token  # zapewnij pad_token

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )
    base = AutoModelForCausalLM.from_pretrained(
        BASE,
        quantization_config=bnb,
        device_map="auto",
        torch_dtype=torch.float16,
    )
    _model = PeftModel.from_pretrained(base, str(ADAPTER_DIR), device_map="auto")
    _model.eval()

def call_model(
    prompt: str,
    max_new_tokens: int = 200,
    do_sample: bool = False,
    temperature: float = 0.7,
    top_p: float = 0.9,
) -> str:
    _load()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    # tokenizacja w trybie czatu
    input_ids = _tok.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt",
    ).to(_model.device)

    pad_id = _tok.pad_token_id if _tok.pad_token_id is not None else _tok.eos_token_id
    attention_mask = (input_ids != pad_id)

    gen_kwargs = dict(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_new_tokens=max_new_tokens,
        pad_token_id=_tok.eos_token_id,
    )
    if do_sample:
        gen_kwargs.update(do_sample=True, temperature=temperature, top_p=top_p)
    else:
        gen_kwargs.update(do_sample=False)

    with torch.inference_mode():
        out_full = _model.generate(**gen_kwargs)

    # odetnij prompt
    out_ids = out_full[0, input_ids.shape[1]:]
    text = _tok.decode(out_ids, skip_special_tokens=True)
    return text.strip()
