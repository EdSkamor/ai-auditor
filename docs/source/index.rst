AI Auditor - Dokumentacja
==========================

.. image:: _static/logo.png
   :alt: AI Auditor Logo
   :align: center
   :width: 200px

AI Auditor to zaawansowany system audytu faktur i analizy dokumentów finansowych, wykorzystujący sztuczną inteligencję do automatyzacji procesów audytowych.

.. toctree::
   :maxdepth: 2
   :caption: Spis treści:

   quickstart
   installation
   user_guide/index
   api/index
   howto/index
   architecture/index
   troubleshooting
   changelog

Funkcje główne
--------------

* **Walidacja faktur PDF** - Automatyczna walidacja faktur względem danych POP
* **OCR i ekstrakcja danych** - Rozpoznawanie tekstu z dokumentów PDF i obrazów
* **Integracja z KRS** - Weryfikacja danych kontrahentów w Krajowym Rejestrze Sądowym
* **Biała lista VAT** - Sprawdzanie statusu podatników VAT
* **Generowanie raportów ryzyka** - Tworzenie kompleksowych raportów oceny ryzyka
* **Asystent AI** - Inteligentny system Q&A dla pytań audytowych
* **Interfejs webowy** - Nowoczesny panel użytkownika w Streamlit
* **API REST** - Pełne API do integracji z innymi systemami

Szybki start
------------

1. **Instalacja**::

   pip install -r requirements.txt

2. **Uruchomienie interfejsu webowego**::

   streamlit run streamlit_app.py

3. **Uruchomienie audytu z linii komend**::

   ai-auditor validate --file faktura.pdf --pop-file dane_pop.csv

4. **Testowanie systemu**::

   python scripts/smoke_all.py

Wymagania systemowe
-------------------

* **Python**: 3.10-3.12
* **System operacyjny**: Linux, macOS, Windows
* **RAM**: Minimum 8GB (zalecane 16GB+)
* **Dysk**: 10GB wolnego miejsca
* **GPU**: Opcjonalnie NVIDIA RTX 4090 dla lokalnego AI

Dla klientów RTX 4090
---------------------

Specjalna wersja dla systemów RTX 4090 z lokalnym AI:

* **Lokalny asystent AI** - Działa offline po pobraniu modeli
* **GPU-accelerated OCR** - Szybsze przetwarzanie dokumentów
* **4-bit quantization** - Optymalizacja dla RTX 4090
* **Kompletny pakiet kliencki** - Gotowy do wdrożenia

Więcej informacji w sekcji :doc:`installation`.

Wsparcie
--------

* **Dokumentacja**: Pełna dokumentacja w języku polskim
* **Testy**: Kompleksowe testy WSAD+TEST
* **Przykłady**: Gotowe przykłady użycia
* **API**: Pełna dokumentacja API

Licencja
--------

Projekt komercyjny z przeniesieniem praw autorskich.
Biblioteki zewnętrzne zgodne z licencją Apache-2.0.

Indeksy i tabele
================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

