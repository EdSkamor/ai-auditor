"""
Fuzzy Match Demo - Demonstracja fuzzy matching z RapidFuzz
"""

import streamlit as st

from app.ui_utils import apply_modern_css, render_navigation, render_page_header
from core.fuzzy_match import FuzzyMatcher, InvoiceMatcher


def render_fuzzy_match_demo():
    """Render fuzzy match demo page."""
    render_page_header("Fuzzy Match Demo", "🔍")

    st.markdown("### 🎯 Demonstracja Fuzzy Matching z RapidFuzz")

    # Initialize session state
    if "fuzzy_matcher" not in st.session_state:
        st.session_state.fuzzy_matcher = FuzzyMatcher()
    if "invoice_matcher" not in st.session_state:
        st.session_state.invoice_matcher = InvoiceMatcher()

    # Sensitivity slider
    st.markdown("#### ⚙️ Ustawienia")
    col1, col2 = st.columns(2)

    with col1:
        sensitivity = st.slider(
            "Próg czułości",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.fuzzy_matcher.get_sensitivity(),
            step=0.05,
            help="Próg czułości dla dopasowań (0.0 = bardzo niski, 1.0 = bardzo wysoki)",
        )
        st.session_state.fuzzy_matcher.set_sensitivity(sensitivity)
        st.session_state.invoice_matcher.fuzzy_matcher.set_sensitivity(sensitivity)

    with col2:
        match_type = st.selectbox(
            "Typ dopasowania",
            options=st.session_state.fuzzy_matcher.get_available_match_types(),
            index=7,  # WRatio as default
            help="Typ algorytmu dopasowania",
        )

    st.markdown(f"**Aktualny próg czułości:** {sensitivity:.0%}")

    # Demo sections
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "🔤 Porównanie stringów",
            "📄 Numery faktur",
            "🏢 Nazwy kontrahentów",
            "📍 Adresy",
        ]
    )

    with tab1:
        render_string_comparison_demo()

    with tab2:
        render_invoice_numbers_demo()

    with tab3:
        render_contractor_names_demo()

    with tab4:
        render_addresses_demo()


def render_string_comparison_demo():
    """Render string comparison demo."""
    st.markdown("#### 🔤 Porównanie dwóch stringów")
    
    col1, col2 = st.columns(2)
    
    with col1:
        str1 = st.text_input("String 1:", value="ACME Corporation Sp. z o.o.")
    
    with col2:
        str2 = st.text_input("String 2:", value="ACME Corp. Sp. z o.o.")
    
    if st.button("🔍 Porównaj", use_container_width=True):
        if str1 and str2:
            result = st.session_state.fuzzy_matcher.compare_strings(
                str1, str2, "WRatio"
            )

            # Display result
            col1, col2 = st.columns([1, 2])

            with col1:
                st.metric("Wynik dopasowania", f"{result.score:.1f}%")

                if result.score >= 90:
                    st.success("Bardzo dobre dopasowanie")
                elif result.score >= 80:
                    st.info("Dobre dopasowanie")
                elif result.score >= 70:
                    st.warning("Średnie dopasowanie")
                else:
                    st.error("Słabe dopasowanie")

            with col2:
                st.markdown("**Wyjaśnienie:**")
                st.markdown(result.explanation)

            # Show normalized strings
            with st.expander("🔍 Znormalizowane stringi"):
                st.code(f"String 1: {result.normalized_query}")
                st.code(f"String 2: {result.normalized_match}")


def render_invoice_numbers_demo():
    """Render invoice numbers demo."""
    st.markdown("#### 📄 Dopasowanie numerów faktur")

    # Sample invoice numbers
    sample_invoices = [
        "FV/2024/001",
        "FV/2024/002",
        "FV/2024/010",
        "FA/2024/001",
        "Faktura 2024-001",
        "Invoice 2024-001",
        "FV-2024-001",
        "2024/001/FV",
    ]

    col1, col2 = st.columns(2)

    with col1:
        query_invoice = st.text_input(
            "Numer faktury do wyszukania:", value="FV/2024/001"
        )

    with col2:
        st.markdown("**Przykładowe numery faktur:**")
        for invoice in sample_invoices:
            st.text(f"• {invoice}")

    if st.button("🔍 Znajdź dopasowania", use_container_width=True):
        if query_invoice:
            results = st.session_state.invoice_matcher.match_invoice_numbers(
                query_invoice, sample_invoices
            )

            if results:
                st.markdown(f"**Znaleziono {len(results)} dopasowań:**")

                for i, result in enumerate(results):
                    with st.expander(f"#{i+1}: {result.match} ({result.score:.1f}%)"):
                        st.markdown(result.explanation)
            else:
                st.warning("Brak dopasowań powyżej progu czułości")


def render_contractor_names_demo():
    """Render contractor names demo."""
    st.markdown("#### 🏢 Dopasowanie nazw kontrahentów")

    # Sample contractor names
    sample_contractors = [
        "ACME Corporation Sp. z o.o.",
        "ACME Corp. Sp. z o.o.",
        "ACME Spółka z ograniczoną odpowiedzialnością",
        "ACME Company Ltd.",
        "ACME Polska Sp. z o.o.",
        "Test Company Sp. z o.o.",
        "ABC Corporation",
        "XYZ Ltd.",
    ]

    col1, col2 = st.columns(2)

    with col1:
        query_contractor = st.text_input(
            "Nazwa kontrahenta do wyszukania:", value="ACME Corporation"
        )

    with col2:
        st.markdown("**Przykładowe nazwy kontrahentów:**")
        for contractor in sample_contractors:
            st.text(f"• {contractor}")

    if st.button("🔍 Znajdź kontrahentów", use_container_width=True):
        if query_contractor:
            results = st.session_state.invoice_matcher.match_contractor_names(
                query_contractor, sample_contractors
            )

            if results:
                st.markdown(f"**Znaleziono {len(results)} dopasowań:**")

                for i, result in enumerate(results):
                    with st.expander(f"#{i+1}: {result.match} ({result.score:.1f}%)"):
                        st.markdown(result.explanation)
            else:
                st.warning("Brak dopasowań powyżej progu czułości")


def render_addresses_demo():
    """Render addresses demo."""
    st.markdown("#### 📍 Dopasowanie adresów")

    # Sample addresses
    sample_addresses = [
        "ul. Marszałkowska 1, 00-001 Warszawa",
        "Marszałkowska 1, Warszawa",
        "ul. Marszałkowska 1, 00-001 Warszawa, Polska",
        "Marszałkowska 1, 00-001 Warszawa",
        "ul. Krakowskie Przedmieście 1, 00-001 Warszawa",
        "Krakowskie Przedmieście 1, Warszawa",
        "ul. Nowy Świat 1, 00-001 Warszawa",
        "Nowy Świat 1, Warszawa",
    ]

    col1, col2 = st.columns(2)

    with col1:
        query_address = st.text_input(
            "Adres do wyszukania:", value="Marszałkowska 1, Warszawa"
        )

    with col2:
        st.markdown("**Przykładowe adresy:**")
        for address in sample_addresses:
            st.text(f"• {address}")

    if st.button("🔍 Znajdź adresy", use_container_width=True):
        if query_address:
            results = st.session_state.invoice_matcher.match_addresses(
                query_address, sample_addresses
            )

            if results:
                st.markdown(f"**Znaleziono {len(results)} dopasowań:**")

                for i, result in enumerate(results):
                    with st.expander(f"#{i+1}: {result.match} ({result.score:.1f}%)"):
                        st.markdown(result.explanation)
            else:
                st.warning("Brak dopasowań powyżej progu czułości")


def main():
    """Main function for Fuzzy Match Demo page."""
    apply_modern_css()
    render_navigation()
    render_fuzzy_match_demo()


if __name__ == "__main__":
    main()
