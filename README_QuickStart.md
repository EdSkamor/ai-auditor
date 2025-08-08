# AI Auditor — Quick Start (Linux Mint 22.1 XFCE)

Ten przewodnik pozwala uruchomić AI Auditor lokalnie na Linux Mint 22.1 XFCE (bazującym na Ubuntu 24.04 LTS) od zera — zarówno w trybie deweloperskim, jak i jako usługę systemową z reverse proxy w Nginx.

---

## A. Wymagania wstępne

### 1. Aktualizacja systemu
\`\`\`bash
sudo apt update && sudo apt upgrade -y
\`\`\`

### 2. Instalacja pakietów bazowych
\`\`\`bash
sudo apt install -y python3.12 python3.12-venv python3-pip git curl \
                    build-essential libssl-dev libffi-dev \
                    nginx
\`\`\`

### 3. (Opcjonalnie) Sterowniki NVIDIA + CUDA
Jeśli masz kartę NVIDIA, zainstaluj sterowniki i CUDA Toolkit:
\`\`\`bash
sudo apt install -y nvidia-driver-550 nvidia-cuda-toolkit
\`\`\`

---

## B. Klonowanie repozytorium i przygotowanie środowiska
\`\`\`bash
# Pobierz kod
git clone https://github.com/EdSkamor/ai-audytor.git
cd ai-audytor

# Utwórz wirtualne środowisko
python3.12 -m venv .venv
source .venv/bin/activate

# Zainstaluj zależności
pip install --upgrade pip
pip install -r requirements.txt
\`\`\`

---

## C. Uruchomienie lokalne (tryb dev)
\`\`\`bash
export TRANSFORMERS_VERBOSITY=error
uvicorn server:app --reload --host 0.0.0.0 --port 8000
\`\`\`

- Strona będzie dostępna pod: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- API health check:
\`\`\`bash
curl -s http://127.0.0.1:8000/healthz
\`\`\`

---

## D. Uruchamianie jako usługa systemd

### 1. Tworzenie unitu systemowego
Plik \`/etc/systemd/system/aiauditor.service\`:
\`\`\`ini
[Unit]
Description=AI Auditor Service
After=network.target

[Service]
User=USERNAME
WorkingDirectory=/home/USERNAME/ai-audytor
Environment="PATH=/home/USERNAME/ai-audytor/.venv/bin"
Environment="TRANSFORMERS_VERBOSITY=error"
ExecStart=/home/USERNAME/ai-audytor/.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
\`\`\`
> 🔹 Zamień \`USERNAME\` na swoją nazwę użytkownika w systemie.

### 2. Aktywacja usługi
\`\`\`bash
sudo systemctl daemon-reload
sudo systemctl enable --now aiauditor.service
\`\`\`

### 3. Sprawdzenie statusu
\`\`\`bash
systemctl status aiauditor.service
\`\`\`

---

## E. Reverse Proxy w Nginx

Plik \`/etc/nginx/sites-available/aiauditor\`:
\`\`\`nginx
server {
    listen 80;
    server_name twojadomena.pl;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
\`\`\`

Aktywacja konfiguracji:
\`\`\`bash
sudo ln -s /etc/nginx/sites-available/aiauditor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
\`\`\`
> 🔹 Jeśli chcesz HTTPS, użyj [Certbot](https://certbot.eff.org/) do wystawienia certyfikatu Let's Encrypt.

---

## F. Test działania

1. Sprawdź dostępność API:
\`\`\`bash
curl -s http://twojadomena.pl/healthz
\`\`\`

2. Wejdź w przeglądarce na:
\`\`\`
http://twojadomena.pl
\`\`\`

---

**Gotowe!**
Teraz AI Auditor działa w tle jako usługa systemowa i jest dostępny przez domenę z reverse proxy.
