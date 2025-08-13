# Fine-tuning Donut — baza i procedura

**Model bazowy:** `naver-clova-ix/donut-base`
**Zbiór danych (demo):** `katanaml-org/invoices-donut-data-v1`
**Split (z logów):** train=425, val=50, test=26
**Cel:** szybka weryfikacja pipeline’u FT i inferencji „OCR-free” na fakturach.

> Zbiór demo zawiera międzynarodowe/anglojęzyczne szablony, różne od polskich (np. Inter Cars). FT na nim stabilizuje pipeline, ale **jakość na naszych fakturach** była neutralna → potrzebny **lokalny zbiór PL** i FT na nim.

## Jak uruchomiliśmy FT (GPU)
```bash
export DONUT_BASE=naver-clova-ix/donut-base
export DONUT_DS=katanaml-org/invoices-donut-data-v1
export DONUT_OUT=models/donut-auditor
export EPOCHS=6 BATCH=1 GA=16 LR=5e-5 MAX_LENGTH=768

nohup python -u scripts/train_donut_safe.py >> logs_donut_ft.txt 2>&1 & echo $! > donut_ft.pid
tail -f logs_donut_ft.txt
