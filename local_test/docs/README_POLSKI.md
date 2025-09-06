
# AI Auditor - Instrukcja Użytkownika (Polski)

## 🎯 Co Otrzymujesz

### System Główny
- **Silnik Audytu Faktur**: Kompletny pipeline index → match → export
- **Logika Tie-breaker**: Dopasowanie nazwa pliku vs. klient z konfigurowalnymi wagami
- **Kompatybilność Formatów Liczb**: Obsługuje 1,000.00, 1 000,00 i inne formaty
- **Profesjonalne Raporty**: Excel, JSON, CSV z podsumowaniami wykonawczymi

### Interfejs Web
- **Panel Przesyłania**: Przeciągnij i upuść pliki PDF/ZIP
- **Konfiguracja Audytu**: Dostosuj wagi tie-breaker i opcje przetwarzania
- **Dashboard Wyników**: Zobacz top niedopasowania i pobierz pakiety
- **Przetwarzanie w Czasie Rzeczywistym**: Aktualizacje postępu na żywo

### Lokalny Asystent AI
- **Q&A oparte na RAG**: Zadawaj pytania dotyczące danych audytu
- **Praca Offline**: Działa bez internetu po pobraniu modeli
- **Wsparcie Wielojęzyczne**: Polski i Angielski
- **Ekspertyza Księgowa**: Wyszkolony na wiedzy audytowej i księgowej

## 🚀 Szybki Start

### 1. Uruchomienie
```bash
# Uruchom skrypt startowy
./scripts/start_local_test.sh
```

### 2. Dostęp do Interfejsu
- **Panel Web**: http://localhost:8501
- **Serwer API**: http://localhost:8000
- **Dokumentacja**: http://localhost:8000/docs

## 📊 Przykłady Użycia

### Interfejs Web
1. Otwórz http://localhost:8501
2. Prześlij pliki PDF (lub archiwum ZIP)
3. Prześlij plik danych POP
4. Skonfiguruj ustawienia tie-breaker
5. Kliknij "Uruchom Audyt"
6. Pobierz pakiet wyników

### Użycie CLI
```bash
# Walidacja demo
ai-auditor validate --demo --file faktura.pdf --pop-file pop.xlsx

# Walidacja zbiorcza
ai-auditor validate --bulk --input-dir ./pdfs --pop-file pop.xlsx --output-dir ./results

# Z niestandardowymi ustawieniami tie-breaker
ai-auditor validate --bulk --input-dir ./pdfs --pop-file pop.xlsx \
  --tiebreak-weight-fname 0.7 --tiebreak-min-seller 0.4 --amount-tol 0.01
```

### Asystent AI
1. Otwórz interfejs web
2. Przejdź do zakładki "Asystent AI"
3. Zadawaj pytania takie jak:
   - "Jakie są top niedopasowania w moim audycie?"
   - "Wyjaśnij logikę tie-breaker"
   - "Jak interpretować wyniki pewności?"

## 📁 Pliki Wynikowe

### Wyniki Audytu
- `Audyt_koncowy.xlsx` - Kompletny raport Excel
- `verdicts.jsonl` - Szczegółowe wyniki dopasowania
- `verdicts_summary.json` - Podsumowanie wykonawcze
- `verdicts_top50_mismatches.csv` - Top niedopasowania
- `All_invoices.csv` - Wszystkie przetworzone faktury
- `ExecutiveSummary.pdf` - Podsumowanie wykonawcze (opcjonalne)

## 🧪 Testowanie

### Uruchom Testy
```bash
# Kompletny zestaw testów
python3 scripts/smoke_all.py

# Test wydajności
python3 scripts/smoke_perf_200.py

# Test A/B tie-breaker
python3 scripts/smoke_tiebreak_ab.py
```

### Weryfikacja Instalacji
```bash
# Sprawdź interfejs web
curl http://localhost:8501

# Sprawdź API
curl http://localhost:8000/healthz
```

## 🛡️ Bezpieczeństwo

### Ochrona Danych
- Wszystkie przetwarzanie jest lokalne (brak chmury)
- Żadne dane nie opuszczają systemu
- Opcje szyfrowanego przechowywania
- Ślady audytu dla wszystkich operacji

### Kontrola Dostępu
- Dostęp tylko z sieci lokalnej
- Konfigurowalna autentykacja
- Uprawnienia oparte na rolach
- Zarządzanie sesjami

## 📞 Wsparcie

### Dokumentacja
- `docs/` - Kompletna dokumentacja
- `PRODUCTION_CHECKLIST.md` - Status funkcji
- `docs/CONTEXT_FOR_CURSOR.md` - Kontekst rozwoju

### Rozwiązywanie Problemów
- Sprawdź logi w katalogu `logs/`
- Uruchom skrypty diagnostyczne
- Zweryfikuj wymagania systemowe
- Sprawdź pobieranie modeli

## 🎯 Wydajność

### Benchmarki
- **Przetwarzanie PDF**: >20 plików/sekundę
- **Dopasowanie**: >100 dopasowań/sekundę
- **Użycie Pamięci**: <100MB na 1000 rekordów
- **Odpowiedź AI**: <2 sekundy na pytanie

### Optymalizacja
- Akceleracja GPU włączona
- Kwantyzacja modelu 4-bit
- Przetwarzanie wsadowe
- Efektywne strumieniowanie pamięci

---

**Twój system AI Auditor jest gotowy do użycia produkcyjnego!** 🚀
