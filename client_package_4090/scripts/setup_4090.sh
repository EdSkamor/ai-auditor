#!/bin/bash
# AI Auditor - RTX 4090 Setup Script

echo "🚀 Setting up AI Auditor for RTX 4090..."

# Check system requirements
echo "📋 Checking system requirements..."

# Check GPU
if ! nvidia-smi &> /dev/null; then
    echo "❌ NVIDIA GPU not detected. Please install NVIDIA drivers."
    exit 1
fi

# Check CUDA
if ! nvcc --version &> /dev/null; then
    echo "❌ CUDA not detected. Please install CUDA 12.x."
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ $(echo "$python_version < 3.10" | bc -l) -eq 1 ]]; then
    echo "❌ Python 3.10+ required. Found: $python_version"
    exit 1
fi

echo "✅ System requirements met"

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r web/requirements_web.txt

# Install AI dependencies
echo "🧠 Installing AI dependencies..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers accelerate bitsandbytes
pip install sentence-transformers chromadb
pip install paddlepaddle paddleocr

# Download models
echo "📥 Downloading AI models..."
python3 scripts/download_models.py

# Run tests
echo "🧪 Running tests..."
python3 scripts/smoke_all.py

echo "✅ Setup complete!"
echo "🚀 Start the system with: ./scripts/start_4090.sh"
