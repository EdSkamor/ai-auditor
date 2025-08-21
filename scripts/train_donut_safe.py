import os, json, torch
from datasets import load_dataset
from transformers import DonutProcessor, VisionEncoderDecoderModel, TrainingArguments, Trainer

BASE = os.environ.get("DONUT_BASE","naver-clova-ix/donut-base")
DS   = os.environ.get("DONUT_DS","katanaml-org/invoices-donut-data-v1")
OUT  = os.environ.get("DONUT_OUT","models/donut-auditor")

EPOCHS = int(os.environ.get("EPOCHS","6"))
BATCH  = int(os.environ.get("BATCH","1"))
GA     = int(os.environ.get("GA","16"))
LR     = float(os.environ.get("LR","5e-5"))
MAXLEN = int(os.environ.get("MAX_LENGTH","768"))

gpu = torch.cuda.is_available()
bf16 = gpu and torch.cuda.get_device_capability(0)[0] >= 8
fp16 = gpu and not bf16
print(f"[cfg] base={BASE} ds={DS} out={OUT} epochs={EPOCHS} bs={BATCH} ga={GA} lr={LR} bf16={bf16} fp16={fp16}")

processor = DonutProcessor.from_pretrained(BASE, use_fast=True)
model = VisionEncoderDecoderModel.from_pretrained(BASE)
model.config.max_length = MAXLEN

ds = load_dataset(DS)

def encode_batch(examples):
    pixel_values, labels = [], []
    for image, label in zip(examples["image"], examples["ground_truth"]):
        pv = processor(image.convert("RGB"), return_tensors="pt").pixel_values.squeeze(0)
        pixel_values.append(pv)
        txt = json.dumps(label, ensure_ascii=False)
        labels.append(processor.tokenizer(txt, add_special_tokens=False)["input_ids"])
    examples["pixel_values"] = pixel_values
    examples["labels"] = labels
    return examples

train = ds["train"].map(encode_batch, batched=True, remove_columns=ds["train"].column_names)
valid = ds["validation"].map(encode_batch, batched=True, remove_columns=ds["validation"].column_names)

args = TrainingArguments(
    output_dir=OUT,
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH,
    gradient_accumulation_steps=GA,
    learning_rate=LR,
    logging_steps=5,
    save_total_limit=1,
    bf16=bf16,
    fp16=fp16 if not bf16 else False,
    dataloader_num_workers=2,
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train,
    eval_dataset=valid,
    processing_class=processor,  # zamiast przestarzałego `tokenizer=...`
)

resume = os.environ.get("RESUME") or None
trainer.train(resume_from_checkpoint=resume)
trainer.save_model(OUT)
processor.save_pretrained(OUT)
print("[done] saved to", OUT)
