import os, json, torch
from pathlib import Path
from PIL import Image
from torch.utils.data import Dataset
from transformers import DonutProcessor, VisionEncoderDecoderModel, TrainingArguments, Trainer

BASE   = os.environ.get("DONUT_BASE","naver-clova-ix/donut-base")
OUT    = os.environ.get("DONUT_OUT","models/donut-auditor-local")
MAXLEN = int(os.environ.get("MAX_LENGTH","768"))
EPOCHS = int(os.environ.get("EPOCHS","6"))
BATCH  = int(os.environ.get("BATCH","1"))
GA     = int(os.environ.get("GA","16"))
LR     = float(os.environ.get("LR","5e-5"))

gpu  = torch.cuda.is_available()
bf16 = gpu and torch.cuda.get_device_capability(0)[0] >= 8
fp16 = gpu and not bf16

DATA_DIR = Path("data/local_donut")

def load_jsonl(p: str):
    return [json.loads(l) for l in open(p, encoding="utf-8")]

class LocalDonutDS(Dataset):
    def __init__(self, items, processor, max_length):
        self.items = items
        self.processor = processor
        self.max_length = max_length
    def __len__(self): return len(self.items)
    def __getitem__(self, i):
        ex = self.items[i]
        image = Image.open(ex["image_path"]).convert("RGB")
        label_text = json.dumps(ex["labels"], ensure_ascii=False)

        enc = self.processor(
            images=image,
            text=label_text,
            return_tensors="pt",
            max_length=self.max_length,
            truncation=True,
        )
        pixel_values = enc.pixel_values.squeeze(0)
        labels = enc.input_ids.squeeze(0)

        # Zmaskuj pady na -100 (ignorowane w lossie)
        pad_id = self.processor.tokenizer.pad_token_id
        labels = torch.where(labels == pad_id, torch.tensor(-100), labels)

        return {"pixel_values": pixel_values, "labels": labels}

def main():
    train_items = load_jsonl("data/local_donut/train.jsonl")

    processor = DonutProcessor.from_pretrained(BASE)
    model = VisionEncoderDecoderModel.from_pretrained(BASE)

    # --- KLUCZOWE: tokeny w configu ---
    tok = processor.tokenizer
    # pad_token fallback = eos, jeśli brak
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token

    model.config.eos_token_id = tok.eos_token_id
    model.config.pad_token_id = tok.pad_token_id

    # decoder_start_token_id: preferuj bos, potem "<s>", potem eos
    dsid = getattr(tok, "bos_token_id", None)
    if dsid is None:
        try:
            dsid = tok.convert_tokens_to_ids("<s>")
            if dsid is None or dsid == tok.unk_token_id:
                raise ValueError
        except Exception:
            dsid = tok.eos_token_id
    model.config.decoder_start_token_id = dsid

    model.config.max_length = MAXLEN

    print(f"[cfg] base={BASE} out={OUT} train={len(train_items)} bf16={bf16} fp16={fp16} maxlen={MAXLEN} dsid={model.config.decoder_start_token_id}")

    ds_train = LocalDonutDS(train_items, processor, MAXLEN)

    args = TrainingArguments(
        output_dir=OUT,
        per_device_train_batch_size=BATCH,
        gradient_accumulation_steps=GA,
        learning_rate=LR,
        num_train_epochs=EPOCHS,
        logging_steps=5,
        save_strategy="no",
        bf16=bf16,
        fp16=(fp16 if not bf16 else False),
        remove_unused_columns=False,
    )

    trainer = Trainer(
        model=model,
        args=args,
        tokenizer=processor,  # ok mimo ostrzeżenia
        train_dataset=ds_train,
    )

    trainer.train()
    Path(OUT).mkdir(parents=True, exist_ok=True)
    model.save_pretrained(OUT)
    processor.save_pretrained(OUT)
    print(f"[done] saved to {OUT}")

if __name__ == "__main__":
    main()
