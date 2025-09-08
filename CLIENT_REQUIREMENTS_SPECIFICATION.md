# Specyfikacja Funkcjonalności AI Auditor - Dane od Klienta

## Analiza Pliku: AB Wstepne Procedury (1).xlsx

### Struktura Dokumentu
Plik zawiera **14 arkuszy** z kompletną dokumentacją badania audytorskiego:

1. **Instrukcja Prompt** - Instrukcje dla AI
2. **Dane** - Podstawowe informacje o jednostce
3. **BILANS** - Bilans za lata poprzednie
4. **BILANS KOREKT** - Bilans skorygowany (rok bieżący)
5. **RachPor** - Rachunek zysków i strat za lata poprzednie
6. **RachPor KOREKT** - Rachunek zysków i strat skorygowany (rok bieżący)
7. **RachKal** - Rachunek kalkulacyjny za lata poprzednie
8. **RachKal Korekt** - Rachunek kalkulacyjny skorygowany (rok bieżący)
9. **Cash Flow (RPP)** - Rachunek przepływów pieniężnych
10. **ZZwK** - Zestawienie zmian w kapitale
11. **260 ANAW** - Analiza wskaźnikowa
12. **301 ANAW** - Analiza wskaźnikowa (dodatkowa)
13. **302 RYZBAD** - Ryzyka badania
14. **303 BAZRYZN** - Baza ryzyk

## Instrukcje dla AI (Arkusz "Instrukcja Prompt")

### Główne Zadania AI:
1. **Zgromadzenie sprawozdań finansowych** za ostatnie 3 lata z KRS
2. **Import danych finansowych** do arkuszy:
   - BILANS KOREKT kol.D - rok bieżący
   - BILANS kol.C i D - lata poprzednie
   - RachPor KOREKT kol.D - rok bieżący
   - RachPor kol.C i D - lata poprzednie
3. **Uzupełnienie danych** w arkuszu "Dane" (nazwa jednostki, zarząd, rok SF)
4. **Automatyczne wypełnienie** arkuszy na podstawie danych
5. **Analiza ryzyk** w arkuszu 302 RYZBAD

### Prompt dla Analizy Ryzyk:
```
Przygotuj w formie wypełnionej tabeli 302 RYZBAD ryzyka nieodłączne do badania sprawozdania finansowego danej jednostki.

Weź pod uwagę:
- Charakterystykę jednostki
- Ryzyka specyficzne dla działalności
- Otoczenie prawne jednostki
- Informacje z rynku na temat branży
- Sytuację aktualną jednostki (sprawozdanie zarządu, komunikaty, strona internetowa, publikacje prasowe)
- Dane finansowe (zmiany pozycji na przestrzeni ostatnich 3 lat)
- Istotność badania (Krajowe Standardy Badania)
- Istotność wykonawczą
- Planowanie procedur audytu i technik badania
```

## Struktura Danych Finansowych

### Arkusz "Dane"
Zawiera:
- **Identyfikacja podmiotu** (nazwa, siedziba, NIP, REGON)
- **Zarząd** (prezes, członkowie zarządu)
- **Dane finansowe** (przychody, koszty, zyski/straty)
- **Wskaźniki finansowe** (rentowność, płynność, efektywność)
- **Analiza statystyczna** wskaźników

### Kluczowe Wskaźniki Finansowe:
1. **Rentowność:**
   - ROA (Rentowność aktywów): 19.76%
   - ROE (Rentowność kapitałów własnych): 30.68%
   - Rentowność sprzedaży: 7.52%

2. **Płynność:**
   - Wskaźnik płynności I: 1.86
   - Wskaźnik płynności II: 1.38
   - Wskaźnik płynności III: 1.05

3. **Efektywność:**
   - Rotacja aktywów: 2.71
   - Rotacja środków trwałych: 6.95
   - Rotacja aktywów obrotowych: 4.23
   - Szybkość obrotu zapasów: 24.47 dni
   - Szybkość obrotu należności: 15.19 dni
   - Szybkość obrotu zobowiązań: 43.04 dni

## Arkusz Ryzyk (302 RYZBAD)

### Struktura Analizy Ryzyk:
1. **Ryzyka rozległe (ogólne):**
   - Ryzyko obejścia kontroli przez zarząd
   - Ryzyko oszustwa na poziomie sprawozdania

2. **Ryzyka specyficzne (na poziomie stwierdzeń):**
   - Obszar badania
   - Czynniki ryzyka
   - Opis ryzyka ("co może pójść źle")
   - Rodzaj ryzyka (rozległe/specyficzne)
   - Prawdopodobieństwo wystąpienia (1-3)
   - Oczekiwana wielkość zniekształcenia
   - Czy ryzyko wynika z szacunków
   - Ryzyko oszustwa/nadużyć
   - Obszar kontroli wewnętrznej
   - Testowanie kontroli
   - Reakcja na RIZ (testy szczegółowe)
   - Techniki badania
   - Procedury wiarygodności

## Specyfikacja Funkcjonalności dla AI Auditor

### 1. Moduł Importu Danych
- **Import z KRS:** Automatyczne pobieranie sprawozdań finansowych
- **Import Excel:** Wczytywanie danych z plików Excel
- **Walidacja danych:** Sprawdzanie kompletności i poprawności
- **Mapowanie pól:** Automatyczne przypisywanie danych do odpowiednich arkuszy

### 2. Moduł Analizy Finansowej
- **Kalkulacja wskaźników:** Automatyczne obliczanie wskaźników finansowych
- **Analiza trendów:** Porównanie danych za 3 lata
- **Benchmarking:** Porównanie z branżą
- **Identyfikacja anomalii:** Wykrywanie nietypowych zmian

### 3. Moduł Analizy Ryzyk
- **Identyfikacja ryzyk:** Automatyczne wykrywanie ryzyk na podstawie danych
- **Klasyfikacja ryzyk:** Rozległe vs specyficzne
- **Ocena prawdopodobieństwa:** Algorytmiczna ocena ryzyka
- **Planowanie procedur:** Sugerowanie testów audytorskich
- **Dokumentacja:** Generowanie kart badania

### 4. Moduł Raportowania
- **Generowanie arkuszy:** Automatyczne wypełnianie szablonów
- **Raporty analityczne:** Szczegółowe analizy wskaźników
- **Wnioski i rekomendacje:** AI-generated insights
- **Eksport:** PDF, Excel, Word

### 5. Moduł Integracji
- **API KRS:** Połączenie z bazą KRS
- **Integracja z systemami:** ERP, księgowe
- **Synchronizacja danych:** Real-time updates
- **Backup i wersjonowanie:** Historia zmian

## Priorytety Implementacji

### Faza 1 (Pilne):
1. **Import danych Excel** - podstawowa funkcjonalność
2. **Kalkulacja wskaźników** - automatyczne obliczenia
3. **Analiza ryzyk** - identyfikacja podstawowych ryzyk

### Faza 2 (Średnioterminowe):
1. **Integracja z KRS** - automatyczne pobieranie danych
2. **Zaawansowana analiza** - AI-powered insights
3. **Generowanie raportów** - automatyczne dokumenty

### Faza 3 (Długoterminowe):
1. **Machine Learning** - predykcja ryzyk
2. **Integracja z systemami** - pełna automatyzacja
3. **Dashboard** - interaktywne raporty

## Wymagania Techniczne

### Dane Wejściowe:
- Sprawozdania finansowe (Excel, PDF)
- Dane z KRS (API)
- Informacje o jednostce (nazwa, branża, wielkość)

### Dane Wyjściowe:
- Wypełnione arkusze analityczne
- Karty badania ryzyk
- Raporty z wnioskami
- Rekomendacje procedur audytorskich

### Integracje:
- KRS API
- Systemy księgowe
- Bazy danych branżowych
- Narzędzia audytorskie

## Uwagi Implementacyjne

1. **Zgodność z ISA:** Wszystkie procedury muszą być zgodne z Międzynarodowymi Standardami Badania
2. **Bezpieczeństwo danych:** Szyfrowanie, kontrola dostępu, audit trail
3. **Skalowalność:** System musi obsługiwać różne rozmiary jednostek
4. **Użyteczność:** Intuicyjny interfejs dla audytorów
5. **Dokumentacja:** Pełna dokumentacja procedur i metodologii
