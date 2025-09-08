# 🚀 Konfiguracja AI przez Tunel Localtunnel

## ✅ **Status: GOTOWE**

Twoje lokalne AI jest teraz dostępne publicznie przez tunel!

## 🔗 **URL Twojego AI:**
```
https://ai-auditor-romaks.loca.lt
```

## 🎯 **Jak to działa:**

1. **Lokalnie**: AI server działa na `http://localhost:8000`
2. **Tunel**: Localtunnel przekierowuje ruch z `https://ai-auditor-romaks.loca.lt` na lokalny port 8000
3. **Streamlit Cloud**: Aplikacja na `https://ai-auditor-86.streamlit.app/` używa publicznego URL AI

## 🚀 **Uruchomienie (wymagane):**

### **Krok 1: Uruchom AI Server**
```bash
cd /home/romaks/ai_2/ai-auditor
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### **Krok 2: Uruchom Tunel (w nowym terminalu)**
```bash
cd /home/romaks/ai_2/ai-auditor
lt --port 8000 --subdomain ai-auditor-romaks
```

### **Krok 3: Sprawdź czy działa**
```bash
curl https://ai-auditor-romaks.loca.lt/healthz
curl https://ai-auditor-romaks.loca.lt/ready
```

## 🌐 **Testowanie:**

1. **Otwórz**: https://ai-auditor-86.streamlit.app/
2. **Sprawdź AI Status** - powinien pokazywać "✅ AI Model gotowy"
3. **Przetestuj chat** - zadaj pytanie w sekcji "Analiza Sprawozdania"

## ⚠️ **Ważne:**

- **Tunel musi być aktywny** - jeśli go zamkniesz, AI przestanie działać na stronie
- **AI Server musi działać** - tunel tylko przekierowuje ruch
- **URL tunelu** może się zmienić przy restarcie (ale subdomain `ai-auditor-romaks` powinien zostać)

## 🔧 **Troubleshooting:**

### **Problem: "Serwer AI niedostępny"**
```bash
# Sprawdź czy AI server działa
curl http://localhost:8000/healthz

# Sprawdź czy tunel działa
curl https://ai-auditor-romaks.loca.lt/healthz
```

### **Problem: "Model się dogrzewa"**
- Poczekaj 2-3 minuty po uruchomieniu AI servera
- Model Llama 3 8B potrzebuje czasu na załadowanie

### **Problem: Tunel nie działa**
```bash
# Restart tunelu
pkill -f localtunnel
lt --port 8000 --subdomain ai-auditor-romaks
```

## 📊 **Status Endpointów:**

- ✅ `/healthz` - podstawowe "żyję"
- ✅ `/ready` - status modelu
- ✅ `/analyze` - główny endpoint AI

## 🎉 **Gotowe!**

Twoje lokalne AI jest teraz dostępne na stronie projektowej!
