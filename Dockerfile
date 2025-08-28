# syntax=docker/dockerfile:1
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
RUN python -m pip install --upgrade pip wheel setuptools && \
    ( [ -f requirements.txt ] && pip install -r requirements.txt || true ) && \
    pip install "streamlit>=1.32" "pandas>=2.0" "matplotlib>=3.8" && \
    (pip install "llama-cpp-python>=0.3" --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu || true)
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD ["curl","-fsS","http://localhost:8501/healthz"]
ENTRYPOINT ["streamlit","run","app/Home.py","--server.port=8501","--server.address=0.0.0.0"]
