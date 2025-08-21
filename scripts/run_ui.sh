#!/usr/bin/env bash
pkill -f "streamlit run" 2>/dev/null || true
exec streamlit run app/Chat.py --server.port 8501 --server.headless=true
