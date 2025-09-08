from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

BASE = "meta-llama/Meta-Llama-3-8B-Instruct"
ADAPTER_DIR = (Path(__file__).resolve().parent / "outputs" / "lora-auditor").resolve()

SYSTEM_PROMPT = (
    "Jesteś doświadczonym audytorem finansowym z wieloletnim doświadczeniem. "
    "Odpowiadasz po polsku w sposób naturalny i przyjazny, jak kolega po fachu. "
    "Używasz praktycznych przykładów, czasem żartujesz, ale zawsze profesjonalnie. "
    "Wyjaśniasz skomplikowane zagadnienia prostym językiem. "
    "Przy różnicach wartości podawaj p.p. (punkty procentowe), a nie %. "
    "Bądź pomocny, ale nie przesadnie formalny - mów jak człowiek, nie jak instrukcja."
)

_tok = None
_model = None

def _load():
    global _tok, _model
    if _tok is not None and _model is not None:
        return

    _tok = AutoTokenizer.from_pretrained(BASE, use_fast=False)
    if _tok.pad_token_id is None:
        _tok.pad_token = _tok.eos_token

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,  # szybsze wykonywanie na większości GPU
    )
    base = AutoModelForCausalLM.from_pretrained(
        BASE,
        quantization_config=bnb,
        device_map="auto",
    )
    _model = PeftModel.from_pretrained(base, str(ADAPTER_DIR), device_map="auto")
    _model.eval()

def call_model(prompt: str, max_new_tokens: int = 160, do_sample: bool = True,
               temperature: float = 0.8, top_p: float = 0.9) -> str:
    _load()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    inputs = _tok.apply_chat_template(messages, return_tensors="pt", add_generation_prompt=True)
    input_ids = inputs.to(_model.device)
    # bezpieczna maska uwagi dla pojedynczego przykładu
    attention_mask = torch.ones_like(input_ids, dtype=torch.long)

    gen_kwargs = dict(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_new_tokens=max_new_tokens,
        do_sample=do_sample,
        pad_token_id=_tok.eos_token_id,
    )
    if do_sample:
        gen_kwargs.update(temperature=temperature, top_p=top_p)

    with torch.no_grad():
        out_ids = _model.generate(**gen_kwargs)

    out = _tok.decode(out_ids[0, input_ids.shape[1]:], skip_special_tokens=True)
    return out.strip()
