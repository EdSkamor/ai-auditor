# AI Auditor

Production-ready AI Auditor system for invoice validation and audit support. All data processing is done locally – no cloud, no risk.

## ✨ Features

### ✅ Production Ready (Level 200)
- 🔍 **PDF↔POP Validation** with deterministic tie-breaker logic
- 📊 **Bulk Processing** - handles 10s-1000s PDFs efficiently
- 🏗️ **Complete Audit Pipeline** - index → match → export
- 📈 **Professional Excel Reports** with formulas and formatting
- 🛡️ **Enterprise Security** - on-premise, no data leakage
- 🧪 **WSAD+TEST Methodology** - comprehensive test suite
- ⚡ **High Performance** - optimized for production workloads

### 🔄 In Development
- 🧠 **Local AI Inference** using LLaMA3 with LoRA support
- 📊 **OCR Database** with sample enrichment capabilities
- 🏢 **KRS + Whitelist Integration** for company data enrichment
- 🌐 **Streamlit Web Panel** (minimalistic, functional)
- 📚 **Sphinx Documentation** + ready-made runtime package

## 🛠️ Installation

### Prerequisites
- Python 3.12+
- NVIDIA GPU (RTX 4090 recommended)
- Linux/Ubuntu (tested on Linux Mint 22.1)

### Quick Start
```bash
# Clone repository
git clone https://github.com/EdSkamor/ai-auditor.git
cd ai-auditor

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run tests
pytest

# Start web server
uvicorn server:app --reload --host 0.0.0.0 --port 8001

## 🚀 How to run on host

For production deployment and testing:

```bash
# Terminal #1 - Setup and health checks
bash scripts/dev/host_setup.sh

# Terminal #2 - Cloudflare tunnel (keep open)
bash scripts/dev/host_tunnel.sh
# Copy the printed TUN=... URL

# Terminal #1 - Run tests
bash scripts/dev/host_tests.sh
# Use TUN as AI_API_BASE in Streamlit Cloud
```

### Understanding TUN (Tunnel URL)

**TUN** is the ephemeral Cloudflare tunnel URL that exposes your local AI service to the internet. It looks like:
```
TUN=https://abc123-def456.trycloudflare.com
```

**Important**: This URL changes every time you restart the tunnel, so you need to update it in Streamlit Cloud each time.

### Extracting TUN from logs

If you need to get the tunnel URL manually:
```bash
# Extract TUN from cloudflared log
TUN=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflared.log | tail -1)
echo "TUN=$TUN"
```

### Deployment Checklist

✅ **AI Health** → Local service running on port 8001
```bash
curl -s http://127.0.0.1:8001/healthz
# Should return: {"status":"healthy","ready":true}
```

✅ **Tunnel** → Cloudflare tunnel active and accessible
```bash
curl -s https://$TUN/healthz
# Should return: {"status":"healthy","ready":true}
```

✅ **Streamlit Cloud** → Environment variable set
- Go to Streamlit Cloud dashboard
- Set `AI_API_BASE` to your tunnel URL: `https://$TUN`
- Deploy/restart the app

### Co to jest TUN?

**TUN** to efemeryczny adres tunelu Cloudflare (np. `https://abc123.trycloudflare.com`) kierujący ruch z Internetu do lokalnego AI (127.0.0.1:8001).

Uruchom:
```bash
scripts/dev/host_tunnel.sh
```

a potem ustaw w Streamlit Cloud:
```bash
AI_API_BASE=<TUN>
```

### Jak uruchomić na hoście (3 zakładki terminala)

**Zakładka #1 – setup i start:**
```bash
bash scripts/dev/host_setup.sh
```

**Zakładka #2 – tunel (zostaw otwartą):**
```bash
bash scripts/dev/host_tunnel.sh
```

**Zakładka #1 – testy + raport:**
```bash
bash scripts/dev/host_tests.sh
bash scripts/dev/host_write_report.sh
```

### Prerequisites for host deployment:
- Docker and Docker Compose installed
- Cloudflared installed (`cloudflared` command available)
- Ports 8001 and 8501 available on host
```

## 🚀 Usage

### CLI Commands

```bash
# Demo validation (single file)
ai-auditor validate --demo --file invoice.pdf --pop-file pop_data.xlsx

# Bulk validation (complete audit pipeline)
ai-auditor validate --bulk --input-dir ./pdfs --pop-file pop_data.xlsx --output-dir ./results

# Advanced validation with tie-breaker settings
ai-auditor validate --bulk --input-dir ./pdfs --pop-file pop_data.xlsx \
  --tiebreak-weight-fname 0.7 --tiebreak-min-seller 0.4 --amount-tol 0.01

# OCR sampling
ai-auditor ocr-sample --input invoice.pdf --sample-size 10

# Data enrichment
ai-auditor enrich-data --input companies.csv --krs --whitelist

# Risk table generation
ai-auditor generate-risk-table --data financial_data.xlsx --output risk_table.xlsx

# Build documentation
ai-auditor build-docs --html --pdf --clean
```

### Web Interface
Open http://127.0.0.1:8000/ for the web interface.

### API Endpoints
- `GET /healthz` - Health check
- `POST /analyze` - Text analysis
- `POST /analyze-file` - File analysis

## 🏗️ Architecture

```
ai-auditor/
├── core/                 # Core functionality
│   ├── exceptions.py     # Custom exceptions
│   ├── model_interface.py # Unified model interface
│   ├── prompt_generator.py # MCP template handling
│   └── data_processing.py # Data ingestion & analysis
├── cli/                  # Command-line interfaces
│   ├── base.py          # Base CLI framework
│   ├── validate.py      # Validation CLI
│   ├── ocr_sample.py    # OCR sampling CLI
│   ├── enrich_data.py   # Data enrichment CLI
│   ├── generate_risk_table.py # Risk table CLI
│   └── build_docs.py    # Documentation CLI
├── tests/               # Test suite
├── scripts/             # WSAD test scripts
├── docs/                # Sphinx documentation
└── web/                 # Web interface
```

## 🧪 Testing

### WSAD+TEST Methodology
Each feature has its own test script in `scripts/`:

```bash
# Complete smoke test suite
python3 scripts/smoke_all.py

# Performance test (200 PDFs)
python3 scripts/smoke_perf_200.py

# Tie-breaker A/B testing
python3 scripts/smoke_tiebreak_ab.py

# Validation tests
python3 scripts/test_validation_demo.py
python3 scripts/test_validation_bulk.py

# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=cli
```

### Test Categories
- **Smoke Tests**: Complete functionality verification
- **Performance Tests**: Load and stress testing (200+ PDFs)
- **A/B Tests**: Tie-breaker algorithm validation
- **Unit Tests**: Individual function testing
- **Integration Tests**: End-to-end workflow testing
- **Security Tests**: Input validation and edge cases

## 📚 Documentation

- [Quick Start Guide](docs/QUICKSTART.md)
- [API Documentation](docs/API.md)
- [User Guide](docs/USER_GUIDE.md)
- [Configuration](docs/CONFIG.md)
- [Deployment](docs/DEPLOYMENT.md)

## 🔧 Configuration

### Environment Variables
```bash
export AIAUDITOR_DEBUG=true
export AIAUDITOR_MAX_FILE_MB=50
export AIAUDITOR_ALLOW_ORIGINS="http://localhost:3000,http://localhost:8000"
export TRANSFORMERS_VERBOSITY=error
```

### Model Configuration
The system supports multiple model backends:
- **HuggingFace**: LLaMA3 with LoRA adapters
- **llama.cpp**: Local GGUF models
- **Mock**: For testing and development

## 🚀 Deployment

### Production Setup
```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3-venv build-essential

# Install application
pip install -e .

# Configure systemd service
sudo cp scripts/ai-auditor.service /etc/systemd/system/
sudo systemctl enable ai-auditor
sudo systemctl start ai-auditor

# Configure Nginx
sudo cp scripts/nginx.conf /etc/nginx/sites-available/ai-auditor
sudo ln -s /etc/nginx/sites-available/ai-auditor /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

## 📄 License

Apache-2.0 License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -e ".[dev,docs]"

# Install pre-commit hooks
pre-commit install

# Run code formatting
black .
isort .

# Run linting
flake8
mypy .

# Build documentation
sphinx-build -b html docs docs/_build/html
```

## 🌐 Deploy on Streamlit Cloud

### Prerequisites
- Cloudflare tunnel set up for AI service
- Streamlit Cloud account

### Configuration
1. **Set AI_API_BASE environment variable** in Streamlit Cloud:
   ```
   AI_API_BASE=https://your-tunnel-url.trycloudflare.com
   ```

2. **Deploy to Streamlit Cloud**:
   - Connect your GitHub repository
   - Set environment variables in Streamlit Cloud dashboard
   - Deploy the `streamlit_app.py` file

### Health Check Commands
```bash
# Check AI service health
curl http://127.0.0.1:8001/healthz
# Expected: {"status":"healthy","ready":true}

# Check UI service health
curl http://127.0.0.1:8501/_stcore/health
# Expected: ok
```

### Troubleshooting
```bash
# Check container status
docker compose ps

# View AI service logs
docker compose logs -n 200 ai

# View UI service logs
docker compose logs -n 200 ui

# Restart services
docker compose down
docker compose up -d
```

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in `docs/`
- Review the test scripts in `scripts/`

---

**Note**: This is a production system designed for financial auditing. Ensure proper testing and validation before use in production environments.
