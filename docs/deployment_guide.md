# AI Auditor - Przewodnik Wdrożenia

## 🚀 Wdrożenie Lokalne (RTX 4090)

### Wymagania Systemowe
- **GPU**: NVIDIA RTX 4090 (24 GB VRAM)
- **CPU**: 8 rdzeni (lub więcej)
- **RAM**: 32 GB+
- **Dysk**: ≥ 10 GB wolnego miejsca
- **OS**: Linux x86_64 (Ubuntu 22.04 LTS zalecane)
- **Sterowniki**: nvidia-driver + CUDA 12.x

### Instalacja
```bash
# 1. Klonowanie repozytorium
git clone <repository-url>
cd ai-auditor/client_package_4090

# 2. Instalacja zależności
./install.sh

# 3. Uruchomienie systemu
./start.sh
```

### Dostęp do Systemu
- **Panel Audytora**: http://localhost:8503
- **API Server**: http://localhost:8000
- **Dokumentacja API**: http://localhost:8000/docs

## 🌐 Wdrożenie z Cloudflare (Dla Klienta)

### Architektura
```
[Klient] ←→ [Cloudflare] ←→ [Twój Serwer Lokalny]
```

### Konfiguracja Cloudflare

#### 1. Dodanie Domeny
```bash
# W panelu Cloudflare
1. Dodaj domenę klienta (np. audit.client.com)
2. Skonfiguruj DNS A record → Twój IP
3. Włącz SSL/TLS (Full)
```

#### 2. Konfiguracja Tunnels
```bash
# Instalacja cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Konfiguracja tunnel
cloudflared tunnel login
cloudflared tunnel create ai-auditor
cloudflared tunnel route dns ai-auditor audit.client.com
```

#### 3. Konfiguracja Tunnel
```yaml
# ~/.cloudflared/config.yml
tunnel: <tunnel-id>
credentials-file: /home/user/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: audit.client.com
    service: http://localhost:8503
  - hostname: api.client.com
    service: http://localhost:8000
  - service: http_status:404
```

#### 4. Uruchomienie Tunnel
```bash
# Uruchomienie jako serwis
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

### Konfiguracja Bezpieczeństwa

#### 1. Access Control
```bash
# W panelu Cloudflare
1. Security → WAF
2. Dodaj reguły dla:
   - Rate limiting
   - Geo-blocking
   - Bot protection
```

#### 2. Authentication
```bash
# Cloudflare Access
1. Zero Trust → Access
2. Dodaj aplikację
3. Skonfiguruj authentication:
   - Email domain
   - MFA
   - Session timeout
```

## 🔧 Konfiguracja Systemu

### Pliki Konfiguracyjne

#### 1. audit_config.yaml
```yaml
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
```

#### 2. model_config.yaml
```yaml
llm:
  model_name: "microsoft/DialoGPT-medium"
  device: "cuda"
  max_length: 512
  temperature: 0.3
  do_sample: true

embedding:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  device: "cuda"
  max_seq_length: 512

ocr:
  engine: "tesseract"
  languages: ["pol", "eng"]
  preprocessing: true
```

#### 3. integrations.yaml
```yaml
ksef:
  enabled: true
  endpoint: "https://ksef.mf.gov.pl"
  timeout: 30
  retry_attempts: 3

jpk:
  enabled: true
  validation: true
  schemas_path: "./schemas/"

vat_whitelist:
  enabled: true
  endpoint: "https://www.podatki.gov.pl"
  cache_ttl: 3600

krs:
  enabled: true
  endpoint: "https://rejestr.io"
  api_key: "${KRS_API_KEY}"
```

### Zmienne Środowiskowe
```bash
# .env
AI_AUDITOR_DATA_DIR="/path/to/data"
AI_AUDITOR_CACHE_DIR="/path/to/cache"
AI_AUDITOR_LOG_LEVEL="INFO"
AI_AUDITOR_SECRET_KEY="your-secret-key"
KRS_API_KEY="your-krs-api-key"
```

## 📊 Monitoring i Logi

### Logi Systemowe
```bash
# Logi aplikacji
tail -f logs/ai-auditor.log

# Logi systemowe
journalctl -u ai-auditor -f

# Logi Cloudflare
cloudflared tunnel info ai-auditor
```

### Monitoring Zasobów
```bash
# GPU monitoring
nvidia-smi -l 1

# System monitoring
htop
iotop
```

### Alerty
```bash
# Konfiguracja alertów
# /etc/systemd/system/ai-auditor-monitor.service
[Unit]
Description=AI Auditor Monitor
After=network.target

[Service]
Type=simple
User=ai-auditor
ExecStart=/path/to/monitor.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🔒 Bezpieczeństwo

### Firewall
```bash
# UFW configuration
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### SSL/TLS
```bash
# Let's Encrypt (jeśli nie używasz Cloudflare)
sudo apt install certbot
sudo certbot --nginx -d audit.client.com
```

### Backup
```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_$DATE.tar.gz /path/to/ai-auditor/data
aws s3 cp backup_$DATE.tar.gz s3://your-backup-bucket/
```

## 🚀 Deployment Scripts

### start.sh
```bash
#!/bin/bash
set -e

echo "🚀 Starting AI Auditor..."

# Check GPU
nvidia-smi

# Start API server
cd local_test
uvicorn server:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Wait for API
sleep 5

# Start UI
cd ../web
streamlit run modern_ui.py --server.port 8503 --server.address 0.0.0.0 &
UI_PID=$!

echo "✅ AI Auditor started!"
echo "📊 Panel: http://localhost:8503"
echo "⚡ API: http://localhost:8000"

# Cleanup function
cleanup() {
    echo "🛑 Stopping AI Auditor..."
    kill $API_PID $UI_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM
wait
```

### stop.sh
```bash
#!/bin/bash
echo "🛑 Stopping AI Auditor..."

# Kill processes
pkill -f "uvicorn server:app"
pkill -f "streamlit run modern_ui.py"

echo "✅ AI Auditor stopped"
```

### restart.sh
```bash
#!/bin/bash
echo "🔄 Restarting AI Auditor..."
./stop.sh
sleep 2
./start.sh
```

## 📋 Checklist Wdrożenia

### Przed Wdrożeniem
- [ ] Sprawdzenie wymagań systemowych
- [ ] Instalacja zależności
- [ ] Konfiguracja GPU i CUDA
- [ ] Test lokalny systemu

### Wdrożenie Lokalne
- [ ] Instalacja pakietu klienckiego
- [ ] Konfiguracja plików config
- [ ] Uruchomienie systemu
- [ ] Test wszystkich funkcji

### Wdrożenie z Cloudflare
- [ ] Konfiguracja domeny
- [ ] Setup Cloudflare Tunnel
- [ ] Konfiguracja SSL/TLS
- [ ] Test połączenia zewnętrznego

### Po Wdrożeniu
- [ ] Test wydajności
- [ ] Konfiguracja monitoringu
- [ ] Setup backup
- [ ] Dokumentacja dla użytkowników

## 🆘 Rozwiązywanie Problemów

### System nie uruchamia się
```bash
# Sprawdź logi
tail -f logs/ai-auditor.log

# Sprawdź GPU
nvidia-smi

# Sprawdź porty
netstat -tlnp | grep -E "(8000|8503)"
```

### Problemy z Cloudflare
```bash
# Sprawdź tunnel status
cloudflared tunnel info ai-auditor

# Sprawdź DNS
nslookup audit.client.com

# Test połączenia
curl -I https://audit.client.com
```

### Problemy z wydajnością
```bash
# Sprawdź zasoby
htop
nvidia-smi -l 1

# Sprawdź logi
grep "ERROR" logs/ai-auditor.log
```

## 📞 Wsparcie

### Kontakt
- **Email**: support@ai-auditor.com
- **Telefon**: +48 XXX XXX XXX
- **Dokumentacja**: http://localhost:8000/docs

### Escalation
1. **Level 1**: Podstawowe problemy
2. **Level 2**: Problemy techniczne
3. **Level 3**: Problemy architektoniczne

---

**Wersja**: 1.0.0  
**Data**: 2024-01-15  
**Autor**: AI Auditor Team
