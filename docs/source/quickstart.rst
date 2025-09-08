Szybki start
============

Ten przewodnik pomoże Ci szybko rozpocząć pracę z AI Auditor.

Instalacja
----------

1. **Sklonuj repozytorium**::

   git clone <repository-url>
   cd ai-auditor

2. **Utwórz środowisko wirtualne**::

   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # lub
   venv\Scripts\activate     # Windows

3. **Zainstaluj zależności**::

   pip install -r requirements.txt

4. **Zainstaluj pakiet**::

   pip install -e .

Pierwszy audyt
--------------

1. **Przygotuj dane testowe**::

   python scripts/setup_local_test.py

2. **Uruchom interfejs webowy**::

   streamlit run streamlit_app.py

3. **Otwórz przeglądarkę**::
   
   Przejdź do http://localhost:8501

4. **Wykonaj audyt**:
   
   - Prześlij plik PDF z fakturą
   - Wybierz plik POP (dane populacji)
   - Kliknij "Uruchom audyt"
   - Pobierz wyniki

Alternatywnie - z linii komend
-------------------------------

1. **Audyt pojedynczej faktury**::

   ai-auditor validate --file faktura.pdf --pop-file dane_pop.csv --output-dir wyniki/

2. **Audyt wsadowy**::

   ai-auditor validate --input-dir faktury/ --pop-file dane_pop.csv --output-dir wyniki/

3. **Test OCR**::

   ai-auditor ocr-sample --input-dir faktury/ --sample-size 5 --engine tesseract

4. **Wzbogacenie danych KRS**::

   ai-auditor enrich-data --input-file kontrahenci.csv --output-file kontrahenci_wzbogaceni.csv

5. **Generowanie raportu ryzyka**::

   ai-auditor generate-risk-table --data dane_audytu.json --output raport_ryzyka.xlsx

Testowanie systemu
------------------

Uruchom kompletny test systemu::

   python scripts/smoke_all.py

Testy wydajnościowe::

   python scripts/smoke_perf_200.py

Test A/B tie-breakera::

   python scripts/smoke_tiebreak_ab.py

Konfiguracja
------------

1. **Plik konfiguracyjny** (opcjonalny)::

   # config.yaml
   krs:
     api_key: "your-api-key"
     cache_ttl_hours: 24
   
   ocr:
     engine: "tesseract"
     language: "pol"
     gpu_enabled: true
   
   ai_assistant:
     embedding_model: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
     llm_model: "microsoft/DialoGPT-medium"

2. **Użyj konfiguracji**::

   ai-auditor validate --config config.yaml --file faktura.pdf --pop-file dane_pop.csv

Struktura wyników
-----------------

Po wykonaniu audytu otrzymasz:

* **All_invoices.csv** - Wszystkie przetworzone faktury
* **verdicts.jsonl** - Szczegółowe wyniki dopasowań
* **verdicts_summary.json** - Podsumowanie audytu
* **Audyt_koncowy.xlsx** - Kompletny raport Excel
* **verdicts_top50_mismatches.csv** - Top 50 niezgodności

Przykład struktury katalogu wyników::

   wyniki/
   ├── All_invoices.csv
   ├── verdicts.jsonl
   ├── verdicts_summary.json
   ├── Audyt_koncowy.xlsx
   ├── verdicts_top50_mismatches.csv
   └── logs/
       └── audit_2024-01-15_10-30-00.log

Następne kroki
--------------

* :doc:`user_guide/index` - Pełny przewodnik użytkownika
* :doc:`api/index` - Dokumentacja API
* :doc:`howto/index` - Przewodniki krok po kroku
* :doc:`architecture/index` - Architektura systemu

Rozwiązywanie problemów
-----------------------

Jeśli napotkasz problemy:

1. **Sprawdź logi**::

   tail -f logs/audit_*.log

2. **Uruchom testy diagnostyczne**::

   python scripts/test_validation_demo.py
   python scripts/test_ocr.py
   python scripts/test_krs_integration.py

3. **Sprawdź zależności**::

   pip check

4. **Zobacz sekcję** :doc:`troubleshooting` dla typowych problemów.



