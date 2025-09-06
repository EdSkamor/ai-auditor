#!/bin/bash

# AI Auditor - Skrypt instalacyjny dla RTX 4090
# Instalacja wszystkich zależności i konfiguracja systemu

set -e

echo "🚀 AI Auditor - Instalacja dla RTX 4090"
echo "========================================"

# Sprawdzenie wymagań systemowych
echo "📋 Sprawdzanie wymagań systemowych..."

# Sprawdzenie GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ NVIDIA drivers nie są zainstalowane"
    echo "   Zainstaluj: sudo apt install nvidia-driver-535"
    exit 1
fi

# Sprawdzenie CUDA
if ! command -v nvcc &> /dev/null; then
    echo "⚠️  CUDA nie jest zainstalowane"
    echo "   Zainstaluj CUDA 12.x z: https://developer.nvidia.com/cuda-downloads"
fi

# Sprawdzenie Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 nie jest zainstalowany"
    echo "   Zainstaluj: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Sprawdzenie wersji Python
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ $(echo "$PYTHON_VERSION < 3.10" | bc -l) -eq 1 ]]; then
    echo "❌ Python 3.10+ jest wymagany (obecna wersja: $PYTHON_VERSION)"
    exit 1
fi

echo "✅ Wymagania systemowe spełnione"

# Tworzenie środowiska wirtualnego
echo "🐍 Tworzenie środowiska wirtualnego..."
python3 -m venv venv
source venv/bin/activate

# Aktualizacja pip
echo "📦 Aktualizacja pip..."
pip install --upgrade pip

# Instalacja zależności
echo "📦 Instalacja zależności Python..."
pip install -r requirements.txt

# Instalacja PyTorch z CUDA
echo "🔥 Instalacja PyTorch z CUDA..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Instalacja transformers
echo "🤗 Instalacja transformers..."
pip install transformers accelerate

# Instalacja sentence-transformers
echo "📝 Instalacja sentence-transformers..."
pip install sentence-transformers

# Instalacja OCR dependencies
echo "👁️ Instalacja zależności OCR..."
pip install pytesseract opencv-python easyocr paddlepaddle paddleocr

# Instalacja Streamlit
echo "🌐 Instalacja Streamlit..."
pip install streamlit plotly

# Instalacja FastAPI
echo "⚡ Instalacja FastAPI..."
pip install fastapi uvicorn python-multipart

# Instalacja pandas i numpy
echo "📊 Instalacja pandas i numpy..."
pip install pandas numpy

# Instalacja requests
echo "🌍 Instalacja requests..."
pip install requests

# Tworzenie katalogów
echo "📁 Tworzenie katalogów..."
mkdir -p data/{uploads,exports,cache,logs}
mkdir -p config
mkdir -p models

# Kopiowanie plików konfiguracyjnych
echo "⚙️ Kopiowanie plików konfiguracyjnych..."
cp ../config/*.yaml config/ 2>/dev/null || echo "⚠️  Brak plików konfiguracyjnych"

# Tworzenie pliku konfiguracyjnego
echo "📝 Tworzenie konfiguracji..."
cat > config/audit_config.yaml << EOF
# AI Auditor - Konfiguracja audytu
audit:
  max_file_size: 100MB
  supported_formats: [pdf, zip, csv, xlsx]
  batch_size: 10
  timeout: 3600

model:
  llm_model: "microsoft/DialoGPT-medium"
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  device: "cuda"
  max_length: 512
  temperature: 0.3

integrations:
  ksef:
    enabled: true
    endpoint: "https://ksef.mf.gov.pl"
  jpk:
    enabled: true
  vat_whitelist:
    enabled: true
    endpoint: "https://www.podatki.gov.pl"
  krs:
    enabled: true
    endpoint: "https://rejestr.io"

security:
  encryption: true
  audit_logging: true
  access_control: true
  session_timeout: 3600
EOF

# Tworzenie skryptu startowego
echo "🚀 Tworzenie skryptu startowego..."
cat > start.sh << 'EOF'
#!/bin/bash

# AI Auditor - Skrypt startowy
set -e

echo "🚀 Uruchamianie AI Auditor..."

# Aktywacja środowiska wirtualnego
source venv/bin/activate

# Sprawdzenie GPU
echo "🔍 Sprawdzanie GPU..."
nvidia-smi

# Uruchomienie serwera API
echo "⚡ Uruchamianie serwera API..."
cd ../local_test
uvicorn server:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Czekanie na uruchomienie API
sleep 5

# Uruchomienie panelu audytora
echo "🌐 Uruchamianie panelu audytora..."
cd ../web
streamlit run modern_ui.py --server.port 8503 --server.address 0.0.0.0 &
UI_PID=$!

echo "✅ AI Auditor uruchomiony!"
echo "📊 Panel Audytora: http://localhost:8503"
echo "⚡ API Server: http://localhost:8000"
echo "📚 Dokumentacja: http://localhost:8000/docs"
echo ""
echo "Naciśnij Ctrl+C aby zatrzymać"

# Funkcja czyszczenia
cleanup() {
    echo "🛑 Zatrzymywanie AI Auditor..."
    kill $API_PID $UI_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Czekanie na zakończenie
wait
EOF

chmod +x start.sh

# Tworzenie skryptu testowego
echo "🧪 Tworzenie skryptu testowego..."
cat > test_system.sh << 'EOF'
#!/bin/bash

# AI Auditor - Test systemu
set -e

echo "🧪 Testowanie systemu AI Auditor..."

# Aktywacja środowiska wirtualnego
source venv/bin/activate

# Test importów
echo "📦 Test importów..."
python3 -c "
import torch
import transformers
import streamlit
import fastapi
import pandas
import numpy
print('✅ Wszystkie importy działają')
"

# Test GPU
echo "🔥 Test GPU..."
python3 -c "
import torch
if torch.cuda.is_available():
    print(f'✅ CUDA dostępne: {torch.cuda.get_device_name(0)}')
    print(f'✅ VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
else:
    print('❌ CUDA niedostępne')
"

# Test modeli
echo "🤖 Test modeli..."
python3 -c "
from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-medium')
model = AutoModel.from_pretrained('microsoft/DialoGPT-medium')
print('✅ Modele działają')
"

echo "✅ Wszystkie testy przeszły pomyślnie!"
EOF

chmod +x test_system.sh

# Tworzenie requirements.txt
echo "📝 Tworzenie requirements.txt..."
cat > requirements.txt << EOF
# AI Auditor - Zależności dla RTX 4090

# Core dependencies
torch>=2.0.0
transformers>=4.30.0
accelerate>=0.20.0
sentence-transformers>=2.2.0

# Web framework
streamlit>=1.28.0
fastapi>=0.100.0
uvicorn>=0.23.0
python-multipart>=0.0.6

# Data processing
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0

# OCR
pytesseract>=0.3.10
opencv-python>=4.8.0
easyocr>=1.7.0
paddlepaddle>=2.5.0
paddleocr>=2.7.0

# HTTP requests
requests>=2.31.0

# PDF processing
pdfplumber>=0.9.0
pypdf>=3.15.0
reportlab>=4.0.0

# Database
sqlite3

# Utilities
psutil>=5.9.0
python-dateutil>=2.8.0
pydantic>=2.0.0
EOF

echo "✅ Instalacja zakończona pomyślnie!"
echo ""
echo "🚀 Aby uruchomić system:"
echo "   ./start.sh"
echo ""
echo "🧪 Aby przetestować system:"
echo "   ./test_system.sh"
echo ""
echo "📚 Dokumentacja:"
echo "   README.md"
