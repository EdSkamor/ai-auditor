# Wstępne Procedury - Dokumentacja Modułu

## Przegląd

Moduł `ai_audytor.validators.wstepne_procedury` przetwarza pliki Excel z Wstępnymi Procedurami audytorskimi, konwertuje je do formatu JSON i ewaluuje formuły Excel.

## Struktura Plików

### Wejście
- **Plik Excel**: `AB Wstepne Procedury (1).xlsx` - oryginalny plik z danymi audytorskimi
- **Plik JSON**: `ai_audytor_wsad_wstepne_procedury.json` - skonwertowany plik JSON

### Wyjście
- **Raport**: Struktura danych z wynikami ewaluacji formuł
- **Logi**: Informacje o błędach i statusie przetwarzania

## Mapowanie JSON ↔️ Arkusze

### Struktura JSON

```json
{
  "metadata": {
    "source_file": "AB Wstepne Procedury (1).xlsx",
    "sheets_count": 14,
    "sheets": ["Instrukcja Prompt", "Dane", "BILANS", ...]
  },
  "sheets": {
    "sheet_name": {
      "name": "sheet_name",
      "rows": 100,
      "cols": 10,
      "data": [
        {"0": "value", "1": "value", ...},
        ...
      ],
      "formulas": {},
      "named_ranges": {},
      "data_validations": {},
      "header_row_absolute": 0
    }
  }
}
```

### Mapowanie Arkuszy

| Arkusz | Opis | Zawartość |
|--------|------|-----------|
| **Instrukcja Prompt** | Instrukcje dla AI | Prompty, procedury, wytyczne |
| **Dane** | Podstawowe informacje | Identyfikacja podmiotu, wskaźniki |
| **BILANS** | Bilans za lata poprzednie | Aktywa, pasywa, kapitał |
| **BILANS KOREKT** | Bilans skorygowany | Rok bieżący z korektami |
| **RachPor** | Rachunek zysków i strat | Przychody, koszty, wyniki |
| **RachPor KOREKT** | RZiS skorygowany | Rok bieżący z korektami |
| **RachKal** | Rachunek kalkulacyjny | Szczegółowe koszty |
| **RachKal Korekt** | Rachunek kalkulacyjny skorygowany | Rok bieżący |
| **Cash Flow (RPP)** | Rachunek przepływów pieniężnych | Przepływy gotówkowe |
| **ZZwK** | Zestawienie zmian w kapitale | Zmiany kapitału |
| **260 ANAW** | Analiza wskaźnikowa | Wskaźniki finansowe |
| **301 ANAW** | Analiza wskaźnikowa (dodatkowa) | Dodatkowe wskaźniki |
| **302 RYZBAD** | Ryzyka badania | Identyfikacja i ocena ryzyk |
| **303 BAZRYZN** | Baza ryzyk | Katalog ryzyk |

## Obsługiwane Funkcje Excel

### Funkcje Matematyczne

#### SUM
```excel
=SUM(A1:A10)     # Suma zakresu
=SUM(A1,B1,C1)   # Suma pojedynczych komórek
```

#### AVERAGE
```excel
=AVERAGE(A1:A10) # Średnia z zakresu
=AVERAGE(A1,B1)  # Średnia z pojedynczych komórek
```

### Funkcje Statystyczne

#### COUNT/COUNTA
```excel
=COUNT(A1:A10)   # Liczba komórek z wartościami liczbowymi
=COUNTA(A1:A10)  # Liczba komórek z dowolnymi wartościami
```

### Funkcje Logiczne

#### IF
```excel
=IF(A1>100, "High", "Low")  # Warunkowa ewaluacja
=IF(A1>50, A1*2, A1)        # Warunkowe obliczenia
```

## Ograniczenia

### Obsługiwane Funkcje
- ✅ SUM, AVERAGE, COUNT, COUNTA, IF
- ❌ VLOOKUP, HLOOKUP, INDEX, MATCH
- ❌ Funkcje tekstowe (CONCATENATE, LEFT, RIGHT)
- ❌ Funkcje daty (TODAY, NOW, DATE)
- ❌ Funkcje finansowe (NPV, IRR, PMT)

### Ograniczenia Parsowania
- **Referencje komórek**: Obsługiwane formaty A1, $A$1
- **Zakresy**: Obsługiwane formaty A1:A10, $A$1:$B$10
- **Zagnieżdżone funkcje**: Nieobsługiwane
- **Funkcje zewnętrzne**: Nieobsługiwane

### Ograniczenia Ewaluacji
- **Warunki IF**: Proste porównania (>, <, =, >=, <=)
- **Typy danych**: Liczby, tekst, formuły
- **Błędy**: Logowane, nie przerywają przetwarzania

## Przykłady Użycia

### Podstawowe Użycie

```python
from ai_audytor.validators.wstepne_procedury import process_wstepne_procedury

# Przetwórz plik JSON
result = process_wstepne_procedury('ai_audytor_wsad_wstepne_procedury.json')

if result['status'] == 'success':
    print(f"Przetworzono {result['report']['summary']['total_sheets']} arkuszy")
    print(f"Ewaluowano {result['report']['summary']['successful_evaluations']} formuł")
else:
    print(f"Błąd: {result['error']}")
```

### Szczegółowa Ewaluacja

```python
from ai_audytor.validators.wstepne_procedury import parse_wstepne, eval_formulas, to_report

# 1. Załaduj dane
data = parse_wstepne(Path('ai_audytor_wsad_wstepne_procedury.json'))

# 2. Ewaluuj formuły
results = eval_formulas(data)

# 3. Stwórz raport
report = to_report(data, results)

# 4. Analizuj wyniki
for sheet_name, sheet_summary in report['sheets_summary'].items():
    print(f"Arkusz {sheet_name}: {sheet_summary['formulas_count']} formuł")
```

### Testowanie Formuł

```python
from ai_audytor.validators.wstepne_procedury import FormulaEvaluator

# Utwórz ewaluator
evaluator = FormulaEvaluator(data)

# Testuj formuły
result1 = evaluator.evaluate_formula('=SUM(A1:A10)')
result2 = evaluator.evaluate_formula('=AVERAGE(B1:B5)')
result3 = evaluator.evaluate_formula('=IF(C1>100, "High", "Low")')
```

## Struktura Wyników

### Raport Podsumowujący

```python
{
    'metadata': {
        'source_file': 'AB Wstepne Procedury (1).xlsx',
        'sheets_count': 14,
        'sheets': [...]
    },
    'summary': {
        'total_sheets': 14,
        'total_formulas': 25,
        'successful_evaluations': 23,
        'formula_errors': 2,
        'success_rate': 92.0
    },
    'sheets_summary': {
        'Dane': {
            'formulas_count': 5,
            'rows': 50,
            'cols': 10
        },
        ...
    },
    'formula_errors': [
        {
            'sheet': 'BILANS',
            'cell': 'C15',
            'formula': '=VLOOKUP(A15,Table1,2,FALSE)',
            'error': 'Unsupported function: VLOOKUP'
        }
    ]
}
```

### Wyniki Ewaluacji

```python
{
    'evaluated_sheets': {
        'sheet_name': {
            'name': 'sheet_name',
            'formulas': {
                'A1': {
                    'formula': '=SUM(B1:C1)',
                    'result': 150.0
                }
            },
            'evaluated_data': [
                {'0': 'A1', '1': '100', '2': '50'},
                ...
            ]
        }
    },
    'total_formulas': 25,
    'successful_evaluations': 23,
    'formula_errors': [...]
}
```

## Rozwiązywanie Problemów

### Częste Błędy

1. **"Unsupported function"**
   - **Przyczyna**: Funkcja nie jest obsługiwana
   - **Rozwiązanie**: Sprawdź listę obsługiwanych funkcji

2. **"Error evaluating formula"**
   - **Przyczyna**: Błąd składni lub logiki
   - **Rozwiązanie**: Sprawdź składnię formuły

3. **"File not found"**
   - **Przyczyna**: Nieprawidłowa ścieżka do pliku
   - **Rozwiązanie**: Sprawdź ścieżkę i uprawnienia

### Debugowanie

```python
import logging

# Włącz logowanie
logging.basicConfig(level=logging.DEBUG)

# Przetwórz z debugowaniem
result = process_wstepne_procedury('file.json')

# Sprawdź błędy
for error in result['report']['formula_errors']:
    print(f"Błąd w {error['sheet']}!{error['cell']}: {error['error']}")
```

## Rozszerzenia

### Dodawanie Nowych Funkcji

1. Dodaj metodę do klasy `FormulaEvaluator`
2. Zaktualizuj `evaluate_formula` o nową funkcję
3. Dodaj testy dla nowej funkcji
4. Zaktualizuj dokumentację

### Przykład Dodania Funkcji MAX

```python
def _evaluate_max(self, args: List[str]) -> float:
    """Ewaluuje funkcję MAX"""
    values = []
    for arg in args:
        # Parsuj argumenty i pobierz wartości
        # ... logika parsowania ...
        values.append(value)
    return max(values) if values else 0

# W evaluate_formula:
elif func_name == 'MAX':
    return self._evaluate_max(args)
```

## Testowanie

### Uruchamianie Testów

```bash
# Wszystkie testy
pytest tests/test_wstepne_procedury.py

# Konkretny test
pytest tests/test_wstepne_procedury.py::TestWstepneProcedury::test_parse_wstepne

# Z verbose
pytest tests/test_wstepne_procedury.py -v

# Z coverage
pytest tests/test_wstepne_procedury.py --cov=ai_audytor.validators.wstepne_procedury
```

### Struktura Testów

- **TestWstepneProcedury**: Główne testy funkcjonalności
- **TestFormulaEvaluatorEdgeCases**: Testy przypadków brzegowych
- **Fixtures**: Przykładowe dane testowe
- **Parametryzacja**: Testy z różnymi danymi wejściowymi

## Wydajność

### Optymalizacje

1. **Lazy Loading**: Dane ładowane na żądanie
2. **Caching**: Wyniki formuł cachowane
3. **Parallel Processing**: Ewaluacja formuł równolegle
4. **Memory Management**: Zwolnienie pamięci po przetworzeniu

### Metryki

- **Czas przetwarzania**: ~2-5 sekund dla 14 arkuszy
- **Zużycie pamięci**: ~50-100 MB dla typowego pliku
- **Success Rate**: >90% dla standardowych formuł

## Bezpieczeństwo

### Walidacja Wejścia

- Sprawdzanie formatu pliku JSON
- Walidacja struktury danych
- Sanityzacja formuł Excel
- Ochrona przed injection attacks

### Obsługa Błędów

- Graceful degradation przy błędach
- Logowanie wszystkich błędów
- Nie przerywanie przetwarzania przy błędach formuł
- Zwracanie szczegółowych informacji o błędach
