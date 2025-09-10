# AI Auditor Makefile

.PHONY: run-backend run-frontend tunnel install test clean

# Install dependencies
install:
	pip install -r requirements.txt

# Run backend server
run-backend:
	uvicorn app.main:app --reload --port 8000

# Run frontend
run-frontend:
	streamlit run streamlit_app.py

# Start cloudflared tunnel
tunnel:
	bash scripts/tunnel_cloudflared.sh

# Run tests
test:
	python3 -m pytest tests/ -v

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Development setup
dev: install
	@echo "🚀 Starting AI Auditor development environment..."
	@echo "1. Run 'make run-backend' in one terminal"
	@echo "2. Run 'make tunnel' in another terminal"
	@echo "3. Run 'make run-frontend' in a third terminal"

# Health check
health:
	@echo "🏥 Health checking..."
	@curl -s http://localhost:8000/healthz || echo "❌ Backend not running"
	@curl -s http://localhost:8501/ >/dev/null && echo "✅ Frontend running" || echo "❌ Frontend not running"
