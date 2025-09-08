
# AI Auditor - System Requirements for RTX 4090

## 🖥️ Hardware Requirements

### Minimum
- **GPU**: NVIDIA RTX 4090 (24 GB VRAM)
- **CPU**: 8 cores, 3.0 GHz
- **RAM**: 32 GB DDR4
- **Storage**: 50 GB SSD free space
- **Network**: Gigabit Ethernet

### Recommended
- **GPU**: NVIDIA RTX 4090 (24 GB VRAM)
- **CPU**: 16 cores, 3.5 GHz
- **RAM**: 64 GB DDR4
- **Storage**: 100 GB NVMe SSD
- **Network**: 10 Gigabit Ethernet

## 🐧 Software Requirements

### Operating System
- **Linux**: Ubuntu 22.04 LTS (recommended)
- **Architecture**: x86_64
- **Kernel**: 5.15+ (for NVIDIA drivers)

### NVIDIA Stack
- **Driver**: 535+ (latest recommended)
- **CUDA**: 12.1+ (for PyTorch compatibility)
- **cuDNN**: 8.9+ (for deep learning)
- **TensorRT**: 8.6+ (for optimization)

### Python Environment
- **Python**: 3.10-3.12
- **pip**: 23.0+
- **venv**: Built-in virtual environment

## 📦 Dependencies

### Core Dependencies
```
fastapi>=0.111
uvicorn[standard]>=0.30
pandas>=2.2
numpy>=1.24
openpyxl>=3.1
pdfplumber>=0.11
pypdf>=5.0
rapidfuzz>=3.0
streamlit>=1.28
reportlab>=4.0
xlsxwriter>=3.1
```

### AI Dependencies
```
torch>=2.0
transformers>=4.30
accelerate>=0.20
bitsandbytes>=0.41
sentence-transformers>=2.2
chromadb>=0.4
paddlepaddle>=2.5.0
paddleocr>=2.7.0
```

### Development Dependencies
```
pytest>=7.4
black>=23.0
isort>=5.12
flake8>=6.0
mypy>=1.5
```

## 🧠 AI Models

### LLM Model
- **Model**: Llama-3-8B-Instruct
- **Size**: ~8 GB (4-bit quantized)
- **VRAM Usage**: ~8 GB
- **Speed**: Fast inference
- **Quality**: High

### Embedding Model
- **Model**: Multilingual MiniLM
- **Size**: ~100 MB
- **VRAM Usage**: ~100 MB
- **Languages**: Polish, English
- **Speed**: Very fast

### OCR Model
- **Model**: PaddleOCR
- **Size**: ~500 MB
- **VRAM Usage**: ~2 GB
- **Languages**: Polish, English
- **Speed**: GPU-accelerated

## 🔧 Installation Steps

### 1. System Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install NVIDIA drivers
sudo apt install nvidia-driver-535

# Install CUDA
wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run
sudo sh cuda_12.1.0_530.30.02_linux.run

# Install Python
sudo apt install python3.11 python3.11-venv python3.11-dev
```

### 2. AI Auditor Setup
```bash
# Clone repository
git clone <repository-url>
cd ai-auditor

# Run setup script
./scripts/setup_4090.sh
```

### 3. Verification
```bash
# Check GPU
nvidia-smi

# Check CUDA
nvcc --version

# Check Python
python3 --version

# Run tests
python3 scripts/smoke_all.py
```

## 🚀 Performance Tuning

### GPU Optimization
```bash
# Set GPU memory growth
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Enable mixed precision
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
```

### System Optimization
```bash
# Increase file limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize memory
echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf
```

## 🛡️ Security Configuration

### Firewall
```bash
# Allow local access only
sudo ufw allow from 192.168.0.0/16
sudo ufw allow from 10.0.0.0/8
sudo ufw deny 80
sudo ufw deny 443
```

### SSL/TLS
```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

## 📊 Monitoring

### System Monitoring
```bash
# GPU monitoring
watch -n 1 nvidia-smi

# System monitoring
htop
iotop
```

### Application Monitoring
```bash
# Log monitoring
tail -f logs/auditor.log

# Performance monitoring
python3 scripts/monitor_performance.py
```

## 🔧 Troubleshooting

### Common Issues
1. **CUDA out of memory**: Reduce batch size or enable gradient checkpointing
2. **Model loading fails**: Check disk space and permissions
3. **Slow inference**: Verify GPU utilization and model quantization
4. **Web interface not accessible**: Check firewall and port configuration

### Diagnostic Commands
```bash
# Check GPU status
nvidia-smi

# Check CUDA installation
nvcc --version

# Check Python packages
pip list | grep torch

# Check system resources
free -h
df -h
```

---

**Your RTX 4090 system is ready for AI Auditor!** 🚀
