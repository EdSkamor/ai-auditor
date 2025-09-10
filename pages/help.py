"""
Pomoc - Strona pomocy i instrukcji
"""

import streamlit as st

from app.ui_utils import render_page_header


def render_help_page():
    """Render help page."""
    render_page_header("Pomoc i Instrukcje", "❓")

    # Help sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "🚀 Pierwsze kroki",
            "🔍 Audyt",
            "📊 Raporty",
            "🆘 Rozwiązywanie problemów",
            "📞 Kontakt",
        ]
    )

    with tab1:
        render_getting_started()

    with tab2:
        render_audit_guide()

    with tab3:
        render_reports_guide()

    with tab4:
        render_troubleshooting()

    with tab5:
        render_contact()


def render_getting_started():
    """Render getting started guide."""
    st.markdown("### 🚀 Pierwsze kroki")

    st.markdown(
        """
    **1. Logowanie do systemu**
    - Użyj hasła dostępu: `TwojPIN123!`
    - System automatycznie zapamięta Twoją sesję
    - W przypadku problemów skontaktuj się z administratorem

    **2. Nawigacja w systemie**
    - **Chat AI**: Rozmowa z asystentem AI
    - **Analiza POP**: Analiza dokumentów księgowych
    - **Raporty**: Generowanie raportów audytowych
    - **Diagnostyka**: Sprawdzanie stanu systemu
    - **Pomoc**: Ta strona z instrukcjami

    **3. Skróty klawiszowe**
    - `Ctrl+1`: Chat AI
    - `Ctrl+2`: Analiza POP
    - `Ctrl+3`: Raporty
    - `Ctrl+4`: Diagnostyka
    - `Ctrl+D`: Przełącz tryb ciemny/jasny
    - `Ctrl+R`: Odśwież stronę

    **4. Interfejs użytkownika**
    - **Sidebar**: Nawigacja i diagnostyka
    - **Główny obszar**: Zawartość strony
    - **Status bar**: Informacje o połączeniu z AI
    """
    )

    # Quick start video
    st.markdown("### 📹 Szybki start")
    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")  # Placeholder


def render_audit_guide():
    """Render audit guide."""
    st.markdown("### 🔍 Przeprowadzanie audytu")

    st.markdown(
        """
    **1. Przygotowanie plików**
    - Zbierz wszystkie dokumenty (PDF, ZIP, CSV, Excel, XML)
    - Sprawdź jakość skanów (czytelność, rozdzielczość)
    - Uporządkuj pliki tematycznie
    - Maksymalny rozmiar pliku: 100MB

    **2. Uruchamianie analizy**
    - Przejdź do zakładki "Analiza POP"
    - Przeciągnij pliki do obszaru upload
    - Wybierz typ analizy (Kompleksowa, Faktury, Kontrahenci, itp.)
    - Ustaw parametry analizy
    - Kliknij "Uruchom Analizę"
    - Obserwuj postęp w czasie rzeczywistym

    **3. Analiza wyników**
    - Przejrzyj znalezione niezgodności
    - Sprawdź poziom ryzyka (Wysoki, Średni, Niski)
    - Dodaj komentarze do znalezisk
    - Eksportuj wyniki w wybranym formacie

    **4. Typy analiz**
    - **Kompleksowa**: Pełna analiza wszystkich dokumentów
    - **Faktury**: Analiza faktur VAT i sprzedażowych
    - **Kontrahenci**: Weryfikacja danych kontrahentów
    - **Płatności**: Analiza transakcji płatniczych
    - **Zgodność**: Sprawdzenie zgodności z przepisami
    """
    )

    # Analysis flowchart
    st.markdown("### 📊 Schemat analizy")
    st.image(
        "https://via.placeholder.com/600x400?text=Analysis+Flowchart",
        caption="Schemat procesu analizy",
    )


def render_reports_guide():
    """Render reports guide."""
    st.markdown("### 📊 Rodzaje raportów")

    st.markdown(
        """
    **📋 PBC (Prepared by Client)**
    - **Lista PBC**: Co klient musi przygotować
    - **Status PBC**: Co już zostało dostarczone
    - **Timeline PBC**: Harmonogram dostaw dokumentów

    **📁 Working Papers**
    - **Working Papers**: Dokumenty robocze audytu
    - **Łańcuch dowodowy**: Dowody na każdy wniosek audytowy
    - **Statystyki WP**: Podsumowanie dokumentów roboczych

    **📈 Raporty końcowe**
    - **Raport końcowy**: Główny raport audytu
    - **Executive Summary**: Podsumowanie dla zarządu
    - **Compliance Report**: Raport zgodności z przepisami

    **📦 Evidence ZIP**
    - Kompletny pakiet dowodów audytowych
    - Zawiera: raport Excel, findings JSON, manifest, audit trail
    - Gotowy do archiwizacji i przekazania klientowi

    **💾 Formaty eksportu**
    - **Excel (.xlsx)**: Tabele, wykresy, dane
    - **PDF**: Raporty końcowe, dokumenty
    - **JSON**: Dane surowe, API
    - **ZIP**: Archiwa z wszystkimi plikami
    """
    )

    # Report templates
    st.markdown("### 📋 Szablony raportów")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 Pobierz szablon PBC"):
            st.info("Szablon PBC pobrany")

        if st.button("📊 Pobierz szablon WP"):
            st.info("Szablon WP pobrany")

    with col2:
        if st.button("📈 Pobierz szablon raportu"):
            st.info("Szablon raportu pobrany")

        if st.button("📦 Pobierz szablon ZIP"):
            st.info("Szablon ZIP pobrany")


def render_troubleshooting():
    """Render troubleshooting guide."""
    st.markdown("### 🆘 Rozwiązywanie problemów")

    # Common issues
    st.markdown("#### ❌ Częste problemy")

    with st.expander("System nie uruchamia się"):
        st.markdown(
            """
        **Możliwe przyczyny:**
        - Brak połączenia internetowego
        - Problemy z przeglądarką
        - Błąd serwera

        **Rozwiązania:**
        1. Sprawdź połączenie internetowe
        2. Zrestartuj przeglądarkę
        3. Wyczyść cache przeglądarki
        4. Skontaktuj się z administratorem
        """
        )

    with st.expander("Pliki się nie wgrywają"):
        st.markdown(
            """
        **Możliwe przyczyny:**
        - Nieobsługiwany format pliku
        - Plik za duży (>100MB)
        - Problemy z siecią

        **Rozwiązania:**
        1. Sprawdź format pliku (PDF, ZIP, CSV, Excel, XML)
        2. Sprawdź rozmiar pliku (max 100MB)
        3. Spróbuj ponownie za kilka minut
        4. Podziel duże pliki na mniejsze
        """
        )

    with st.expander("Asystent AI nie odpowiada"):
        st.markdown(
            """
        **Możliwe przyczyny:**
        - Serwer AI niedostępny
        - Problemy z siecią
        - Model AI się dogrzewa

        **Rozwiązania:**
        1. Sprawdź połączenie internetowe
        2. Przejdź do "Diagnostyka" i sprawdź status AI
        3. Zadaj pytanie ponownie
        4. Użyj prostszego języka
        5. Poczekaj na dogrzanie modelu
        """
        )

    with st.expander("Raporty się nie generują"):
        st.markdown(
            """
        **Możliwe przyczyny:**
        - Analiza nie została zakończona
        - Błąd w danych
        - Problemy z serwerem

        **Rozwiązania:**
        1. Sprawdź czy analiza się zakończyła
        2. Poczekaj kilka minut
        3. Spróbuj ponownie
        4. Sprawdź logi w "Diagnostyka"
        """
        )

    # System requirements
    st.markdown("#### 💻 Wymagania systemowe")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        **Przeglądarka:**
        - Chrome 90+
        - Firefox 88+
        - Safari 14+
        - Edge 90+

        **System operacyjny:**
        - Windows 10+
        - macOS 10.15+
        - Linux (Ubuntu 18.04+)
        """
        )

    with col2:
        st.markdown(
            """
        **Połączenie:**
        - Internet 10 Mbps+
        - Stabilne połączenie
        - Porty 80, 443 otwarte

        **Rozdzielczość:**
        - Minimum: 1024x768
        - Zalecana: 1920x1080
        - Wsparcie dla urządzeń mobilnych
        """
        )


def render_contact():
    """Render contact information."""
    st.markdown("### 📞 Kontakt i wsparcie")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        **📧 Email:**
        - Wsparcie techniczne: support@ai-auditor.com
        - Administracja: admin@ai-auditor.com
        - Rozwój: dev@ai-auditor.com

        **📱 Telefon:**
        - Wsparcie: +48 XXX XXX XXX
        - Administracja: +48 XXX XXX XXX

        **🕒 Godziny pracy:**
        - Poniedziałek - Piątek: 8:00 - 18:00
        - Sobota: 9:00 - 15:00
        - Niedziela: Zamknięte
        """
        )

    with col2:
        st.markdown(
            """
        **🌐 Strona internetowa:**
        - Główna: https://ai-auditor.com
        - Dokumentacja: https://docs.ai-auditor.com
        - Status: https://status.ai-auditor.com

        **💬 Komunikatory:**
        - Slack: #ai-auditor-support
        - Teams: AI Auditor Support
        - Discord: AI Auditor Community
        """
        )

    # Contact form
    st.markdown("### 📝 Formularz kontaktowy")

    with st.form("contact_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Imię i nazwisko *")
            email = st.text_input("Email *")
            phone = st.text_input("Telefon")

        with col2:
            subject = st.selectbox(
                "Temat *",
                [
                    "Problem techniczny",
                    "Pytanie o funkcjonalność",
                    "Zgłoszenie błędu",
                    "Prośba o nową funkcję",
                    "Inne",
                ],
            )
            priority = st.selectbox(
                "Priorytet", ["Niski", "Średni", "Wysoki", "Krytyczny"]
            )

        message = st.text_area("Wiadomość *", height=100)

        submitted = st.form_submit_button("📤 Wyślij wiadomość")

        if submitted:
            if name and email and subject and message:
                st.success("✅ Wiadomość została wysłana!")
                st.info("Odpowiemy w ciągu 24 godzin.")
            else:
                st.error("❌ Wypełnij wszystkie wymagane pola (*)")

    # FAQ
    st.markdown("### ❓ Często zadawane pytania")

    faq_items = [
        {
            "question": "Jak zmienić hasło dostępu?",
            "answer": "Skontaktuj się z administratorem systemu, który może zmienić hasło w panelu administracyjnym.",
        },
        {
            "question": "Czy mogę analizować pliki większe niż 100MB?",
            "answer": "Nie, maksymalny rozmiar pliku to 100MB. Podziel duże pliki na mniejsze części.",
        },
        {
            "question": "Jak długo trwa analiza dokumentów?",
            "answer": "Czas analizy zależy od liczby i rozmiaru plików. Zazwyczaj 1-5 minut na 100 stron.",
        },
        {
            "question": "Czy dane są bezpieczne?",
            "answer": "Tak, wszystkie dane są szyfrowane i przechowywane zgodnie z RODO.",
        },
        {
            "question": "Czy mogę eksportować wyniki do innych systemów?",
            "answer": "Tak, wyniki można eksportować w formatach Excel, PDF, JSON i ZIP.",
        },
    ]

    for item in faq_items:
        with st.expander(f"❓ {item['question']}"):
            st.write(item["answer"])
