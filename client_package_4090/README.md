# AI Auditor - Pakiet Kliencki RTX 4090

## 🚀 Instalacja i Uruchomienie

### Wymagania Systemowe
- **GPU**: NVIDIA RTX 4090 (24 GB VRAM)
- **CPU**: 8 rdzeni (lub więcej)
- **RAM**: 32 GB+
- **Dysk**: ≥ 10 GB wolnego miejsca
- **OS**: Linux x86_64 (Ubuntu 22.04 LTS zalecane)
- **Sterowniki**: nvidia-driver + CUDA 12.x

### Szybka Instalacja

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

## 📋 Funkcjonalności

### 🔍 Silnik Audytu Faktur
- **Indeksowanie**: Automatyczne przetwarzanie PDF
- **Dopasowywanie**: Inteligentne mapowanie faktur
- **Eksport**: Raporty Excel, JSON, CSV, PDF

### 🤖 Lokalny Asystent AI
- **RAG System**: Q&A z zakresu rachunkowości/audytu
- **Specjalistyczna wiedza**: MSRF, PSR, MSSF, KSeF, JPK
- **Tryby**: Explain, Check, Propose procedures, Draft memo

### 🌐 Integracje PL-core
- **KSeF**: Walidacja XML faktur
- **JPK**: JPK_V7/JPK_KR/JPK_FA
- **Biała lista VAT**: Sprawdzanie NIP-ów
- **KRS/REGON**: Dane rejestrowe firm

### 📊 Analityka Audytowa
- **Ocena ryzyk**: Inherentne, kontroli, wykrycia
- **Journal Entry Testing**: Wykrywanie anomalii
- **Sampling**: MUS, Statistical, Non-statistical

### 🔒 Bezpieczeństwo i Compliance
- **Role użytkowników**: auditor, senior, partner, client_pbc
- **Audit trail**: Pełny dziennik zdarzeń
- **Szyfrowanie**: Hash signatures, HMAC
- **Kontrola dostępu**: RBAC

## 🎛️ Panel Audytora

### 3 Widoki Główne
1. **📊 Dashboard**: Przegląd systemu, statystyki
2. **🏃 Run**: Uruchamianie audytów, kolejka zadań
3. **🔍 Findings**: Niezgodności, filtry, bulk-akcje
4. **📤 Exports**: PBC, Working Papers, raporty

### Funkcje UI
- **Tryb ciemny/jasny**: Przełączanie motywów
- **Skróty klawiszowe**: Szybka nawigacja
- **Bulk-akcje**: Masowe operacje
- **Responsywny design**: Optymalizacja UX

## 🔧 Konfiguracja

### Pliki Konfiguracyjne
- `config/audit_config.yaml`: Konfiguracja audytu
- `config/model_config.yaml`: Konfiguracja modeli AI
- `config/integrations.yaml`: Integracje zewnętrzne

### Zmienne Środowiskowe
```bash
export AI_AUDITOR_DATA_DIR="/path/to/data"
export AI_AUDITOR_CACHE_DIR="/path/to/cache"
export AI_AUDITOR_LOG_LEVEL="INFO"
```

## 📚 Dokumentacja

### Dla Użytkowników
- [Przewodnik użytkownika](docs/user_guide.md)
- [FAQ](docs/faq.md)
- [Przykłady użycia](docs/examples.md)

### Dla Administratorów
- [Przewodnik wdrożenia](docs/deployment_guide.md)
- [Konfiguracja bezpieczeństwa](docs/security_guide.md)
- [Rozwiązywanie problemów](docs/troubleshooting.md)

## 🆘 Wsparcie

### Kontakt
- **Email**: support@ai-auditor.com
- **Telefon**: +48 XXX XXX XXX
- **Dokumentacja**: http://localhost:8000/docs

### Rozwiązywanie Problemów
1. Sprawdź logi: `tail -f logs/ai-auditor.log`
2. Sprawdź status GPU: `nvidia-smi`
3. Sprawdź porty: `netstat -tlnp | grep -E "(8000|8503)"`

## 📄 Licencja

Copyright © 2024 AI Auditor. Wszystkie prawa zastrzeżone.

---

**Wersja**: 1.0.0
**Data**: 2024-01-15
**Autor**: AI Auditor Team
