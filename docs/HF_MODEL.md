# Modele Donut na Hugging Face (private)

**Repozytoria:**
- Lokalny FT (PL): `SKamor/ai-audytor-donut-local`
- Demo FT (global): `SKamor/ai-audytor-donut-ft`

> Repozytoria są **prywatne**. Wymagany token HF (co najmniej Read do użycia, Write do publikacji).

## Użycie w CLI (nasz pipeline)
```bash
hf auth login   # lub: HF_TOKEN=*** hf auth login --token "$HF_TOKEN"
export DONUT_MODEL=SKamor/ai-audytor-donut-local
export USE_DONUT=1
python3 scripts/validate_cli_flex.py <arkusz.xlsx> <katalog_z_pdfami> out.csv
```

## Użycie programistyczne (Python)
```python
from transformers import DonutProcessor, VisionEncoderDecoderModel
repo = "SKamor/ai-audytor-donut-local"
proc  = DonutProcessor.from_pretrained(repo)
model = VisionEncoderDecoderModel.from_pretrained(repo)
# ...wczytaj obraz i generuj/parsuj jak w services/extract_ai_donut.py
```

## Integracja z bazą / usługą
- Backend ładuje nazwę repo z env `DONUT_MODEL` (np. `SKamor/ai-audytor-donut-local`).
- Wersje modeli trzymamy na HF; **nie commitujemy wag do GitHub**.
- Walidacja PDF↔arkusz działa tak samo dla repo z HF i katalogu lokalnego `models/...`.

## Bezpieczeństwo
- **Token HF**: fine-grained; nadaj tylko `Read` (użycie) lub `Write` (publikacja). Rotuj okresowo.
- **Dane**: nie wypychamy `data/`, `analysis/`, `train_logs/`, `models/` do Git — pilnuje `.gitignore`.
- **Dostęp**: repo HF jest `private`; dodawaj użytkowników/org tylko według potrzeby.
- **Logi**: unikamy logowania treści faktur; jeśli trzeba, maskujemy wartości/pola w logach.
- **Retencja**: artefakty treningowe (ckpt, optimizer) zostają wyłącznie na HF/private.

## FAQ
- **Czy wrzucać przetrenowane modele do GitHub?** Nie. Modele trzymamy na HF (private). GitHub jest tylko na kod i dokumentację.

## Parzystość wyników (HF ↔ LOCAL)

Walidacje na prywatnym repozytorium HF i na modelu lokalnym dały identyczne wyniki:
- **Koszty — HF vs LOCAL parity: ✅ TAK**
- **Przychody — HF vs LOCAL parity: ✅ TAK**

To oznacza, że możemy bezpiecznie używać modelu z HF w środowiskach produkcyjnych/CI.

### Jak użyć modelu z HF w naszej walidacji

> Wymagane: zalogowany token HF z uprawnieniem **Model: Read**.

```bash
# logowanie (jednorazowo na host)
hf auth login   # lub: HF_TOKEN=*** hf auth login --token "$HF_TOKEN"

# zmienne środowiskowe
export DONUT_MODEL="SKamor/ai-audytor-donut-local"
export USE_DONUT=1

# uruchom walidację (CPU)
CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=4 \
python3 scripts/validate_cli_flex.py /ścieżka/do/arkusza.xlsx /ścieżka/do/Faktur out.csv
