import os, json
from datasets import load_dataset
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig,
    TrainingArguments, Trainer, DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

BASE = os.environ.get("BASE_MODEL","meta-llama/Meta-Llama-3-8B-Instruct")
DATA = os.environ.get("FT_DATA","data/ft/train.jsonl")
OUT  = os.environ.get("FT_OUT","outputs/lora-auditor-overnight")

assert os.path.exists(DATA), f"Brak pliku z danymi: {DATA}"

# === 1) Dataset (jsonl: {"messages":[{role,content},...], ...})
raw = load_dataset("json", data_files=DATA, split="train")

tok = AutoTokenizer.from_pretrained(BASE, use_fast=False)
if tok.pad_token_id is None:
    tok.pad_token = tok.eos_token

def to_text(example):
    msgs = example["messages"]
    # korzystamy z chat template Llamy – dostaje czysty tekst gotowy do tokenizacji
    txt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)
    return {"text": txt}

raw = raw.map(to_text, remove_columns=[c for c in raw.column_names if c != "text"])

# tokenizacja (batched; max_seq_length=2048 – dostosuj do VRAM)
MAX_LEN = int(os.environ.get("MAX_LEN","2048"))
def tokenize(batch):
    return tok(batch["text"], truncation=True, max_length=MAX_LEN)

tok_ds = raw.map(tokenize, batched=True, remove_columns=["text"])

# === 2) Model 4-bit + przygotowanie pod LoRA
bnb = BitsAndBytesConfig(
    load_in_4bit=True, bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype="float16"
)
base = AutoModelForCausalLM.from_pretrained(BASE, quantization_config=bnb)
base = prepare_model_for_kbit_training(base)

peft_cfg = LoraConfig(
    r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
    target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"]
)
model = get_peft_model(base, peft_cfg)

# === 3) Trener (transformers.Trainer)
args = TrainingArguments(
    output_dir=OUT,
    num_train_epochs=int(os.environ.get("EPOCHS","3")),
    per_device_train_batch_size=int(os.environ.get("BATCH","1")),
    gradient_accumulation_steps=int(os.environ.get("GA","16")),
    learning_rate=float(os.environ.get("LR","2e-4")),
    lr_scheduler_type="cosine",
    bf16=True,
    logging_steps=10,
    save_strategy="epoch",
    report_to=["tensorboard"],
)
collator = DataCollatorForLanguageModeling(tokenizer=tok, mlm=False)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tok_ds,
    data_collator=collator,
)

trainer.train()
trainer.save_model(OUT)  # zapisze adaptery w OUT

print("LoRA adapters saved to:", OUT)
