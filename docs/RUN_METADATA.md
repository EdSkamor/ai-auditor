# run_metadata.json — opis pól

Zapisujemy metadane z przebiegu audytu:

- `generated_at` – timestamp generacji pliku.
- `run_dir` – katalog przebiegu w `web_runs/...`.
- `git.branch`, `git.commit` – kontekst repozytorium.
- `params` – kluczowe parametry uruchomienia (np. `amount_tol`, `tiebreak_weight_fname`, `tiebreak_min_seller`).
- `kpi` – metryki z `verdicts_summary.json` + licznik wierszy z `All_invoices.csv`:
  - `liczba_pdf_koszty`, `liczba_pozycji_koszty`
  - `niezgodnosci` (podział: numer/data/netto)
  - `pdf_count_index` (liczba zindeksowanych plików PDF)

> Plik jest dołączany do paczki ZIP (pack_run) i trafi do Sphinx (Słownik/KPI).
