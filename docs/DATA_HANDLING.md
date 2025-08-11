# Przetwarzanie i bezpieczeństwo danych

- **Lokalne katalogi** (ignorowane przez git):
  - `data/incoming/` — pliki wejściowe
  - `data/processed/` — artefakty (opcjonalnie)
  - `data/samples/` — przykłady bez danych poufnych
- **Domyślnie** nie zapisujemy uploadów na dysk (`saved_to: null`).
- Limit rozmiaru uploadu: `AIAUDITOR_MAX_FILE_MB` (domyślnie 25 MB).
- Rekomendacje:
  - Nie commitować danych.
  - Ograniczyć CORS / dostęp sieciowy.
  - W razie potrzeby anonimizować dane i czyścić po analizie.
- Wykrywanie nagłówków: skan pierwszych 10 wierszy; wiersze powyżej → `prompts`.
