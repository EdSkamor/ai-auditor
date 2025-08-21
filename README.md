# AI Audytor

Lokalny system oparty o LLaMA 3 do analizy i generowania raportów audytorskich. Wszystkie dane przetwarzane są lokalnie – bez chmury, bez ryzyka.

## ✨ Funkcje

- 🔍 Wczytywanie szablonów MCP (Modular Context Prompt)
- 🧠 Lokalna inferencja z użyciem LLaMA3
- 🧾 Generowanie fragmentów raportu
- 🔒 Działa offline, dane nie wychodzą poza urządzenie

## 🛠️ Użycie

```bash
python3 inference/main.py# AI-Audytor

— Zobacz też: [docs/QUICKSTART.md](docs/QUICKSTART.md)

- Fine-tuning Donut: zobacz docs/FINETUNE.md

- **Fallback walidacji (ANYWHERE ≤1
- **Modele na Hugging Face**: zobacz [docs/HF_MODEL.md](docs/HF_MODEL.md)

- **Fallback „ANYWHERE ≤1
- ANYWHERE – wyniki bieżącego uruchomienia: [docs/ANYWHERE_RESULTS.md](docs/ANYWHERE_RESULTS.md)

### Szybka walidacja (strict / ANYWHERE ≤1%)
> Model z HF (private): `export DONUT_MODEL=SKamor/ai-audytor-donut-local`
> Lokalny model: nie ustawiaj `DONUT_MODEL`

```bash
# KOSZTY
scripts/validate2.sh koszty strict
scripts/validate2.sh koszty anywhere1p   # z post-procesem ANYWHERE ≤1%

# PRZYCHODY
scripts/validate2.sh przychody strict
scripts/validate2.sh przychody anywhere1p
