Instalacja
==========

Wymagania systemowe
-------------------

Podstawowe wymagania
~~~~~~~~~~~~~~~~~~~~

* **Python**: 3.10, 3.11 lub 3.12
* **System operacyjny**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+
* **RAM**: Minimum 8GB (zalecane 16GB+)
* **Dysk**: 10GB wolnego miejsca
* **Internet**: Dostęp do internetu dla pobierania modeli AI

Wymagania dla RTX 4090
~~~~~~~~~~~~~~~~~~~~~~

* **GPU**: NVIDIA RTX 4090 (24GB VRAM)
* **CPU**: 8+ rdzeni
* **RAM**: 32GB+
* **Dysk**: 50GB+ (modele AI)
* **CUDA**: 12.x
* **System**: Linux x86_64 (Ubuntu 22.04 LTS zalecane)

Instalacja podstawowa
---------------------

1. **Sklonuj repozytorium**::

   git clone <repository-url>
   cd ai-auditor

2. **Utwórz środowisko wirtualne**::

   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # lub
   venv\Scripts\activate     # Windows

3. **Zaktualizuj pip**::

   pip install --upgrade pip

4. **Zainstaluj zależności**::

   pip install -r requirements.txt

5. **Zainstaluj pakiet w trybie deweloperskim**::

   pip install -e .

Instalacja dla RTX 4090
------------------------

1. **Zainstaluj CUDA 12.x**::

   # Ubuntu/Debian
   wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
   sudo dpkg -i cuda-keyring_1.0-1_all.deb
   sudo apt-get update
   sudo apt-get -y install cuda

2. **Zainstaluj PyTorch z obsługą CUDA**::

   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

3. **Zainstaluj pozostałe zależności**::

   pip install -r requirements.txt

4. **Pobierz modele AI**::

   python scripts/download_models.py

5. **Skonfiguruj lokalne AI**::

   python scripts/setup_local_ai.py

Instalacja zależności opcjonalnych
----------------------------------

OCR Engines
~~~~~~~~~~~

**Tesseract** (domyślny)::

   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr tesseract-ocr-pol

   # macOS
   brew install tesseract tesseract-lang

   # Windows
   # Pobierz z: https://github.com/UB-Mannheim/tesseract/wiki

**EasyOCR**::

   pip install easyocr

**PaddleOCR**::

   pip install paddlepaddle paddleocr

Machine Learning
~~~~~~~~~~~~~~~~

**PyTorch** (dla lokalnego AI)::

   # CPU only
   pip install torch torchvision torchaudio

   # CUDA 12.1
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

**Transformers**::

   pip install transformers accelerate bitsandbytes

**Sentence Transformers**::

   pip install sentence-transformers

Weryfikacja instalacji
----------------------

1. **Sprawdź instalację**::

   ai-auditor --help

2. **Uruchom testy**::

   python scripts/smoke_all.py

3. **Sprawdź komponenty**::

   python -c "import torch; print(f'PyTorch: {torch.__version__}')"
   python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
   python -c "import streamlit; print(f'Streamlit: {streamlit.__version__}')"

4. **Test GPU** (jeśli dostępne)::

   python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
   python -c "import torch; print(f'GPU count: {torch.cuda.device_count()}')"

Konfiguracja środowiska
-----------------------

1. **Zmienne środowiskowe** (opcjonalne)::

   export AI_AUDITOR_CACHE_DIR="/path/to/cache"
   export AI_AUDITOR_LOG_LEVEL="INFO"
   export AI_AUDITOR_CONFIG_FILE="/path/to/config.yaml"

2. **Plik konfiguracyjny** (opcjonalny)::

   # ~/.ai-auditor/config.yaml
   krs:
     api_key: "your-krs-api-key"
     cache_ttl_hours: 24
     rate_limit_delay: 0.5

   vat_whitelist:
     api_key: "your-vat-api-key"
     cache_ttl_hours: 12

   ocr:
     engine: "tesseract"
     language: "pol"
     gpu_enabled: true
     confidence_threshold: 0.7

   ai_assistant:
     embedding_model: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
     llm_model: "microsoft/DialoGPT-medium"
     max_tokens: 512
     temperature: 0.7

   risk_assessment:
     default_confidence_level: 0.95
     time_horizon_months: 12
     include_charts: true
     color_code: true

Rozwiązywanie problemów instalacji
----------------------------------

Problem: "No module named 'torch'"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Rozwiązanie**::

   pip install torch torchvision torchaudio

Problem: "CUDA out of memory"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Rozwiązanie**::

   # Zmniejsz batch size lub użyj CPU
   export CUDA_VISIBLE_DEVICES=""
   # lub
   export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"

Problem: "Tesseract not found"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Rozwiązanie**::

   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr

   # Dodaj do PATH (Windows)
   set PATH=%PATH%;C:\Program Files\Tesseract-OCR

Problem: "Permission denied"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Rozwiązanie**::

   # Użyj --user flag
   pip install --user -r requirements.txt

   # Lub zmień uprawnienia
   sudo chown -R $USER:$USER ~/.local

Problem: "Out of disk space"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Rozwiązanie**::

   # Wyczyść cache pip
   pip cache purge

   # Usuń nieużywane pakiety
   pip-autoremove -y

Aktualizacja
------------

1. **Aktualizuj kod**::

   git pull origin main

2. **Aktualizuj zależności**::

   pip install --upgrade -r requirements.txt

3. **Ponownie zainstaluj pakiet**::

   pip install -e .

4. **Uruchom testy**::

   python scripts/smoke_all.py

Odinstalowanie
--------------

1. **Dezaktywuj środowisko wirtualne**::

   deactivate

2. **Usuń katalog środowiska**::

   rm -rf venv

3. **Usuń cache** (opcjonalne)::

   rm -rf ~/.ai-auditor
   rm -rf ~/.cache/ai-auditor

4. **Usuń katalog projektu**::

   rm -rf ai-auditor

Docker (opcjonalne)
-------------------

1. **Zbuduj obraz**::

   docker build -t ai-auditor .

2. **Uruchom kontener**::

   docker run -p 8501:8501 -v $(pwd)/data:/app/data ai-auditor

3. **Z GPU support**::

   docker run --gpus all -p 8501:8501 -v $(pwd)/data:/app/data ai-auditor
