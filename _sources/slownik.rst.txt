Słownik pól (JSONL / XLSX)
==========================

**Główne pola (na poziomie rekordu):**

- ``sekcja`` – np. Koszty/Przychody
- ``pozycja_id`` – identyfikator w populacji
- ``numer_pop``, ``data_pop``, ``netto_pop`` – dane z populacji
- ``zgodnosc`` – TAK/NIE (po twardych regułach)
- ``uwagi`` – komentarz

**Dopasowanie:**

- ``dopasowanie.status`` – ``znaleziono`` / ``brak``
- ``dopasowanie.kryterium`` – użyte reguły, np. ``numer`` / ``data+netto`` / ``numer+fname``
- ``dopasowanie.confidence`` – skala [0..1] (deterministycznie 0/1 w obecnym trybie)

**PDF / Ekstrakt:**

- ``pdf.plik_oryg`` / ``pdf.sciezka`` – wskazanie pliku PDF
- ``wyciagniete.numer_pdf``, ``wyciagniete.data_pdf``, ``wyciagniete.netto_pdf``

**Porównania (TAK/NIE):**

- ``porownanie.numer``, ``porownanie.data``, ``porownanie.netto``

**Tiebreak (meta):**

- ``tiebreak_meta.by`` – ``fname`` / ``seller`` / ``numer`` / ``other``
- ``tiebreak_meta.numer_norm_equal`` – czy ``numer_pop`` == ``numer_pdf`` po normalizacji

**KPI (run_metadata.json):**

- ``kpi.tiebreak_by_counts`` – rozkład wyborów tie-break
- ``kpi.confidence_avg_all`` / ``kpi.confidence_avg_found`` – średnie confidence

:note: Pola meta mogą nie wystąpić dla rekordów z ``dopasowanie.status = "brak"``.
