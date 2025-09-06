Rozwiązywanie problemów
=======================

Ten rozdział zawiera rozwiązania typowych problemów z AI Auditor.

Problemy z instalacją
---------------------

Problem: "No module named 'torch'"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objawy**::
   
   ImportError: No module named 'torch'

**Rozwiązanie**::

   pip install torch torchvision torchaudio

**Dla RTX 4090**::

   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

Problem: "Tesseract not found"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objawy**::
   
   TesseractNotFoundError: tesseract is not installed or it's not in your PATH

**Rozwiązanie**:

**Ubuntu/Debian**::

   sudo apt-get install tesseract-ocr tesseract-ocr-pol

**macOS**::

   brew install tesseract tesseract-lang

**Windows**::
   
   # Pobierz z: https://github.com/UB-Mannheim/tesseract/wiki
   # Dodaj do PATH: C:\Program Files\Tesseract-OCR

Problem: "CUDA out of memory"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objawy**::
   
   RuntimeError: CUDA out of memory

**Rozwiązanie**::

   # Zmniejsz batch size
   export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"
   
   # Lub użyj CPU
   export CUDA_VISIBLE_DEVICES=""

Problemy z walidacją
--------------------

Problem: "No matching invoices found"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objawy**::
   
   Wszystkie faktury mają status "brak dopasowania"

**Rozwiązanie**:

1. **Sprawdź format danych POP**::
   
   # Sprawdź nagłówki kolumn
   head -1 dane_pop.csv
   
   # Sprawdź format dat
   head -5 dane_pop.csv

2. **Dostosuj tolerancję kwot**::
   
   ai-auditor validate --amount-tol 0.01 --file faktura.pdf --pop-file dane_pop.csv

3. **Sprawdź tie-breaker**::
   
   ai-auditor validate --tiebreak-weight-fname 0.8 --tiebreak-min-seller 0.4

Problem: "Invalid date format"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objawy**::
   
   ValueError: time data '15.01.2024' does not match format '%Y-%m-%d'

**Rozwiązanie**:

1. **Sprawdź format dat w POP**::
   
   # Konwertuj daty do formatu YYYY-MM-DD
   # 15.01.2024 -> 2024-01-15

2. **Użyj narzędzia konwersji**::
   
   python scripts/convert_dates.py --input dane_pop.csv --output dane_pop_fixed.csv

Problem: "Amount parsing failed"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objawy**::
   
   ValueError: could not convert string to float: '1 234,56'

**Rozwiązanie**:

1. **Sprawdź separator dziesiętny**::
   
   # Użyj kropki jako separatora dziesiętnego
   # 1 234,56 -> 1234.56

2. **Sprawdź separator tysięcy**::
   
   # Usuń spacje z separatorów tysięcy
   # 1 234 567,89 -> 1234567.89

Problemy z OCR
--------------

Problem: "OCR confidence too low"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objawy**::
   
   OCR confidence: 0.3 (below threshold 0.7)

**Rozwiązanie**:

1. **Obniż próg pewności**::
   
   ai-auditor ocr-sample --confidence-threshold 0.5

2. **Użyj innego silnika OCR**::
   
   ai-auditor ocr-sample --engine easyocr

3. **Sprawdź jakość obrazu**::
   
   # Upewnij się, że PDF ma dobrą rozdzielczość
   # Minimum 300 DPI dla tekstu

Problem: "OCR engine not available"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objawy**::
   
   ImportError: No module named 'easyocr'

**Rozwiązanie**::

   # Zainstaluj EasyOCR
   pip install easyocr
   
   # Lub PaddleOCR
   pip install paddlepaddle paddleocr

Problemy z integracjami
-----------------------

Problem: "KRS API rate limit exceeded"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objawy**::
   
   HTTPError: 429 Too Many Requests

**Rozwiązanie**:

1. **Zwiększ opóźnienie między żądaniami**::
   
   # W config.yaml
   krs:
     rate_limit_delay: 1.0  # 1 sekunda

2. **Użyj cache**::
   
   # Cache jest włączony domyślnie
   # Sprawdź katalog: ~/.ai-auditor/krs_cache

Problem: "VAT whitelist API key invalid"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objawy**::
   
   HTTPError: 401 Unauthorized

**Rozwiązanie**:

1. **Sprawdź klucz API**::
   
   # W config.yaml
   vat_whitelist:
     api_key: "your-valid-api-key"

2. **Sprawdź uprawnienia klucza**::
   
   # Upewnij się, że klucz ma dostęp do API VAT

Problemy z AI Assistant
-----------------------

Problem: "AI Assistant not responding"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objawy**::
   
   AI Assistant zwraca błędy lub nie odpowiada

**Rozwiązanie**:

1. **Sprawdź modele AI**::
   
   python -c "import torch; print(torch.cuda.is_available())"

2. **Sprawdź pamięć GPU**::
   
   nvidia-smi

3. **Użyj CPU fallback**::
   
   # W config.yaml
   ai_assistant:
     use_cpu: true

Problem: "Embedding model not found"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objawy**::
   
   OSError: Can't load tokenizer for 'sentence-transformers/...'

**Rozwiązanie**:

1. **Sprawdź połączenie internetowe**::
   
   # Modele są pobierane przy pierwszym użyciu

2. **Pobierz modele ręcznie**::
   
   python scripts/download_models.py

Problemy z wydajnością
----------------------

Problem: "Slow processing of large files"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objawy**::
   
   Przetwarzanie dużych plików trwa bardzo długo

**Rozwiązanie**:

1. **Zwiększ liczbę procesów**::
   
   ai-auditor validate --workers 4 --input-dir faktury/

2. **Użyj GPU dla OCR**::
   
   ai-auditor ocr-sample --gpu-enabled

3. **Zwiększ RAM**::
   
   # Użyj systemu z większą ilością RAM
   # Minimum 16GB dla dużych plików

Problem: "Memory usage too high"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objawy**::
   
   System używa zbyt dużo pamięci RAM

**Rozwiązanie**:

1. **Zmniejsz batch size**::
   
   # W config.yaml
   processing:
     batch_size: 10

2. **Użyj przetwarzania strumieniowego**::
   
   ai-auditor validate --streaming --input-dir faktury/

Problemy z logami
-----------------

Problem: "Logs not being created"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objawy**::
   
   Brak plików logów w katalogu logs/

**Rozwiązanie**:

1. **Sprawdź uprawnienia**::
   
   ls -la logs/
   chmod 755 logs/

2. **Sprawdź konfigurację logowania**::
   
   # W config.yaml
   logging:
     level: "INFO"
     file: "logs/audit.log"

Problem: "Log files too large"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objawy**::
   
   Pliki logów są bardzo duże

**Rozwiązanie**:

1. **Włącz rotację logów**::
   
   # W config.yaml
   logging:
     max_size: "10MB"
     backup_count: 5

2. **Wyczyść stare logi**::
   
   find logs/ -name "*.log" -mtime +30 -delete

Problemy z konfiguracją
-----------------------

Problem: "Configuration file not found"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objawy**::
   
   FileNotFoundError: config.yaml not found

**Rozwiązanie**:

1. **Utwórz plik konfiguracyjny**::
   
   cp config.yaml.example config.yaml

2. **Sprawdź ścieżkę**::
   
   ai-auditor validate --config /path/to/config.yaml

Problem: "Invalid configuration format"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objawy**::
   
   yaml.scanner.ScannerError: while scanning for the next token

**Rozwiązanie**:

1. **Sprawdź składnię YAML**::
   
   python -c "import yaml; yaml.safe_load(open('config.yaml'))"

2. **Użyj walidatora**::
   
   ai-auditor validate-config --config config.yaml

Debugowanie
-----------

Włączanie trybu debug
~~~~~~~~~~~~~~~~~~~~~

1. **CLI**::
   
   ai-auditor validate --debug --file faktura.pdf --pop-file dane_pop.csv

2. **Konfiguracja**::
   
   # W config.yaml
   logging:
     level: "DEBUG"

3. **Zmienna środowiskowa**::
   
   export AI_AUDITOR_LOG_LEVEL="DEBUG"

Sprawdzanie statusu systemu
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Test wszystkich komponentów**::
   
   python scripts/smoke_all.py

2. **Test wydajności**::
   
   python scripts/smoke_perf_200.py

3. **Test tie-breakera**::
   
   python scripts/smoke_tiebreak_ab.py

Zbieranie informacji diagnostycznych
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Informacje o systemie**::
   
   python scripts/system_info.py

2. **Informacje o GPU**::
   
   nvidia-smi

3. **Informacje o Python**::
   
   python --version
   pip list

Kontakt z pomocą techniczną
---------------------------

Przed kontaktem z pomocą techniczną:

1. **Zbierz informacje diagnostyczne**::
   
   python scripts/collect_diagnostics.py

2. **Sprawdź logi**::
   
   tail -100 logs/audit_*.log

3. **Uruchom testy**::
   
   python scripts/smoke_all.py

4. **Przygotuj opis problemu**:
   - Krok po kroku jak odtworzyć problem
   - Komunikat błędu
   - Wersja systemu
   - Konfiguracja

