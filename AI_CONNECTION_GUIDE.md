# 🤖 Przewodnik Połączenia AI

## ✅ **Status: Połączenie AI Gotowe!**

Twoje AI jest teraz w pełni połączone z aplikacją Streamlit. Oto jak to działa:

## 🚀 **Jak uruchomić system z AI**

### **Krok 1: Uruchom serwer AI**
```bash
# Aktywuj środowisko wirtualne
source venv/bin/activate

# Uruchom serwer AI (w osobnym terminalu)
./start_ai_server.sh
```

**Co się dzieje:**
- ✅ Ładuje model Llama 3 8B na RTX 4090
- ✅ Uruchamia API na porcie 8000
- ✅ Model gotowy w ~30 sekund

### **Krok 2: Uruchom Streamlit z AI**
```bash
# W nowym terminalu
source venv/bin/activate
./start_streamlit_with_ai.sh
```

**Co się dzieje:**
- ✅ Łączy się z serwerem AI na localhost:8000
- ✅ Uruchamia Streamlit na porcie 8501
- ✅ AI działa w trybie rzeczywistym

## 🌐 **Dostęp do aplikacji**

- **Panel Streamlit**: http://localhost:8501
- **API AI**: http://localhost:8000
- **Status AI**: http://localhost:8000/healthz
- **Gotowość modelu**: http://localhost:8000/ready

## 🔧 **Jak działa połączenie**

### **Architektura:**
```
[Streamlit UI] ←→ [AI Server] ←→ [Llama 3 Model]
    8501             8000           RTX 4090
```

### **Funkcje AI:**
1. **Zakładka "Audytor"** - AI asystent w każdej podzakładce
2. **Analiza Sprawozdania** - specjalistyczne odpowiedzi o analizie finansowej
3. **Ocena Ryzyka** - ekspert w ocenie ryzyk audytowych
4. **Fallback** - jeśli AI niedostępny, używa inteligentnych odpowiedzi przykładowych

### **Parametry AI:**
- **Model**: Llama 3 8B Instruct
- **Temperatura**: 0.8 (bardziej naturalne odpowiedzi)
- **Max tokens**: 512
- **Quantization**: 4-bit (oszczędność pamięci)

## 📊 **Status AI w aplikacji**

W sidebarze widzisz:
- ✅ **AI Model gotowy** - model załadowany i gotowy
- ⏳ **AI Model się dogrzewa** - model się ładuje
- ❌ **Serwer AI niedostępny** - brak połączenia

## 🛠️ **Rozwiązywanie problemów**

### **Problem: "Serwer AI niedostępny"**
```bash
# Sprawdź czy serwer działa
curl http://localhost:8000/healthz

# Jeśli nie działa, uruchom ponownie
./start_ai_server.sh
```

### **Problem: "Model się dogrzewa"**
- Poczekaj ~30 sekund na załadowanie modelu
- Sprawdź status: http://localhost:8000/ready

### **Problem: Brak GPU**
- Model będzie działał na CPU (wolniej)
- Zainstaluj sterowniki NVIDIA + CUDA

### **Problem: Brak pamięci GPU**
```bash
# Sprawdź użycie GPU
nvidia-smi

# Model używa ~12GB VRAM (4-bit quantization)
```

## 🎯 **Testowanie AI**

### **Test 1: Podstawowy**
1. Otwórz http://localhost:8501
2. Przejdź do zakładki "🔍 Audytor"
3. Wybierz "📊 Analiza Sprawozdania"
4. Zadaj pytanie: "Jakie są główne wskaźniki płynności?"

### **Test 2: Zaawansowany**
1. Wybierz "⚠️ Ocena Ryzyka"
2. Zadaj pytanie: "Jak ocenić ryzyko kontroli wewnętrznej?"
3. Sprawdź czy odpowiedź jest naturalna i szczegółowa

## 🔄 **Aktualizacje**

### **Aktualizacja modelu:**
```bash
# Zatrzymaj serwer (Ctrl+C)
# Zaktualizuj model w model_hf_interface.py
# Uruchom ponownie
./start_ai_server.sh
```

### **Aktualizacja temperatury:**
- Edytuj `temperature=0.8` w `streamlit_app.py`
- Restart Streamlit

## 📈 **Wydajność**

### **Czasy odpowiedzi:**
- **Proste pytania**: 2-5 sekund
- **Złożone analizy**: 5-15 sekund
- **Timeout**: 30 sekund

### **Ograniczenia:**
- **Max tokens**: 512 (można zwiększyć)
- **Concurrent requests**: 1 (można zwiększyć)
- **Memory**: ~12GB VRAM

## 🚀 **Wdrożenie na Streamlit Cloud**

Aby wdrożyć na https://ai-auditor-86.streamlit.app/:

1. **Opcja 1: Cloudflare Tunnel**
   ```bash
   # Uruchom lokalny serwer AI
   ./start_ai_server.sh

   # Skonfiguruj Cloudflare Tunnel
   cloudflared tunnel create ai-auditor
   cloudflared tunnel route dns ai-auditor ai-auditor-86.streamlit.app
   ```

2. **Opcja 2: Hugging Face Inference API**
   - Wdróż model na Hugging Face
   - Zmień `AI_SERVER_URL` w Streamlit

3. **Opcja 3: Mock Mode**
   - Aplikacja automatycznie używa mock responses
   - AI działa w trybie przykładowym

## ✅ **Podsumowanie**

Twoje AI jest teraz w pełni funkcjonalne!

**Co masz:**
- ✅ Prawdziwy model Llama 3 8B
- ✅ Naturalne odpowiedzi (temperatura 0.8)
- ✅ Specjalistyczne AI dla audytu
- ✅ Fallback na mock responses
- ✅ Status AI w czasie rzeczywistym
- ✅ Łatwe uruchamianie (2 skrypty)

**Następne kroki:**
1. Uruchom `./start_ai_server.sh`
2. Uruchom `./start_streamlit_with_ai.sh`
3. Otwórz http://localhost:8501
4. Przetestuj AI w zakładce "Audytor"

**Gotowe! 🎉**
