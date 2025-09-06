# AI Auditor - Przewodnik Użytkownika (Wersja dla Osób Nietechnicznych)

## 🎯 Co to jest AI Auditor?

AI Auditor to inteligentny system do automatycznego audytu faktur i dokumentów księgowych. System wykorzystuje sztuczną inteligencję do:

- **Automatycznego przetwarzania** tysięcy faktur w kilka minut
- **Wykrywania błędów** i niezgodności w dokumentach
- **Generowania raportów** gotowych do przekazania klientowi
- **Oceny ryzyk** związanych z transakcjami i kontrahentami

## 🚀 Jak zacząć?

### 1. Uruchomienie Systemu
Po zainstalowaniu systemu, uruchom go klikając na ikonę "AI Auditor" na pulpicie lub wpisując w przeglądarce:
```
http://localhost:8503
```

### 2. Pierwsze Logowanie
- **Login**: Twój adres email
- **Hasło**: Hasło otrzymane od administratora
- **Rola**: auditor, senior, partner, lub client_pbc

## 📊 Panel Główny (Dashboard)

### Co widzisz na dashboardzie?
- **Liczba aktywnych zadań** - ile audytów jest w trakcie
- **Znalezione niezgodności** - ile błędów zostało wykrytych
- **Zakończone audyty** - ile raportów jest gotowych
- **Wykresy** pokazujące status zadań i poziomy ryzyka

### Jak korzystać z dashboardu?
1. **Przeglądaj statystyki** - zobacz ogólny stan systemu
2. **Kliknij na wykresy** - zobacz szczegóły
3. **Użyj skrótów klawiszowych** - Ctrl+1 (Dashboard), Ctrl+2 (Run), itd.

## 🏃 Uruchamianie Audytu (Run)

### Jak wgrać pliki?
1. **Kliknij "Wybierz pliki"** w sekcji Upload
2. **Wybierz pliki** z komputera (PDF, ZIP, CSV, Excel)
3. **Kliknij "Uruchom Audyt"**
4. **Obserwuj postęp** w kolejce zadań

### Jakie pliki można wgrać?
- **PDF** - faktury, umowy, dokumenty
- **ZIP** - archiwa z wieloma plikami
- **CSV/Excel** - listy transakcji, kontrahentów
- **XML** - pliki KSeF, JPK

### Co się dzieje podczas audytu?
1. **Indeksowanie** - system czyta i analizuje pliki
2. **Dopasowywanie** - porównuje dane z bazą kontrahentów
3. **Wykrywanie błędów** - znajduje niezgodności
4. **Generowanie raportu** - tworzy podsumowanie

## 🔍 Przeglądanie Wyników (Findings)

### Co to są "Findings"?
To lista wszystkich znalezionych problemów i niezgodności w dokumentach.

### Jak filtrować wyniki?
- **Poziom ryzyka**: Wysoki, Średni, Niski
- **Kategoria**: Płatności, Kontrahenci, AML, Compliance
- **Data**: Od kiedy szukać problemów

### Jak działa system kolorów?
- 🔴 **Czerwony** - Wysokie ryzyko (wymaga natychmiastowej uwagi)
- 🟡 **Żółty** - Średnie ryzyko (wymaga sprawdzenia)
- 🟢 **Zielony** - Niskie ryzyko (informacyjny)

### Bulk-akcje (Operacje masowe)
- **Zaznacz wszystkie** - wybierz wszystkie niezgodności
- **Eksportuj zaznaczone** - pobierz wybrane problemy
- **Usuń zaznaczone** - usuń z listy (ostrożnie!)

## 📤 Eksportowanie Raportów (Exports)

### Rodzaje eksportów:

#### 📋 PBC (Prepared by Client)
- **Lista PBC** - co klient musi przygotować
- **Status PBC** - co już zostało dostarczone
- **Timeline PBC** - harmonogram dostaw

#### 📁 Working Papers
- **Working Papers** - dokumenty robocze audytu
- **Łańcuch dowodowy** - dowody na każdy wniosek
- **Statystyki WP** - podsumowanie dokumentów

#### 📈 Raporty
- **Raport końcowy** - główny raport audytu
- **Executive Summary** - podsumowanie dla zarządu
- **Compliance Report** - raport zgodności

### Jak eksportować?
1. **Wybierz typ raportu** z odpowiedniej sekcji
2. **Kliknij przycisk eksportu**
3. **Poczekaj na generowanie** (może potrwać kilka minut)
4. **Pobierz plik** z historii eksportów

## 🤖 Asystent AI

### Jak korzystać z asystenta?
1. **Kliknij ikonę chat** w prawym dolnym rogu
2. **Zadaj pytanie** w języku polskim
3. **Otrzymaj odpowiedź** z odnośnikami do dokumentów

### Przykłady pytań:
- "Jakie są wymagania dla JPK_V7?"
- "Co oznacza niezgodność w VAT?"
- "Jakie procedury zastosować dla dużych transakcji?"
- "Wyjaśnij różnicę między MSRF a PSR"

### Tryby asystenta:
- **Explain** - wyjaśnienie pojęć
- **Check** - sprawdzenie zgodności
- **Propose procedures** - propozycja procedur
- **Draft memo** - przygotowanie notatki

## ⚙️ Ustawienia i Personalizacja

### Tryb ciemny/jasny
- **Kliknij ikonę słońca/księżyca** w prawym górnym rogu
- **System zapamięta** Twoje preferencje

### Skróty klawiszowe
- **Ctrl+1** - Dashboard
- **Ctrl+2** - Run (Uruchamianie)
- **Ctrl+3** - Findings (Wyniki)
- **Ctrl+4** - Exports (Eksporty)
- **Ctrl+D** - Przełącz tryb ciemny/jasny
- **Ctrl+R** - Odśwież stronę

## 🔒 Bezpieczeństwo

### Twoje dane są bezpieczne
- **Szyfrowanie** - wszystkie dane są zaszyfrowane
- **Audit trail** - każda akcja jest rejestrowana
- **Kontrola dostępu** - tylko uprawnione osoby mają dostęp
- **Backup** - regularne kopie zapasowe

### Role użytkowników:
- **Auditor** - podstawowe funkcje audytu
- **Senior** - zaawansowane funkcje + zatwierdzanie
- **Partner** - pełny dostęp + zarządzanie
- **Client PBC** - tylko przeglądanie swoich danych

## 🆘 Rozwiązywanie Problemów

### System nie uruchamia się
1. **Sprawdź połączenie internetowe**
2. **Zrestartuj przeglądarkę**
3. **Skontaktuj się z administratorem**

### Pliki się nie wgrywają
1. **Sprawdź format pliku** (PDF, ZIP, CSV, Excel)
2. **Sprawdź rozmiar** (max 100MB)
3. **Spróbuj ponownie** za kilka minut

### Asystent AI nie odpowiada
1. **Sprawdź połączenie internetowe**
2. **Zadaj pytanie ponownie**
3. **Użyj prostszego języka**

### Raporty się nie generują
1. **Sprawdź czy audyt się zakończył**
2. **Poczekaj kilka minut**
3. **Spróbuj ponownie**

## 📞 Wsparcie

### Kontakt
- **Email**: support@ai-auditor.com
- **Telefon**: +48 XXX XXX XXX
- **Godziny**: 8:00-18:00 (pon-pt)

### Dokumentacja
- **Przewodnik użytkownika**: http://localhost:8000/docs
- **FAQ**: Często zadawane pytania
- **Wideo tutoriale**: Linki do filmów instruktażowych

## 💡 Wskazówki i Najlepsze Praktyki

### Jak efektywnie korzystać z systemu?
1. **Regularnie sprawdzaj dashboard** - bądź na bieżąco
2. **Używaj filtrów** - znajdź szybko to czego szukasz
3. **Eksportuj raporty** - zachowaj kopie zapasowe
4. **Korzystaj z asystenta AI** - zadawaj pytania
5. **Używaj skrótów klawiszowych** - oszczędzaj czas

### Jak przygotować pliki do audytu?
1. **Uporządkuj pliki** - nazwij je logicznie
2. **Sprawdź jakość** - upewnij się, że PDF-y są czytelne
3. **Grupuj tematycznie** - faktury, umowy, itp.
4. **Sprawdź rozmiar** - nie przekraczaj 100MB

### Jak interpretować wyniki?
1. **Zacznij od wysokich ryzyk** - najważniejsze problemy
2. **Sprawdź kontekst** - kliknij na szczegóły
3. **Użyj asystenta AI** - poproś o wyjaśnienie
4. **Dokumentuj działania** - zapisz co zrobiłeś

---

**Pamiętaj**: AI Auditor to narzędzie wspomagające, ale ostateczne decyzje zawsze podejmuje audytor. System pomaga w identyfikacji problemów, ale wymaga ludzkiej oceny i interpretacji.
