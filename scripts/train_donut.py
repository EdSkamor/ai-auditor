import os, json, random
from datasets import load_dataset
from PIL import Image
from transformers import DonutProcessor, VisionEncoderDecoderModel, TrainingArguments, Trainer
import torch

BASE = os.environ.get("DONUT_BASE","naver-clova-ix/donut-base")
DS   = os.environ.get("DONUT_DS","katanaml-org/invoices-donut-data-v1")
OUT  = os.environ.get("DONUT_OUT","models/donut-auditor")

# 1) data
ds = load_dataset(DS)
# dataset ma pola: image (ścieżka/obraz) i ground_truth (JSON-string)
train_ds = ds["train"]
eval_ds  = ds.get("validation") or ds.get("test") or train_ds.select(range(min(50,len(train_ds))))

# 2) model + processor
processor = DonutProcessor.from_pretrained(BASE)
model = VisionEncoderDecoderModel.from_pretrained(BASE)
# ustawienia tokenów
model.config.pad_token_id = processor.tokenizer.pad_token_id
model.config.decoder_start_token_id = processor.tokenizer.convert_tokens_to_ids("<s>")
model.config.eos_token_id = processor.tokenizer.eos_token_id
model.config.max_length = int(os.environ.get("MAX_LENGTH","768"))
model.config.num_beams = 1

IGNORE_ID = -100

def mk_label(gt: str):
    # ground_truth jest JSON-em; trenujemy sekwencję "<s> {json} </s>"
    gt = gt if isinstance(gt, str) else json.dumps(gt, ensure_ascii=False)
    text = processor.tokenizer.bos_token + gt + processor.tokenizer.eos_token
    labels = processor.tokenizer(text, add_special_tokens=False, return_tensors="pt").input_ids.squeeze(0)
    return labels

def preprocess(example):
    # obraz -> pixel_values
    img = example["image"]
    if not isinstance(img, Image.Image):
        img = Image.open(img).convert("RGB")
    pixel = processor(img, return_tensors="pt").pixel_values.squeeze(0)
    # label
    labels = mk_label(example["ground_truth"])
    # zamień pad na -100 (ignorowane w lossie)
    labels[labels==processor.tokenizer.pad_token_id] = IGNORE_ID
    return {"pixel_values": pixel, "labels": labels}

train_proc = train_ds.map(preprocess, remove_columns=train_ds.column_names)
eval_proc  = eval_ds.map(preprocess, remove_columns=eval_ds.column_names)

# 3) kolator (proste pad-y)
def collate_fn(batch):
    pixel_values = torch.stack([b["pixel_values"] for b in batch])
    labels = [b["labels"] for b in batch]
    max_len = max(x.size(0) for x in labels)
    padded = torch.full((len(labels), max_len), IGNORE_ID, dtype=torch.long)
    for i, l in enumerate(labels):
        padded[i, :l.size(0)] = l
    return {"pixel_values": pixel_values, "labels": padded}

# 4) trening
args = TrainingArguments(
    output_dir=OUT,
    per_device_train_batch_size=int(os.environ.get("BATCH","1")),
    gradient_accumulation_steps=int(os.environ.get("GA","8")),
    num_train_epochs=int(os.environ.get("EPOCHS","10")),
    learning_rate=float(os.environ.get("LR","1e-5")),
    logging_steps=20,
    save_strategy="epoch",
    evaluation_strategy="epoch",
    bf16=True if torch.cuda.is_available() else False,
    fp16=not torch.cuda.is_bf16_supported() if torch.cuda.is_available() else False,
    remove_unused_columns=False,
    report_to=["none"],
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_proc,
    eval_dataset=eval_proc,
    data_collator=collate_fn,
)

trainer.train()
trainer.save_model(OUT)
processor.save_pretrained(OUT)
print("✅ Donut fine-tuned ->", OUT)
