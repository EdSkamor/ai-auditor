# 🚀 AI Auditor - Quick Start Guide

## Prerequisites

- Docker and Docker Compose installed
- Cloudflared installed (`cloudflared` command available)
- Ports 8001 and 8501 available on host

## Quick Setup (3 terminals)

### Terminal #1: Setup and Health Checks
```bash
cd /home/romaks/ai_2/ai-auditor-clean
bash scripts/dev/host_setup.sh
```

### Terminal #2: Cloudflare Tunnel (keep open)
```bash
cd /home/romaks/ai_2/ai-auditor-clean
bash scripts/dev/host_tunnel.sh
# Copy the printed TUN=... URL
```

### Terminal #1: Run Tests
```bash
cd /home/romaks/ai_2/ai-auditor-clean
bash scripts/dev/host_tests.sh
```

## Understanding TUN (Tunnel URL)

**TUN** is the ephemeral Cloudflare tunnel URL that exposes your local AI service to the internet.

**Format**: `https://abc123-def456.trycloudflare.com`

**Important**: This URL changes every time you restart the tunnel!

### Extracting TUN from logs

```bash
# Extract TUN from cloudflared log
TUN=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflared.log | tail -1)
echo "TUN=$TUN"
```

## Deployment Checklist

### ✅ AI Health
Local service running on port 8001:
```bash
curl -s http://127.0.0.1:8001/healthz
# Expected: {"status":"healthy","ready":true}
```

### ✅ Tunnel
Cloudflare tunnel active and accessible:
```bash
curl -s https://$TUN/healthz
# Expected: {"status":"healthy","ready":true}
```

### ✅ Streamlit Cloud
Environment variable set:
1. Go to Streamlit Cloud dashboard
2. Set `AI_API_BASE` to your tunnel URL: `https://$TUN`
3. Deploy/restart the app

## Troubleshooting

### AI not healthy
```bash
# Check logs
docker compose logs ai

# Rebuild without cache
docker compose build ai --no-cache
docker compose up -d ai
```

### Port conflicts
```bash
# Kill processes on ports
fuser -k 8001/tcp 2>/dev/null || true
fuser -k 8501/tcp 2>/dev/null || true
```

### Quick diagnostics
```bash
bash scripts/dev/host_quick_diag.sh
```

## Expected Results

- **AI**: `{"status":"healthy","ready":true}` on localhost:8001
- **UI**: `ok` on localhost:8501
- **Tunnel**: Same health response via `https://$TUN`
- **CORS**: Preflight OPTIONS returns 200 with proper headers
- **Streamlit Cloud**: App connects to AI via tunnel

## Next Steps

1. Copy `TUN=...` from Terminal #2
2. Set `AI_API_BASE=https://$TUN` in Streamlit Cloud
3. Test the deployed app
4. Remember to update `AI_API_BASE` when tunnel restarts
