# QUICKSTART – AI-Audytor

## CPU via Docker
1) `cp .env.sample .env.local`
2) `docker compose up --build`
3) UI: `http://localhost:8585`

## Co potrafi
- 🧾 Walidacja: filtry + donut + liczniki + PDF (1 wiersz) → eksport.
- 📋 Przegląd: multiselect → Zatwierdź/Odrzuć (CSV w `data/decisions/`) → eksport „po decyzjach”.
- Chat: lokalny LLM `.gguf` (llama-cpp-python).

## Konfiguracja (.env.local)

LLM_GGUF="/app/models/twoj_model.gguf"
KOSZTY_FACT="/app/data/faktury/koszty"
PRZYCHODY_FACT="/app/data/faktury/przychody"
