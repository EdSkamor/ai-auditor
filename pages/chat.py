"""
Chat AI - Strona rozmowy z asystentem AI
"""

import streamlit as st

from app.ui_utils import (
    call_real_ai,
    get_ai_status,
    render_page_header,
)


def render_chat_page():
    """Render chat page."""
    render_page_header("Chat z Asystentem AI", "💬")

    st.markdown(
        "Zadaj pytania z zakresu rachunkowości, audytu, MSRF, PSR, MSSF, KSeF, JPK"
    )

    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

    # AI Status
    ai_status = get_ai_status()
    if ai_status["available"]:
        st.success(f"🤖 AI Online ({ai_status['rtt_avg']:.1f}ms)")
    else:
        st.error("❌ Serwer AI niedostępny")

    st.caption(f"Serwer: {ai_status['server_url']}")

    # Chat input
    if prompt := st.chat_input(
        "Zadaj pytanie o rachunkowość, audyt, MSRF, PSR, MSSF, KSeF, JPK..."
    ):
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.write(prompt)

        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("AI myśli..."):
                if ai_status["available"]:
                    ai_response = call_real_ai(
                        f"Jako ekspert audytu i rachunkowości, odpowiedz na pytanie: {prompt}",
                        temperature=0.8,
                    )
                else:
                    ai_response = generate_mock_response(prompt)
                    ai_response += (
                        "\n\n⚠️ *Używam odpowiedzi przykładowej - serwer AI niedostępny*"
                    )

                st.write(ai_response)

        # Add AI response to history
        st.session_state.chat_history.append(
            {"role": "assistant", "content": ai_response}
        )

    # Clear chat button
    if st.button("🗑️ Wyczyść chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()


def generate_mock_response(prompt: str) -> str:
    """Generate mock AI response."""
    prompt_lower = prompt.lower()

    # MSRF responses
    if "msrf" in prompt_lower:
        return """**MSRF (Międzynarodowe Standardy Sprawozdawczości Finansowej)**

MSRF to zbiór standardów rachunkowości opracowanych przez Radę Międzynarodowych Standardów Rachunkowości (IASB).

**Kluczowe zasady MSRF:**
- Zasada kontynuacji działalności
- Zasada memoriału
- Zasada ostrożności
- Zasada istotności

**Główne standardy:**
- MSRF 1: Prezentacja sprawozdań finansowych
- MSRF 9: Instrumenty finansowe
- MSRF 15: Przychody z umów z klientami
- MSRF 16: Środki trwałe

Czy potrzebujesz szczegółów dotyczących konkretnego standardu?"""

    # PSR responses
    elif "psr" in prompt_lower or "polskie standardy" in prompt_lower:
        return """**PSR (Polskie Standardy Rachunkowości)**

PSR to krajowe standardy rachunkowości obowiązujące w Polsce.

**Kluczowe PSR:**
- PSR 1: Rachunkowość i sprawozdawczość finansowa
- PSR 2: Zmiany zasad rachunkowości
- PSR 3: Zdarzenia po dacie bilansowej
- PSR 4: Rezerwy, zobowiązania warunkowe i aktywa warunkowe

**Zasady:**
- Zasada memoriału
- Zasada ostrożności
- Zasada ciągłości
- Zasada istotności

Czy chcesz poznać szczegóły konkretnego PSR?"""

    # KSeF responses
    elif "ksef" in prompt_lower:
        return """**KSeF (Krajowy System e-Faktur)**

KSeF to system elektronicznych faktur w Polsce.

**Kluczowe informacje:**
- Obowiązkowy od 1 lipca 2024 dla wszystkich podatników
- Faktury w formacie XML
- Integracja z systemami księgowymi
- Walidacja w czasie rzeczywistym

**Korzyści:**
- Automatyzacja procesów
- Redukcja błędów
- Szybsze rozliczenia
- Lepsza kontrola

Czy potrzebujesz pomocy z implementacją KSeF?"""

    # JPK responses
    elif "jpk" in prompt_lower:
        return """**JPK (Jednolity Plik Kontrolny)**

JPK to system elektronicznego przekazywania danych do KAS.

**Typy JPK:**
- JPK_V7: VAT
- JPK_FA: Faktury
- JPK_KR: Księgi rachunkowe
- JPK_WB: Wyciągi bankowe

**Wymagania:**
- Format XML
- Walidacja struktury
- Terminy przekazywania
- Podpis elektroniczny

Czy potrzebujesz pomocy z konkretnym typem JPK?"""

    # Audit responses
    elif "audyt" in prompt_lower or "audit" in prompt_lower:
        return """**Audyt - Podstawowe informacje**

Audyt to niezależne badanie sprawozdań finansowych.

**Etapy audytu:**
1. Planowanie audytu
2. Ocena ryzyka
3. Testy kontroli
4. Testy szczegółowe
5. Zakończenie i raport

**Standardy:**
- Międzynarodowe Standardy Audytu (MSA)
- Polskie Standardy Audytu (PSA)
- Standardy kontroli wewnętrznej

Czy potrzebujesz szczegółów dotyczących konkretnego etapu audytu?"""

    # Default response
    else:
        return """**Witaj w AI Auditor!**

Jestem asystentem AI specjalizującym się w:
- 📊 Rachunkowości i sprawozdawczości finansowej
- 🔍 Audycie i kontroli wewnętrznej
- 📋 Standardach MSRF, PSR, MSSF
- 🌐 Systemach KSeF i JPK
- 📈 Analizie ryzyka finansowego

**Przykładowe pytania:**
- Jak interpretować MSRF 15?
- Co to jest KSeF i kiedy jest obowiązkowy?
- Jak przeprowadzić audyt faktur?
- Jakie są wymagania JPK_V7?

Zadaj konkretne pytanie, a udzielę szczegółowej odpowiedzi!"""
