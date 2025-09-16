#!/bin/bash

# Test script for Docker Compose setup
echo "🐳 Testing AI Auditor Docker Setup"

# Build services
echo "📦 Building Docker images..."
docker compose build

# Start services
echo "🚀 Starting services..."
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Test AI service
echo "🤖 Testing AI service (port 8001)..."
AI_STATUS=$(curl -s http://localhost:8001/healthz)
echo "AI Health: $AI_STATUS"

# Test UI service  
echo "🖥️ Testing UI service (port 8501)..."
UI_STATUS=$(curl -s http://localhost:8501/_stcore/health)
echo "UI Health: $UI_STATUS"

# Test analyze endpoint
echo "🔍 Testing analyze endpoint..."
ANALYZE_RESPONSE=$(curl -s -X POST http://localhost:8001/analyze \
  -H "Content-Type: application/json" \
  -u "user:TwojPIN123!" \
  -d '{"prompt": "test", "max_new_tokens": 100}')
echo "Analyze Response: $ANALYZE_RESPONSE"

# Check if both services are healthy
if [[ "$AI_STATUS" == *"healthy"* ]] && [[ "$UI_STATUS" == "ok" ]]; then
    echo "✅ All services are healthy!"
    echo "🌐 UI available at: http://localhost:8501"
    echo "🔌 AI API available at: http://localhost:8001"
else
    echo "❌ Some services are not healthy"
    echo "AI Status: $AI_STATUS"
    echo "UI Status: $UI_STATUS"
fi

# Show running containers
echo "📋 Running containers:"
docker compose ps

