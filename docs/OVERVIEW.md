# AI Auditor — Overview
- Cel: szybka analiza ryzyk finansowych i danych księgowych (CSV/XLSX, wkrótce PDF).
- Model: LLaMA3 8B Instruct + LoRA (`outputs/lora-auditor`), 4-bit (bitsandbytes).
- Backend: FastAPI (`/analyze`, `/analyze-file`, `/healthz`), prosty frontend w `web/`.
- Prywatność: dane lokalne w `data/` (poza gitem), brak zapisu uploadów domyślnie.
- Deploy: systemd + Nginx (patrz QUICKSTART).
