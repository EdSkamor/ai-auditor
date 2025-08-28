# QUICKSTART – AI-Audytor

## CPU via Docker (zalecane)
1) `cp .env.sample .env.local`
2) `docker compose up --build`
3) UI: `http://localhost:8585`

## GPU (opcjonalnie)
- Kontener:

docker build -f Dockerfile.gpu -t ai-auditor:gpu .
docker run --gpus all --rm -p 8585:8501 --env-file .env.local ai-auditor:gpu

- Host (venv):

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-ci.txt
pip install "llama-cpp-python>=0.3" --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cuBLAS


./scripts/ui_restart.sh


## Funkcje
- **🧾 Walidacja:** filtry + donut + liczniki + link do PDF (1 wiersz) → eksport.
- **📋 Przegląd:** multiselect → Zatwierdź/Odrzuć (CSV w `data/decisions/`) → eksport „po decyzjach”.
- **Chat:** lokalny LLM `.gguf` (llama-cpp-python, bez chmury).

## Zalety / wady
**+ lokalnie, bez chmury**, **+ proste CSV-in/out**, **+ Docker/Compose**
**− CPU wolniejsze**, **− decyzje w CSV (dla multi-user zalecana DB)**, **− brak OCR PDF (do rozbudowy)**

## Konfiguracja (.env.local)

LLM_GGUF="/app/models/twoj_model.gguf"
KOSZTY_FACT="/app/data/faktury/koszty"
PRZYCHODY_FACT="/app/data/faktury/przychody"
