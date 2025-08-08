# AI Auditor — Quick Start (Demo)

**Sprawdzone na:** Linux Mint 22.1 (Mint bazuje na Ubuntu, więc komendy są identyczne jak dla Ubuntu).

Lokalny demo-serwis do analiz audytowych oparty o Llama 3 (HF) + opcjonalny adapter LoRA.

## Wymagania
- **Linux Mint (Ubuntu-based)**
- **Python 3 + venv**
- **GPU NVIDIA** + sterowniki (zalecane; projekt korzysta z 4-bit/bitsandbytes)
- Dostęp do modelu **meta-llama/Meta-Llama-3-8B-Instruct** na Hugging Face (lub podmień w kodzie na inny)

## Instalacja
```bash
# 1) zależności systemowe (venv + narzędzia budowania)
sudo apt update
sudo apt install -y python3-venv build-essential git

# 2) klon repo + wirtualne środowisko
git clone https://github.com/EdSkamor/ai-auditor.git
cd ai-audytor
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# 3) pip deps (API + inference)
pip install -r requirements.txt
```

> Jeśli potrzebujesz dostępu do modeli na HF:
> ```bash
> huggingface-cli login
> ```

## Uruchomienie
```bash
# mniej logów z transformers
export TRANSFORMERS_VERBOSITY=error

# dev-server z hot-reload
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Otwórz: **http://127.0.0.1:8000/** (konsola web)
Status: **http://127.0.0.1:8000/healthz**

### Test API (curl)
```bash
curl -s http://127.0.0.1:8000/healthz
# {"status":"ok"}

curl -s -X POST http://127.0.0.1:8000/analyze   -H 'Content-Type: application/json'   -d '{"prompt":"Spadek przychodów 40% r/r, dług 65%: wskaż 3–5 ryzyk i działania.","max_new_tokens":220,"do_sample":false}'
```

### LoRA (opcjonalnie)
Umieść pliki adaptera po trenowaniu:
```
outputs/lora-auditor/
  ├─ adapter_model.safetensors
  └─ adapter_config.json
```
Serwis sam spróbuje załadować adapter. Brak adaptera → jedzie model bazowy.

### Zmiana modelu
W pliku `model_hf_interface.py` zmień stałą:
```py
BASE = "meta-llama/Meta-Llama-3-8B-Instruct"
```

### Uwaga
- Przy `do_sample=false` biblioteka ignoruje `temperature/top_p` — to normalne.
- Ostrzeżenie o `attention_mask` można zignorować w demie.

## Zatrzymanie
```bash
# w terminalu z serwerem naciśnij CTRL+C
```
