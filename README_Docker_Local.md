# AI Auditor - Local-First Docker Setup

## Overview
Local-first architecture with Docker Compose. No cloud dependencies except Cursor.

## Services
- **AI Service**: FastAPI on port 8001 (`app.main:app`)
- **UI Service**: Streamlit on port 8501 (`streamlit_app.py`)

## Quick Start

### 1. Build and Start
```bash
docker compose build
docker compose up -d
```

### 2. Verify Services
```bash
# AI Health
curl http://localhost:8001/healthz

# UI Health  
curl http://localhost:8501/_stcore/health

# Run E2E Test
python test_e2e.py
```

### 3. Access Applications
- **UI**: http://localhost:8501
- **AI API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

## Configuration

### Environment Variables
- `AI_API_BASE`: AI service URL (default: http://127.0.0.1:8001)
- `BACKEND_URL`: Backend URL (default: http://127.0.0.1:8001)
- `BASIC_AUTH_USER`: API username (default: user)
- `BASIC_AUTH_PASS`: API password (default: TwojPIN123!)

### Volumes
- `pdfs/`: Input PDF files (read-only)
- `populacja/`: Population data (read-only)
- `outputs/`: Generated artifacts (read-write)
- `logs/`: Application logs (read-write)

## API Endpoints

### Health Check
```bash
GET /healthz
# Returns: {"status":"healthy","ready":true}
```

### Analysis
```bash
POST /analyze
# Auth: Basic (user:TwojPIN123!)
# Body: {"prompt": "analysis request", "max_new_tokens": 200}
```

## Architecture
- **Local-First**: All processing happens locally
- **No Cloud Dependencies**: Only Cursor as paid tool
- **Docker Compose**: Easy deployment and scaling
- **Health Checks**: Built-in service monitoring
- **Volume Mapping**: Persistent data storage

## Troubleshooting

### Port Conflicts
```bash
# Check what's using ports
lsof -i :8001
lsof -i :8501

# Stop services
docker compose down
```

### Service Logs
```bash
# View logs
docker compose logs ai
docker compose logs ui

# Follow logs
docker compose logs -f
```

### Reset Everything
```bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

## Development

### Local Development
```bash
# AI Service
python -c "from app.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8001)"

# UI Service
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```

### Testing
```bash
# Run E2E test
python test_e2e.py

# Run unit tests
python -m pytest tests/
```

## Security
- Non-root containers
- Basic Authentication for API
- CORS configuration
- Volume isolation
- Health check monitoring

