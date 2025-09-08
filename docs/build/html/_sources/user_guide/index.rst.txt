Przewodnik użytkownika
======================

Ten przewodnik zawiera szczegółowe instrukcje użytkowania AI Auditor.

.. toctree::
   :maxdepth: 2

   getting_started
   web_interface
   cli_commands
   file_formats
   validation_process
   ocr_processing
   data_enrichment
   risk_assessment
   ai_assistant
   reporting
   configuration
   troubleshooting

Wprowadzenie
------------

AI Auditor to kompleksowy system audytu faktur i analizy dokumentów finansowych. System oferuje:

* **Automatyczną walidację faktur** względem danych populacji (POP)
* **OCR i ekstrakcję danych** z dokumentów PDF i obrazów
* **Integrację z zewnętrznymi API** (KRS, Biała lista VAT)
* **Generowanie raportów ryzyka** z formułami Excel
* **Asystenta AI** do pytań audytowych
* **Interfejs webowy** i **API REST**

Główne komponenty
-----------------

1. **Interfejs webowy** - Streamlit-based panel użytkownika
2. **CLI** - Narzędzia linii komend dla automatyzacji
3. **API REST** - Endpointy do integracji z innymi systemami
4. **Silnik walidacji** - Algorytmy dopasowywania PDF↔POP
5. **OCR Engine** - Rozpoznawanie tekstu z dokumentów
6. **Integracje** - KRS, VAT Whitelist, inne API
7. **AI Assistant** - System Q&A z RAG
8. **Generator raportów** - Excel, PDF, JSON

Przepływ pracy
--------------

Typowy przepływ pracy z AI Auditor:

1. **Przygotowanie danych**
   - Przygotuj pliki PDF z fakturami
   - Przygotuj plik POP (dane populacji)
   - Skonfiguruj parametry audytu

2. **Wykonanie audytu**
   - Uruchom walidację (web/CLI/API)
   - Monitoruj postęp
   - Sprawdź logi w przypadku błędów

3. **Analiza wyników**
   - Przejrzyj raporty
   - Sprawdź niezgodności
   - Użyj AI Assistant do pytań

4. **Eksport i raportowanie**
   - Pobierz raporty Excel/PDF
   - Wyeksportuj dane do innych systemów
   - Wygeneruj raporty ryzyka

Wsparcie
--------

* **Dokumentacja**: Pełna dokumentacja w języku polskim
* **Przykłady**: Gotowe przykłady w katalogu `examples/`
* **Testy**: Kompleksowe testy WSAD+TEST
* **Logi**: Szczegółowe logi dla debugowania
