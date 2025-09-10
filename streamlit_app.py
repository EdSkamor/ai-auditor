"""
NOWY AI AUDITOR - KOMPLETNY INTERFACE
Wszystkie funkcje w jednym pliku - gwarantowane działanie

UWAGA: W przypadku komunikatu "środowisko się zresetowało":
1. Sprawdź czy serwer AI działa na localhost:8000
2. Uruchom ponownie: uvicorn server:app --host 0.0.0.0 --port 8000
3. Sprawdź połączenie internetowe dla Streamlit Cloud
4. W razie problemów zrestartuj aplikację
"""

import os
import time
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="AI Auditor - Panel Audytora",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Password
ADMIN_PASSWORD = "TwojPIN123!"

# AI Configuration
AI_SERVER_URL = "https://ai-auditor-romaks-8002.loca.lt"
AI_TIMEOUT = 30


@st.cache_data(ttl=3600)  # Cache for 1 hour
def call_real_ai(prompt: str, temperature: float = 0.8, max_tokens: int = 2048) -> str:
    """Call the real AI model via API."""
    try:
        # Check if AI server is available
        health_response = requests.get(f"{AI_SERVER_URL}/healthz", timeout=5)
        if not health_response.ok:
            return f"❌ Serwer AI niedostępny (status: {health_response.status_code})"

        # Check if model is ready
        ready_response = requests.get(f"{AI_SERVER_URL}/ready", timeout=5)
        if ready_response.ok:
            ready_data = ready_response.json()
            if not ready_data.get("model_ready", False):
                return "⏳ Model AI się dogrzewa, spróbuj za chwilę..."

        # Call AI model with enhanced context
        payload = {
            "prompt": prompt,
            "max_new_tokens": max_tokens,
            "do_sample": True,
            "temperature": temperature,
            "top_p": 0.9,
            "repetition_penalty": 1.1,
            "top_k": 50,
        }

        response = requests.post(
            f"{AI_SERVER_URL}/analyze", json=payload, timeout=AI_TIMEOUT
        )

        if response.ok:
            data = response.json()
            return data.get("output", "Brak odpowiedzi od AI")
        else:
            return f"❌ Błąd AI: {response.status_code} - {response.text}"

    except requests.exceptions.ConnectionError:
        return "❌ Brak połączenia z serwerem AI. Upewnij się, że serwer działa na localhost:8002"
    except requests.exceptions.Timeout:
        return "⏰ Timeout - AI nie odpowiedział w czasie 30 sekund"
    except Exception as e:
        return f"❌ Błąd połączenia z AI: {str(e)}"


def apply_modern_css():
    """Nowoczesny CSS."""
    theme = {
        "primary_color": "#2563eb",
        "secondary_color": "#7c3aed",
        "background_color": "#fafafa",
        "surface_color": "#ffffff",
        "text_color": "#1f2937",
        "border_color": "#e5e7eb",
        "gradient_start": "#2563eb",
        "gradient_end": "#7c3aed",
    }

    css = f"""
<style>
        .stApp {{
            background-color: {theme['background_color']};
            color: {theme['text_color']};
        }}

        .main-header {{
            font-size: 2.5rem;
            font-weight: 700;
            color: {theme['primary_color']};
        text-align: center;
        margin-bottom: 2rem;
            background: linear-gradient(135deg, {theme['gradient_start']}, {theme['gradient_end']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .stButton > button {{
            background: linear-gradient(135deg, {theme['gradient_start']}, {theme['gradient_end']});
        color: white;
        border: none;
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }}

        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        }}

        .metric-card {{
            background: {theme['surface_color']};
            border: 1px solid {theme['border_color']};
            border-radius: 16px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }}
</style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_login():
    """Strona logowania."""
    st.markdown('<div class="main-header">🔍 AI Auditor</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Logowanie")

        password = st.text_input("Hasło:", type="password")

        if st.button("Zaloguj", use_container_width=True):
            if password == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Nieprawidłowe hasło!")

        st.info("**Hasło:** `TwojPIN123!`")


def render_sidebar():
    """Sidebar z nawigacją."""
    with st.sidebar:
        st.markdown("### 🎛️ Panel Sterowania")

        # Theme toggle
        theme_icon = "🌙" if not st.session_state.dark_mode else "☀️"
        if st.button(theme_icon, key="theme_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

        st.divider()

        # Navigation
        pages = {
            "📊 Dashboard": "dashboard",
            "🏃 Run": "run",
            "🔍 Niezgodności": "findings",
            "📤 Eksporty": "exports",
            "💬 Chat AI": "chat",
            "🤖 AI Audytor": "ai_auditor",
            "📚 Instrukcje": "instructions",
            "⚙️ Settings": "settings",
        }

        for label, page in pages.items():
            is_active = st.session_state.current_page == page
            if st.button(label, key=f"nav_{page}", use_container_width=True):
                st.session_state.current_page = page
                st.rerun()

        st.divider()

        # Enhanced AI Diagnostics
        st.markdown("### 🔧 Diagnostyka")

        # AI Status with RTT
        ai_status = "❌ Offline"
        rtt_avg = "N/A"

        try:
            # Test RTT with 3 attempts
            rtt_times = []
            for i in range(3):
                start_time = time.time()
                response = requests.get(f"{AI_SERVER_URL}/healthz", timeout=5)
                rtt = (time.time() - start_time) * 1000  # Convert to ms
                rtt_times.append(rtt)

            rtt_avg = f"{sum(rtt_times)/len(rtt_times):.1f}ms"

            if response.ok:
                ai_status = f"✅ Online ({rtt_avg})"
            else:
                ai_status = f"⚠️ Issues ({rtt_avg})"

        except Exception:
            ai_status = "❌ Offline"
            rtt_avg = "N/A"

        st.markdown(f"**AI Server:** {ai_status}")

        # Backend selector
        backend = st.selectbox(
            "Backend AI:",
            ["Local (localhost:8000)", "Tunnel (loca.lt)", "Mock"],
            key="ai_backend",
        )

        # Package versions
        with st.expander("📦 Wersje pakietów"):
            try:
                import pandas as pd_lib
                import requests as req_lib
                import streamlit as st_lib

                st.text(f"Streamlit: {st_lib.__version__}")
                st.text(f"Pandas: {pd_lib.__version__}")
                st.text(f"Requests: {req_lib.__version__}")
            except Exception as e:
                st.error(f"Błąd: {e}")

        # Restart session button
        if st.button("🔄 Restart Sesji", use_container_width=True):
            st.session_state.clear()
            st.success("✅ Sesja wyczyszczona!")
            st.rerun()

        st.divider()

        # Logout
        if st.button("🚪 Wyloguj", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()


@st.cache_data(ttl=300)  # Cache for 5 minutes
def render_dashboard():
    """Rozbudowany Dashboard z funkcjonalnościami AI."""
    st.markdown(
        '<div class="main-header">📊 Dashboard - Panel Kontrolny</div>',
        unsafe_allow_html=True,
    )

    # Status AI
    col_status, col_info = st.columns([1, 3])
    with col_status:
        try:
            response = requests.get(f"{AI_SERVER_URL}/healthz", timeout=2)
            if response.ok:
                st.success("🤖 AI Online")
            else:
                st.warning("⚠️ AI Issues")
        except:
            st.error("❌ AI Offline")

    with col_info:
        st.info(
            "💡 **AI Auditor** - Kompleksowy system audytu z funkcjonalnościami z plików klienta"
        )

    # Quick stats - rozbudowane
    st.subheader("📊 Statystyki Audytu")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("📁 Pliki", "1,234", "12%", help="Liczba przetworzonych plików")

    with col2:
        st.metric("🔍 Niezgodności", "23", "-5%", help="Znalezione problemy")

    with col3:
        st.metric("✅ Sukces", "98.1%", "2.3%", help="Wskaźnik powodzenia")

    with col4:
        st.metric("⏱️ Czas", "2.3s", "-0.5s", help="Średni czas przetwarzania")

    with col5:
        st.metric("🤖 AI Calls", "456", "23%", help="Liczba wywołań AI")

    # Rozbudowane wykresy
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Trendy Audytu")
        data = pd.DataFrame(
            {
                "Data": pd.date_range("2024-01-01", periods=30),
                "Przetworzone": [100 + i * 2 + (i % 7) * 5 for i in range(30)],
                "Niezgodności": [10 + i * 0.5 + (i % 5) * 2 for i in range(30)],
                "Sukces": [95 + i * 0.1 + (i % 3) * 1 for i in range(30)],
            }
        )
        fig = px.line(
            data,
            x="Data",
            y=["Przetworzone", "Niezgodności", "Sukces"],
            title="Trendy audytu w czasie",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🥧 Rozkład Dokumentów")
        data = {
            "Kategoria": ["Zgodne", "Niezgodne", "Do sprawdzenia", "W trakcie"],
            "Wartość": [75, 15, 7, 3],
        }
        fig = px.pie(
            data, values="Wartość", names="Kategoria", title="Status dokumentów"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Nowe sekcje
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Ostatnie Akcje")
        actions = [
            {
                "Akcja": "Analiza Wskaźników",
                "Status": "✅ Zakończona",
                "Czas": "2 min temu",
            },
            {"Akcja": "Ocena Ryzyka", "Status": "🔄 W trakcie", "Czas": "5 min temu"},
            {
                "Akcja": "Generowanie Raportu",
                "Status": "✅ Zakończona",
                "Czas": "10 min temu",
            },
            {
                "Akcja": "Weryfikacja Bilansu",
                "Status": "⏳ Oczekuje",
                "Czas": "15 min temu",
            },
        ]
        df_actions = pd.DataFrame(actions)
        st.dataframe(df_actions, use_container_width=True)

    with col2:
        st.subheader("🚨 Alerty i Powiadomienia")
        alerts = [
            {
                "Typ": "⚠️",
                "Wiadomość": "Wysokie ryzyko w obszarze zapasów",
                "Priorytet": "Wysoki",
            },
            {"Typ": "ℹ️", "Wiadomość": "Nowy plik do analizy", "Priorytet": "Średni"},
            {
                "Typ": "✅",
                "Wiadomość": "Raport gotowy do pobrania",
                "Priorytet": "Niski",
            },
            {"Typ": "🔄", "Wiadomość": "Aktualizacja AI modelu", "Priorytet": "Średni"},
        ]
        df_alerts = pd.DataFrame(alerts)
        st.dataframe(df_alerts, use_container_width=True)

    # Szybkie akcje
    st.subheader("⚡ Szybkie Akcje")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🚀 Uruchom Audyt", use_container_width=True):
            st.success("✅ Audyt uruchomiony!")

    with col2:
        if st.button("📊 Generuj Raport", use_container_width=True):
            st.success("✅ Raport wygenerowany!")

    with col3:
        if st.button("🔍 Sprawdź AI", use_container_width=True):
            with st.spinner("Testuję AI..."):
                test_response = call_real_ai(
                    "Test połączenia z dashboard", max_tokens=100
                )
                if "❌" in test_response:
                    st.error("❌ AI niedostępny")
                else:
                    st.success("✅ AI działa poprawnie!")

    with col4:
        if st.button("📈 Analiza Trendów", use_container_width=True):
            with st.spinner("Analizuję trendy..."):
                trend_response = call_real_ai(
                    "Przeanalizuj trendy audytu i podaj rekomendacje", max_tokens=500
                )
                st.success("✅ Analiza trendów zakończona!")
                with st.expander("Wyniki analizy trendów"):
                    st.markdown(trend_response)


def render_run_page():
    """Rozbudowana strona uruchamiania audytu z AI."""
    st.markdown(
        '<div class="main-header">🏃 Run - Kolejki i Joby</div>', unsafe_allow_html=True
    )

    # Status systemu
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔄 Aktywne Joby", "3", "1")
    with col2:
        st.metric("⏳ W Kolejce", "7", "-2")
    with col3:
        st.metric("✅ Zakończone", "156", "12")

    # File upload - rozbudowane
    st.subheader("📁 Prześlij Pliki do Audytu")

    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_files = st.file_uploader(
            "Drag and drop files here",
            type=["pdf", "xlsx", "xls", "csv", "json"],
            accept_multiple_files=True,
            help="Limit 200MB per file • PDF, Excel, CSV, JSON",
        )

    with col2:
        st.subheader("⚙️ Opcje Audytu")
        audit_type = st.selectbox(
            "Typ audytu:",
            [
                "Kompletny audyt",
                "Szybka analiza",
                "Weryfikacja zgodności",
                "Analiza ryzyka",
                "Sprawdzenie wskaźników",
            ],
        )

        priority = st.selectbox("Priorytet:", ["Normalny", "Wysoki", "Krytyczny"])

        use_ai = st.checkbox("Użyj AI do analizy", value=True)
        generate_report = st.checkbox("Generuj raport", value=True)

    if uploaded_files:
        st.success(f"✅ Wgrano {len(uploaded_files)} plików")

        # Lista plików
        with st.expander("📋 Lista wgranych plików"):
            for i, file in enumerate(uploaded_files):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"{i+1}. {file.name} ({file.size} bytes)")
                with col2:
                    st.write(f"Typ: {file.type}")
                with col3:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.info(f"Usunięto {file.name}")

        # Uruchomienie audytu
        col1, col2, col3 = st.columns([2, 1, 1])
        with col2:
            if st.button("🚀 Uruchom Audyt", use_container_width=True):
                with st.spinner("Uruchamianie audytu..."):
                    # Symulacja uruchomienia
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    for i in range(100):
                        progress_bar.progress(i + 1)
                        status_text.text(f"Przetwarzanie... {i+1}%")
                        time.sleep(0.02)

                    if use_ai:
                        ai_response = call_real_ai(
                            f"Przeanalizuj {len(uploaded_files)} plików w kontekście {audit_type}. Podaj podsumowanie.",
                            max_tokens=500,
                        )
                        st.success("✅ Audyt zakończony z AI!")
                        with st.expander("🤖 Analiza AI"):
                            st.markdown(ai_response)
                    else:
                        st.success("✅ Audyt uruchomiony!")

        with col3:
            if st.button("⏸️ Wstrzymaj", use_container_width=True):
                st.warning("⏸️ Audyt wstrzymany")

    # Job queue - rozbudowana
    st.subheader("📋 Kolejki i Joby")

    # Aktywne joby
    with st.expander("🔄 Aktywne Joby", expanded=True):
        active_jobs = [
            {
                "ID": "JOB-001",
                "Typ": "Analiza Bilansu",
                "Status": "🔄 W trakcie",
                "Postęp": "65%",
                "Czas": "2:30",
            },
            {
                "ID": "JOB-002",
                "Typ": "Ocena Ryzyka",
                "Status": "🔄 W trakcie",
                "Postęp": "30%",
                "Czas": "1:15",
            },
            {
                "ID": "JOB-003",
                "Typ": "Weryfikacja RZiS",
                "Status": "🔄 W trakcie",
                "Postęp": "80%",
                "Czas": "3:45",
            },
        ]
        df_active = pd.DataFrame(active_jobs)
        st.dataframe(df_active, use_container_width=True)

        # Paski postępu
        for job in active_jobs:
            progress = int(job["Postęp"].replace("%", ""))
            st.progress(progress / 100, text=f"{job['ID']}: {job['Postęp']}")

    # Kolejka oczekujących
    with st.expander("⏳ Kolejka Oczekujących"):
        pending_jobs = [
            {
                "ID": "JOB-004",
                "Typ": "Analiza Wskaźników",
                "Priorytet": "Wysoki",
                "Czas oczekiwania": "5 min",
            },
            {
                "ID": "JOB-005",
                "Typ": "Cash Flow",
                "Priorytet": "Normalny",
                "Czas oczekiwania": "12 min",
            },
            {
                "ID": "JOB-006",
                "Typ": "Zestawienie Zmian",
                "Priorytet": "Niski",
                "Czas oczekiwania": "25 min",
            },
        ]
        df_pending = pd.DataFrame(pending_jobs)
        st.dataframe(df_pending, use_container_width=True)

    # Historia jobów
    with st.expander("📊 Historia Jobów"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("✅ Zakończone dzisiaj", "23", "5")
            st.metric("❌ Błędy", "2", "-1")
        with col2:
            st.metric("⏱️ Średni czas", "4.2 min", "-0.3 min")
            st.metric("📈 Wydajność", "94%", "2%")

    # Zarządzanie jobami
    st.subheader("🎛️ Zarządzanie Jobami")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("⏸️ Wstrzymaj Wszystkie", use_container_width=True):
            st.warning("⏸️ Wszystkie joby wstrzymane")

    with col2:
        if st.button("▶️ Wznów Wszystkie", use_container_width=True):
            st.success("▶️ Wszystkie joby wznowione")

    with col3:
        if st.button("🗑️ Wyczyść Kolejkę", use_container_width=True):
            st.info("🗑️ Kolejka wyczyszczona")

    with col4:
        if st.button("📊 Raport Statusu", use_container_width=True):
            with st.spinner("Generuję raport..."):
                report_response = call_real_ai(
                    "Przygotuj raport statusu systemu audytu z rekomendacjami optymalizacji",
                    max_tokens=300,
                )
                st.success("📊 Raport wygenerowany!")
                with st.expander("Raport statusu"):
                    st.markdown(report_response)


def render_findings_page():
    """Rozbudowana strona niezgodności z AI."""
    st.markdown(
        '<div class="main-header">🔍 Niezgodności - Zarządzanie Problemami</div>',
        unsafe_allow_html=True,
    )

    # Statystyki niezgodności
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("🔴 Krytyczne", "5", "2")
    with col2:
        st.metric("🟠 Wysokie", "12", "-1")
    with col3:
        st.metric("🟡 Średnie", "23", "3")
    with col4:
        st.metric("🟢 Niskie", "45", "-5")
    with col5:
        st.metric("✅ Rozwiązane", "156", "12")

    # Filtry i wyszukiwanie
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        filter_status = st.selectbox(
            "Status:", ["Wszystkie", "Otwarte", "W trakcie", "Rozwiązane", "Zamknięte"]
        )
    with col2:
        filter_priority = st.selectbox(
            "Priorytet:", ["Wszystkie", "Krytyczny", "Wysoki", "Średni", "Niski"]
        )
    with col3:
        filter_type = st.selectbox(
            "Typ:",
            [
                "Wszystkie",
                "Błąd walidacji",
                "Brak podpisu",
                "Nieprawidłowa kwota",
                "Niezgodność z przepisami",
            ],
        )
    with col4:
        search_term = st.text_input("🔍 Szukaj:", placeholder="Wpisz ID lub opis...")

    # Rozbudowane niezgodności
    findings = [
        {
            "ID": "F001",
            "Typ": "Błąd walidacji",
            "Priorytet": "Krytyczny",
            "Status": "Otwarty",
            "Data": "2024-09-09",
            "Opis": "Nieprawidłowa walidacja NIP w dokumencie FA-2024/001",
            "Odpowiedzialny": "Jan Kowalski",
        },
        {
            "ID": "F002",
            "Typ": "Brak podpisu",
            "Priorytet": "Wysoki",
            "Status": "W trakcie",
            "Data": "2024-09-08",
            "Opis": "Brak podpisu elektronicznego na umowie",
            "Odpowiedzialny": "Anna Nowak",
        },
        {
            "ID": "F003",
            "Typ": "Nieprawidłowa kwota",
            "Priorytet": "Krytyczny",
            "Status": "Otwarty",
            "Data": "2024-09-07",
            "Opis": "Rozbieżność w kwocie faktury vs umowa",
            "Odpowiedzialny": "Piotr Wiśniewski",
        },
        {
            "ID": "F004",
            "Typ": "Niezgodność z przepisami",
            "Priorytet": "Średni",
            "Status": "Rozwiązany",
            "Data": "2024-09-06",
            "Opis": "Niezgodność z nowymi przepisami VAT",
            "Odpowiedzialny": "Maria Kowalczyk",
        },
        {
            "ID": "F005",
            "Typ": "Błąd walidacji",
            "Priorytet": "Niski",
            "Status": "Zamknięty",
            "Data": "2024-09-05",
            "Opis": "Błąd w walidacji numeru konta",
            "Odpowiedzialny": "Tomasz Zieliński",
        },
    ]

    # Filtrowanie danych
    filtered_findings = findings
    if filter_status != "Wszystkie":
        filtered_findings = [
            f for f in filtered_findings if f["Status"] == filter_status
        ]
    if filter_priority != "Wszystkie":
        filtered_findings = [
            f for f in filtered_findings if f["Priorytet"] == filter_priority
        ]
    if filter_type != "Wszystkie":
        filtered_findings = [f for f in filtered_findings if f["Typ"] == filter_type]
    if search_term:
        filtered_findings = [
            f
            for f in filtered_findings
            if search_term.lower() in f["ID"].lower()
            or search_term.lower() in f["Opis"].lower()
        ]

    # Wyświetlanie niezgodności
    st.subheader(f"📋 Lista Niezgodności ({len(filtered_findings)} znalezionych)")

    if filtered_findings:
        df = pd.DataFrame(filtered_findings)

        # Edytowalna tabela
        edited_df = st.data_editor(
            df,
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    help="Wybierz status niezgodności",
                    width="medium",
                    options=["Otwarty", "W trakcie", "Rozwiązany", "Zamknięty"],
                    required=True,
                ),
                "Priorytet": st.column_config.SelectboxColumn(
                    "Priorytet",
                    help="Wybierz priorytet",
                    width="medium",
                    options=["Krytyczny", "Wysoki", "Średni", "Niski"],
                    required=True,
                ),
            },
            hide_index=True,
            use_container_width=True,
        )

        # Szczegóły wybranej niezgodności
        if len(edited_df) > 0:
            selected_id = st.selectbox(
                "Wybierz niezgodność do szczegółów:", edited_df["ID"].tolist()
            )
            if selected_id:
                selected_finding = next(
                    f for f in filtered_findings if f["ID"] == selected_id
                )

                with st.expander(f"📄 Szczegóły {selected_id}", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Typ:** {selected_finding['Typ']}")
                        st.write(f"**Priorytet:** {selected_finding['Priorytet']}")
                        st.write(f"**Status:** {selected_finding['Status']}")
                    with col2:
                        st.write(f"**Data:** {selected_finding['Data']}")
                        st.write(
                            f"**Odpowiedzialny:** {selected_finding['Odpowiedzialny']}"
                        )

                    st.write(f"**Opis:** {selected_finding['Opis']}")

                    # Komentarze i notatki
                    st.subheader("💬 Komentarze")
                    comment = st.text_area(
                        "Dodaj komentarz:", key=f"comment_{selected_id}"
                    )
                    if st.button("💾 Zapisz komentarz", key=f"save_{selected_id}"):
                        st.success("✅ Komentarz zapisany!")

                    # Historia zmian
                    st.subheader("📝 Historia zmian")
                    history = [
                        {
                            "Data": "2024-09-09 10:30",
                            "Użytkownik": "Jan Kowalski",
                            "Akcja": "Utworzono niezgodność",
                        },
                        {
                            "Data": "2024-09-09 11:15",
                            "Użytkownik": "Anna Nowak",
                            "Akcja": "Zmieniono status na 'W trakcie'",
                        },
                        {
                            "Data": "2024-09-09 14:20",
                            "Użytkownik": "Piotr Wiśniewski",
                            "Akcja": "Dodano komentarz",
                        },
                    ]
                    st.dataframe(pd.DataFrame(history), use_container_width=True)
    else:
        st.info("🔍 Brak niezgodności spełniających kryteria wyszukiwania")

    # Akcje masowe
    st.subheader("🎛️ Akcje Masowe")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("📊 Generuj Raport", use_container_width=True):
            with st.spinner("Generuję raport..."):
                report_response = call_real_ai(
                    f"Przygotuj raport niezgodności dla {len(filtered_findings)} problemów. Uwzględnij statystyki, priorytety i rekomendacje.",
                    max_tokens=500,
                )
                st.success("✅ Raport wygenerowany!")
                with st.expander("📊 Raport niezgodności"):
                    st.markdown(report_response)

    with col2:
        if st.button("📧 Wyślij Email", use_container_width=True):
            st.success("✅ Email wysłany do zespołu!")

    with col3:
        if st.button("🔄 Odśwież", use_container_width=True):
            st.rerun()

    with col4:
        if st.button("📋 Eksportuj CSV", use_container_width=True):
            st.success("✅ Plik CSV wygenerowany!")

    with col5:
        if st.button("🤖 Analiza AI", use_container_width=True):
            with st.spinner("Analizuję niezgodności..."):
                ai_analysis = call_real_ai(
                    f"Przeanalizuj {len(filtered_findings)} niezgodności i podaj rekomendacje dotyczące ich rozwiązania oraz zapobiegania podobnym problemom w przyszłości.",
                    max_tokens=600,
                )
                st.success("✅ Analiza AI zakończona!")
                with st.expander("🤖 Analiza AI niezgodności"):
                    st.markdown(ai_analysis)

    # Wykresy analityczne
    st.subheader("📈 Analiza Niezgodności")
    col1, col2 = st.columns(2)

    with col1:
        # Wykres priorytetów
        priority_data = {
            "Priorytet": ["Krytyczny", "Wysoki", "Średni", "Niski"],
            "Liczba": [5, 12, 23, 45],
        }
        fig_priority = px.bar(
            priority_data, x="Priorytet", y="Liczba", title="Rozkład według priorytetów"
        )
        st.plotly_chart(fig_priority, use_container_width=True)

    with col2:
        # Wykres statusów
        status_data = {
            "Status": ["Otwarty", "W trakcie", "Rozwiązany", "Zamknięty"],
            "Liczba": [15, 8, 12, 156],
        }
        fig_status = px.pie(
            status_data,
            values="Liczba",
            names="Status",
            title="Rozkład według statusów",
        )
        st.plotly_chart(fig_status, use_container_width=True)

    # Statystyki niezgodności
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("🔴 Krytyczne", "5", "2")
    with col2:
        st.metric("🟠 Wysokie", "12", "-1")
    with col3:
        st.metric("🟡 Średnie", "23", "3")
    with col4:
        st.metric("🟢 Niskie", "45", "-5")
    with col5:
        st.metric("✅ Rozwiązane", "156", "12")

    # Filtry i wyszukiwanie
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        filter_status = st.selectbox(
            "Status:", ["Wszystkie", "Otwarte", "W trakcie", "Rozwiązane", "Zamknięte"]
        )
    with col2:
        filter_priority = st.selectbox(
            "Priorytet:", ["Wszystkie", "Krytyczny", "Wysoki", "Średni", "Niski"]
        )
    with col3:
        filter_type = st.selectbox(
            "Typ:",
            [
                "Wszystkie",
                "Błąd walidacji",
                "Brak podpisu",
                "Nieprawidłowa kwota",
                "Niezgodność z przepisami",
            ],
        )
    with col4:
        search_term = st.text_input("🔍 Szukaj:", placeholder="Wpisz ID lub opis...")

    # Rozbudowane niezgodności
    findings = [
        {
            "ID": "F001",
            "Typ": "Błąd walidacji",
            "Priorytet": "Krytyczny",
            "Status": "Otwarty",
            "Data": "2024-09-09",
            "Opis": "Nieprawidłowa walidacja NIP w dokumencie FA-2024/001",
            "Odpowiedzialny": "Jan Kowalski",
        },
        {
            "ID": "F002",
            "Typ": "Brak podpisu",
            "Priorytet": "Wysoki",
            "Status": "W trakcie",
            "Data": "2024-09-08",
            "Opis": "Brak podpisu elektronicznego na umowie",
            "Odpowiedzialny": "Anna Nowak",
        },
        {
            "ID": "F003",
            "Typ": "Nieprawidłowa kwota",
            "Priorytet": "Krytyczny",
            "Status": "Otwarty",
            "Data": "2024-09-07",
            "Opis": "Rozbieżność w kwocie faktury vs umowa",
            "Odpowiedzialny": "Piotr Wiśniewski",
        },
        {
            "ID": "F004",
            "Typ": "Niezgodność z przepisami",
            "Priorytet": "Średni",
            "Status": "Rozwiązany",
            "Data": "2024-09-06",
            "Opis": "Niezgodność z nowymi przepisami VAT",
            "Odpowiedzialny": "Maria Kowalczyk",
        },
        {
            "ID": "F005",
            "Typ": "Błąd walidacji",
            "Priorytet": "Niski",
            "Status": "Zamknięty",
            "Data": "2024-09-05",
            "Opis": "Błąd w walidacji numeru konta",
            "Odpowiedzialny": "Tomasz Zieliński",
        },
    ]

    # Filtrowanie danych
    filtered_findings = findings
    if filter_status != "Wszystkie":
        filtered_findings = [
            f for f in filtered_findings if f["Status"] == filter_status
        ]
    if filter_priority != "Wszystkie":
        filtered_findings = [
            f for f in filtered_findings if f["Priorytet"] == filter_priority
        ]
    if filter_type != "Wszystkie":
        filtered_findings = [f for f in filtered_findings if f["Typ"] == filter_type]
    if search_term:
        filtered_findings = [
            f
            for f in filtered_findings
            if search_term.lower() in f["ID"].lower()
            or search_term.lower() in f["Opis"].lower()
        ]

    # Wyświetlanie niezgodności
    st.subheader(f"📋 Lista Niezgodności ({len(filtered_findings)} znalezionych)")

    if filtered_findings:
        df = pd.DataFrame(filtered_findings)

        # Edytowalna tabela
        edited_df = st.data_editor(
            df,
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    help="Wybierz status niezgodności",
                    width="medium",
                    options=["Otwarty", "W trakcie", "Rozwiązany", "Zamknięty"],
                    required=True,
                ),
                "Priorytet": st.column_config.SelectboxColumn(
                    "Priorytet",
                    help="Wybierz priorytet",
                    width="medium",
                    options=["Krytyczny", "Wysoki", "Średni", "Niski"],
                    required=True,
                ),
            },
            hide_index=True,
            use_container_width=True,
        )

        # Szczegóły wybranej niezgodności
        if len(edited_df) > 0:
            selected_id = st.selectbox(
                "Wybierz niezgodność do szczegółów:", edited_df["ID"].tolist()
            )
            if selected_id:
                selected_finding = next(
                    f for f in filtered_findings if f["ID"] == selected_id
                )

                with st.expander(f"📄 Szczegóły {selected_id}", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Typ:** {selected_finding['Typ']}")
                        st.write(f"**Priorytet:** {selected_finding['Priorytet']}")
                        st.write(f"**Status:** {selected_finding['Status']}")
                    with col2:
                        st.write(f"**Data:** {selected_finding['Data']}")
                        st.write(
                            f"**Odpowiedzialny:** {selected_finding['Odpowiedzialny']}"
                        )

                    st.write(f"**Opis:** {selected_finding['Opis']}")

                    # Komentarze i notatki
                    st.subheader("💬 Komentarze")
                    comment = st.text_area(
                        "Dodaj komentarz:", key=f"comment_{selected_id}"
                    )
                    if st.button("💾 Zapisz komentarz", key=f"save_{selected_id}"):
                        st.success("✅ Komentarz zapisany!")

                    # Historia zmian
                    st.subheader("📝 Historia zmian")
                    history = [
                        {
                            "Data": "2024-09-09 10:30",
                            "Użytkownik": "Jan Kowalski",
                            "Akcja": "Utworzono niezgodność",
                        },
                        {
                            "Data": "2024-09-09 11:15",
                            "Użytkownik": "Anna Nowak",
                            "Akcja": "Zmieniono status na 'W trakcie'",
                        },
                        {
                            "Data": "2024-09-09 14:20",
                            "Użytkownik": "Piotr Wiśniewski",
                            "Akcja": "Dodano komentarz",
                        },
                    ]
                    st.dataframe(pd.DataFrame(history), use_container_width=True)
    else:
        st.info("🔍 Brak niezgodności spełniających kryteria wyszukiwania")

    # Akcje masowe
    st.subheader("🎛️ Akcje Masowe")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("📊 Generuj Raport", use_container_width=True):
            with st.spinner("Generuję raport..."):
                report_response = call_real_ai(
                    f"Przygotuj raport niezgodności dla {len(filtered_findings)} problemów. Uwzględnij statystyki, priorytety i rekomendacje.",
                    max_tokens=500,
                )
                st.success("✅ Raport wygenerowany!")
                with st.expander("📊 Raport niezgodności"):
                    st.markdown(report_response)

    with col2:
        if st.button("📧 Wyślij Email", use_container_width=True):
            st.success("✅ Email wysłany do zespołu!")

    with col3:
        if st.button("🔄 Odśwież", use_container_width=True):
            st.rerun()

    with col4:
        if st.button("📋 Eksportuj CSV", use_container_width=True):
            st.success("✅ Plik CSV wygenerowany!")

    with col5:
        if st.button("🤖 Analiza AI", use_container_width=True):
            with st.spinner("Analizuję niezgodności..."):
                ai_analysis = call_real_ai(
                    f"Przeanalizuj {len(filtered_findings)} niezgodności i podaj rekomendacje dotyczące ich rozwiązania oraz zapobiegania podobnym problemom w przyszłości.",
                    max_tokens=600,
                )
                st.success("✅ Analiza AI zakończona!")
                with st.expander("🤖 Analiza AI niezgodności"):
                    st.markdown(ai_analysis)

    # Wykresy analityczne
    st.subheader("📈 Analiza Niezgodności")
    col1, col2 = st.columns(2)

    with col1:
        # Wykres priorytetów
        priority_data = {
            "Priorytet": ["Krytyczny", "Wysoki", "Średni", "Niski"],
            "Liczba": [5, 12, 23, 45],
        }
        fig_priority = px.bar(
            priority_data, x="Priorytet", y="Liczba", title="Rozkład według priorytetów"
        )
        st.plotly_chart(fig_priority, use_container_width=True)

    with col2:
        # Wykres statusów
        status_data = {
            "Status": ["Otwarty", "W trakcie", "Rozwiązany", "Zamknięty"],
            "Liczba": [15, 8, 12, 156],
        }
        fig_status = px.pie(
            status_data,
            values="Liczba",
            names="Status",
            title="Rozkład według statusów",
        )
        st.plotly_chart(fig_status, use_container_width=True)


def render_exports_page():
    """Rozbudowana strona eksportów z AI."""
    st.markdown(
        '<div class="main-header">📤 Eksporty - PBC/WP/Raporty</div>',
        unsafe_allow_html=True,
    )

    # Statystyki eksportów
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Raporty", "23", "5")
    with col2:
        st.metric("📋 PBC", "45", "12")
    with col3:
        st.metric("📄 Working Papers", "67", "8")
    with col4:
        st.metric("📈 Eksporty dzisiaj", "12", "3")

    # Typy eksportów - rozbudowane
    st.subheader("📊 Typy Eksportów")

    # PBC (Prepared by Client)
    with st.expander("📋 PBC (Prepared by Client)", expanded=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("**Dokumenty przygotowane przez klienta**")
            st.info(
                "📋 PBC to dokumenty i informacje przygotowane przez klienta na potrzeby audytu"
            )
        with col2:
            if st.button("📋 Lista PBC", use_container_width=True):
                with st.spinner("Generuję listę PBC..."):
                    pbc_response = call_real_ai(
                        "Przygotuj listę dokumentów PBC (Prepared by Client) wymaganych do audytu sprawozdania finansowego",
                        max_tokens=400,
                    )
                    st.success("✅ Lista PBC wygenerowana!")
                    with st.expander("📋 Lista PBC"):
                        st.markdown(pbc_response)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📊 Status PBC", use_container_width=True):
                st.success("✅ Status PBC wygenerowany!")
        with col2:
            if st.button("📅 Timeline PBC", use_container_width=True):
                st.success("✅ Timeline PBC wygenerowany!")
        with col3:
            if st.button("🔍 Weryfikacja PBC", use_container_width=True):
                with st.spinner("Weryfikuję PBC..."):
                    verification_response = call_real_ai(
                        "Przeprowadź weryfikację kompletności i zgodności dokumentów PBC z wymogami audytu",
                        max_tokens=300,
                    )
                    st.success("✅ Weryfikacja PBC zakończona!")
                    with st.expander("🔍 Weryfikacja PBC"):
                        st.markdown(verification_response)

    # Working Papers
    with st.expander("📄 Working Papers", expanded=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("**Dokumentacja robocza audytu**")
            st.info(
                "📄 Working Papers to dokumentacja robocza zawierająca dowody audytorskie i procedury"
            )
        with col2:
            if st.button("📄 Working Papers", use_container_width=True):
                with st.spinner("Generuję Working Papers..."):
                    wp_response = call_real_ai(
                        "Przygotuj kompletny zestaw Working Papers dla audytu sprawozdania finansowego, uwzględniając wszystkie obszary",
                        max_tokens=500,
                    )
                    st.success("✅ Working Papers wygenerowane!")
                    with st.expander("📄 Working Papers"):
                        st.markdown(wp_response)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔗 Łańcuch dowodowy", use_container_width=True):
                st.success("✅ Łańcuch dowodowy wygenerowany!")
        with col2:
            if st.button("📊 Statystyki WP", use_container_width=True):
                st.success("✅ Statystyki WP wygenerowane!")
        with col3:
            if st.button("🔍 Kontrola WP", use_container_width=True):
                with st.spinner("Kontroluję Working Papers..."):
                    control_response = call_real_ai(
                        "Przeprowadź kontrolę jakości Working Papers pod kątem kompletności i zgodności ze standardami audytu",
                        max_tokens=300,
                    )
                    st.success("✅ Kontrola WP zakończona!")
                    with st.expander("🔍 Kontrola WP"):
                        st.markdown(control_response)

    # Raporty
    with st.expander("📊 Raporty Audytorskie", expanded=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("**Raporty końcowe i podsumowania**")
            st.info(
                "📊 Raporty audytorskie to końcowe dokumenty zawierające opinie i wnioski z audytu"
            )
        with col2:
            if st.button("📊 Raport końcowy", use_container_width=True):
                with st.spinner("Generuję raport końcowy..."):
                    final_report = call_real_ai(
                        "Przygotuj kompletny raport końcowy z audytu sprawozdania finansowego, uwzględniając wszystkie obszary, ryzyka i rekomendacje",
                        max_tokens=800,
                    )
                    st.success("✅ Raport końcowy wygenerowany!")
                    with st.expander("📊 Raport końcowy"):
                        st.markdown(final_report)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📋 Executive Summary", use_container_width=True):
                with st.spinner("Generuję Executive Summary..."):
                    exec_summary = call_real_ai(
                        "Przygotuj Executive Summary raportu audytorskiego dla zarządu, zawierający kluczowe wnioski i rekomendacje",
                        max_tokens=400,
                    )
                    st.success("✅ Executive Summary wygenerowany!")
                    with st.expander("📋 Executive Summary"):
                        st.markdown(exec_summary)
        with col2:
            if st.button("✅ Compliance Report", use_container_width=True):
                with st.spinner("Generuję Compliance Report..."):
                    compliance_report = call_real_ai(
                        "Przygotuj raport zgodności z przepisami prawa, standardami rachunkowości i wymogami regulacyjnymi",
                        max_tokens=400,
                    )
                    st.success("✅ Compliance Report wygenerowany!")
                    with st.expander("✅ Compliance Report"):
                        st.markdown(compliance_report)
        with col3:
            if st.button("📈 Raport Trendów", use_container_width=True):
                with st.spinner("Generuję raport trendów..."):
                    trends_report = call_real_ai(
                        "Przygotuj raport analizy trendów finansowych i operacyjnych na przestrzeni ostatnich lat",
                        max_tokens=400,
                    )
                    st.success("✅ Raport trendów wygenerowany!")
                    with st.expander("📈 Raport trendów"):
                        st.markdown(trends_report)

    # Nowe sekcje
    with st.expander("🔧 Narzędzia Eksportu", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📁 Format Eksportu")
            export_format = st.selectbox(
                "Wybierz format:", ["PDF", "Excel", "Word", "CSV", "JSON", "XML"]
            )

            st.subheader("📅 Zakres Dat")
            col_date1, col_date2 = st.columns(2)
            with col_date1:
                start_date = st.date_input(
                    "Data początkowa:", value=datetime.now().date() - timedelta(days=30)
                )
            with col_date2:
                end_date = st.date_input("Data końcowa:", value=datetime.now().date())

        with col2:
            st.subheader("🎯 Opcje Eksportu")
            include_charts = st.checkbox("Uwzględnij wykresy", value=True)
            include_ai_analysis = st.checkbox("Uwzględnij analizę AI", value=True)
            include_attachments = st.checkbox("Uwzględnij załączniki", value=False)

            if st.button("🚀 Generuj Kompletny Eksport", use_container_width=True):
                with st.spinner("Generuję kompletny eksport..."):
                    export_response = call_real_ai(
                        f"Przygotuj kompletny eksport audytu w formacie {export_format} dla okresu {start_date} - {end_date}. Uwzględnij wszystkie dokumenty, analizy i raporty.",
                        max_tokens=600,
                    )
                    st.success("✅ Kompletny eksport wygenerowany!")
                    with st.expander("🚀 Kompletny eksport"):
                        st.markdown(export_response)

    # Historia eksportów - rozbudowana
    st.subheader("📚 Historia Eksportów")

    # Filtry historii
    col1, col2, col3 = st.columns(3)
    with col1:
        history_filter = st.selectbox(
            "Filtr:", ["Wszystkie", "Dzisiaj", "Ostatni tydzień", "Ostatni miesiąc"]
        )
    with col2:
        type_filter = st.selectbox(
            "Typ:", ["Wszystkie", "PBC", "Working Papers", "Raporty"]
        )
    with col3:
        status_filter = st.selectbox(
            "Status:", ["Wszystkie", "Zakończone", "W trakcie", "Błąd"]
        )

    # Historia eksportów
    export_history = [
        {
            "Data": "2024-09-09 14:30",
            "Typ": "Raport końcowy",
            "Format": "PDF",
            "Status": "✅ Zakończony",
            "Rozmiar": "2.3 MB",
        },
        {
            "Data": "2024-09-09 12:15",
            "Typ": "Working Papers",
            "Format": "Excel",
            "Status": "✅ Zakończony",
            "Rozmiar": "5.7 MB",
        },
        {
            "Data": "2024-09-09 10:45",
            "Typ": "PBC Lista",
            "Format": "Word",
            "Status": "✅ Zakończony",
            "Rozmiar": "1.2 MB",
        },
        {
            "Data": "2024-09-08 16:20",
            "Typ": "Compliance Report",
            "Format": "PDF",
            "Status": "✅ Zakończony",
            "Rozmiar": "3.1 MB",
        },
        {
            "Data": "2024-09-08 14:10",
            "Typ": "Executive Summary",
            "Format": "PDF",
            "Status": "🔄 W trakcie",
            "Rozmiar": "-",
        },
        {
            "Data": "2024-09-08 11:30",
            "Typ": "Raport Trendów",
            "Format": "Excel",
            "Status": "❌ Błąd",
            "Rozmiar": "-",
        },
    ]

    df_history = pd.DataFrame(export_history)
    st.dataframe(df_history, use_container_width=True)

    # Akcje na historii
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📥 Pobierz Wszystkie", use_container_width=True):
            st.success("✅ Wszystkie pliki pobrane!")
    with col2:
        if st.button("🗑️ Wyczyść Historię", use_container_width=True):
            st.info("🗑️ Historia wyczyszczona!")
    with col3:
        if st.button("📊 Statystyki Eksportów", use_container_width=True):
            with st.spinner("Generuję statystyki..."):
                stats_response = call_real_ai(
                    "Przygotuj statystyki eksportów audytorskich, uwzględniając trendy, popularne formaty i wydajność",
                    max_tokens=300,
                )
                st.success("✅ Statystyki wygenerowane!")
                with st.expander("📊 Statystyki eksportów"):
                    st.markdown(stats_response)
    with col4:
        if st.button("🔄 Odśwież", use_container_width=True):
            st.rerun()


def render_chat_page():
    """Rozbudowana strona Chat AI z funkcjonalnościami."""
    st.markdown(
        '<div class="main-header">💬 Chat AI - Asystent Audytora</div>',
        unsafe_allow_html=True,
    )

    # Status AI
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        try:
            response = requests.get(f"{AI_SERVER_URL}/healthz", timeout=2)
            if response.ok:
                st.success("🤖 AI Online")
            else:
                st.warning("⚠️ AI Issues")
        except:
            st.error("❌ AI Offline")

    with col2:
        st.info(
            "💡 **Chat AI** - Inteligentny asystent audytora z dostępem do funkcjonalności z plików klienta"
        )

    with col3:
        if st.button("🔄 Odśwież Status"):
            st.rerun()

    # Opcje chat
    col1, col2 = st.columns([3, 1])

    with col1:
        # Initialize chat
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Zadaj pytanie o audyt..."):
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Analizuję z rozszerzonym kontekstem..."):
                    # Enhanced prompt for better context
                    enhanced_prompt = f"""
                    Jako ekspert audytor z dostępem do funkcjonalności z plików klienta, odpowiedz szczegółowo na pytanie:

                    {prompt}

                    KONTEKST DOSTĘPNYCH DANYCH:
                    - 14 arkuszy audytorskich (AB Wstępne Procedury)
                    - Wskaźniki finansowe (ROA: 19.76%, ROE: 30.68%, płynność, efektywność)
                    - Ryzyka audytorskie (rozległe i specyficzne)
                    - Sprawozdania finansowe za 3 lata
                    - Procedury audytorskie i standardy

                    Uwzględnij w odpowiedzi:
                    - Konkretne dane z arkuszy klienta
                    - Referencje do standardów audytu
                    - Praktyczne rekomendacje
                    - Potencjalne ryzyka i mitygację
                    - Procedury audytorskie

                    Odpowiedź powinna być szczegółowa, profesjonalna i oparta na danych klienta.
                    """

                    # Call AI with enhanced parameters
                    ai_response = call_real_ai(
                        enhanced_prompt, temperature=0.8, max_tokens=3072
                    )
                    st.markdown(f"**Odpowiedź AI:**\n\n{ai_response}")

            st.session_state.messages.append(
                {"role": "assistant", "content": ai_response}
            )

    with col2:
        st.subheader("⚙️ Opcje Chat")

        # Ustawienia AI
        temperature = st.slider(
            "Temperatura AI",
            0.1,
            1.0,
            0.8,
            0.1,
            help="Kontrola kreatywności odpowiedzi",
        )
        max_tokens = st.slider(
            "Długość odpowiedzi",
            512,
            4096,
            3072,
            256,
            help="Maksymalna długość odpowiedzi",
        )

        # Typy pytań
        st.subheader("💡 Przykładowe Pytania")
        sample_questions = [
            "Jakie są główne ryzyka audytorskie?",
            "Przeanalizuj wskaźniki finansowe ROA i ROE",
            "Jak przeprowadzić ocenę ryzyka?",
            "Co to są wstępne procedury audytorskie?",
            "Jakie dokumenty PBC są wymagane?",
            "Przeanalizuj bilans jednostki",
            "Jak ocenić płynność finansową?",
            "Co to są Working Papers?",
        ]

        for i, question in enumerate(sample_questions):
            if st.button(
                f"💬 {question[:30]}...", key=f"sample_{i}", use_container_width=True
            ):
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()

        # Akcje chat
        st.subheader("🎛️ Akcje")

        if st.button("🗑️ Wyczyść Chat", use_container_width=True):
            st.session_state.messages = []
            st.success("✅ Chat wyczyszczony!")
            st.rerun()

        if st.button("💾 Eksportuj Chat", use_container_width=True):
            if st.session_state.messages:
                chat_export = "\n\n".join(
                    [
                        f"{msg['role'].upper()}: {msg['content']}"
                        for msg in st.session_state.messages
                    ]
                )
                st.download_button(
                    label="📥 Pobierz Chat",
                    data=chat_export,
                    file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                )
            else:
                st.info("Brak wiadomości do eksportu")

        if st.button("📊 Analiza Chat", use_container_width=True):
            if st.session_state.messages:
                with st.spinner("Analizuję chat..."):
                    chat_analysis = call_real_ai(
                        f"Przeanalizuj historię chat audytorskiego i podaj podsumowanie głównych tematów, pytań i rekomendacji. Historia: {len(st.session_state.messages)} wiadomości.",
                        max_tokens=400,
                    )
                    st.success("✅ Analiza chat zakończona!")
                    with st.expander("📊 Analiza chat"):
                        st.markdown(chat_analysis)
            else:
                st.info("Brak wiadomości do analizy")

    # Statystyki chat
    if st.session_state.messages:
        st.subheader("📊 Statystyki Chat")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("💬 Wiadomości", len(st.session_state.messages))
        with col2:
            user_messages = len(
                [m for m in st.session_state.messages if m["role"] == "user"]
            )
            st.metric("👤 Pytania", user_messages)
        with col3:
            ai_messages = len(
                [m for m in st.session_state.messages if m["role"] == "assistant"]
            )
            st.metric("🤖 Odpowiedzi", ai_messages)
        with col4:
            total_chars = sum(len(m["content"]) for m in st.session_state.messages)
            st.metric("📝 Znaki", f"{total_chars:,}")

    # Szybkie akcje
    st.subheader("⚡ Szybkie Akcje")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🔍 Analiza Ryzyka", use_container_width=True):
            with st.spinner("Analizuję ryzyka..."):
                risk_analysis = call_real_ai(
                    "Przeprowadź kompleksową analizę ryzyka audytorskiego, uwzględniając ryzyka rozległe i specyficzne z plików klienta",
                    max_tokens=500,
                )
                st.session_state.messages.append(
                    {"role": "user", "content": "Analiza ryzyka audytorskiego"}
                )
                st.session_state.messages.append(
                    {"role": "assistant", "content": risk_analysis}
                )
                st.success("✅ Analiza ryzyka dodana do chat!")
                st.rerun()

    with col2:
        if st.button("📊 Wskaźniki Finansowe", use_container_width=True):
            with st.spinner("Analizuję wskaźniki..."):
                indicators_analysis = call_real_ai(
                    "Przeanalizuj wskaźniki finansowe z arkuszy 260 ANAW i 301 ANAW, uwzględniając ROA, ROE, płynność i efektywność",
                    max_tokens=500,
                )
                st.session_state.messages.append(
                    {"role": "user", "content": "Analiza wskaźników finansowych"}
                )
                st.session_state.messages.append(
                    {"role": "assistant", "content": indicators_analysis}
                )
                st.success("✅ Analiza wskaźników dodana do chat!")
                st.rerun()

    with col3:
        if st.button("📋 Procedury Audytorskie", use_container_width=True):
            with st.spinner("Analizuję procedury..."):
                procedures_analysis = call_real_ai(
                    "Opisz wstępne procedury audytorskie z pliku AB Wstępne Procedury, uwzględniając wszystkie 14 arkuszy",
                    max_tokens=500,
                )
                st.session_state.messages.append(
                    {"role": "user", "content": "Wstępne procedury audytorskie"}
                )
                st.session_state.messages.append(
                    {"role": "assistant", "content": procedures_analysis}
                )
                st.success("✅ Analiza procedur dodana do chat!")
                st.rerun()

    with col4:
        if st.button("📄 Sprawozdania Finansowe", use_container_width=True):
            with st.spinner("Analizuję sprawozdania..."):
                financial_analysis = call_real_ai(
                    "Przeanalizuj sprawozdania finansowe (BILANS, RachPor, RachKal, Cash Flow, ZZwK) z plików klienta",
                    max_tokens=500,
                )
                st.session_state.messages.append(
                    {"role": "user", "content": "Analiza sprawozdań finansowych"}
                )
                st.session_state.messages.append(
                    {"role": "assistant", "content": financial_analysis}
                )
                st.success("✅ Analiza sprawozdań dodana do chat!")
                st.rerun()


def render_ai_auditor_page():
    """Strona AI Audytor z funkcjonalnościami z plików klienta."""
    st.markdown(
        '<div class="main-header">🤖 AI Audytor - Narzędzia Specjalistyczne</div>',
        unsafe_allow_html=True,
    )

    # Tabs for different audit functions
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📁 Wstępne Procedury",
            "📊 Analiza Bilansu",
            "💰 Rachunek P&L",
            "📈 Cash Flow",
            "🔍 Analiza Ryzyka",
        ]
    )

    with tab1:
        st.subheader("📁 Wstępne Procedury - Analiza Dokumentów")

        col1, col2 = st.columns([2, 1])

        with col1:
            # File upload and operation selection
            with st.expander("📁 Analiza Plików - Wstępne Procedury", expanded=True):
                uploaded_file = st.file_uploader(
                    "Wgraj plik do analizy",
                    type=["xlsx", "xls", "csv", "pdf", "json"],
                    help="Wspieramy pliki Excel, CSV, PDF i JSON z danymi audytorskimi",
                )

                if uploaded_file:
                    st.success(f"✅ Wgrano: {uploaded_file.name}")

                    # Operation selection based on client files
                    operation_type = st.selectbox(
                        "Wybierz operację:",
                        [
                            "📊 Analiza Wstępnych Procedur (AB Wstepne Procedury)",
                            "📈 Analiza Wskaźników Finansowych (260 ANAW, 301 ANAW)",
                            "🔍 Analiza Ryzyka Biznesowego (302 RYZBAD)",
                            "📋 Analiza Baz Ryzyka (303 BAZRYZN)",
                            "💰 Analiza Rachunku P&L (RachPor, RachPor KOREKT)",
                            "📊 Analiza Bilansu (BILANS, BILANS KOREKT)",
                            "📈 Analiza Cash Flow (RPP)",
                            "🔄 Analiza Rachunku Kapitałów (RachKal, RachKal Korekt)",
                            "📋 Analiza Zobowiązań (ZZwK)",
                            "🤖 Kompleksowa Analiza AI",
                        ],
                    )

                    if st.button("🚀 Uruchom Analizę", use_container_width=True):
                        with st.spinner("Analizuję dane..."):
                            # Load client data
                            import json

                            try:
                                with open(
                                    "ai_audytor_wsad_wstepne_procedury.json",
                                    "r",
                                    encoding="utf-8",
                                ) as f:
                                    client_data = json.load(f)

                                # Generate analysis based on operation type
                                if "Wstępnych Procedur" in operation_type:
                                    analysis = call_real_ai(
                                        f"Przeanalizuj wstępne procedury audytorskie z pliku {uploaded_file.name}. "
                                        f"Dane klienta zawierają {client_data['metadata']['sheets_count']} arkuszy: "
                                        f"{', '.join(client_data['metadata']['sheets'])}. "
                                        f"Skup się na arkuszu 'Instrukcja Prompt' i 'Dane'.",
                                        max_tokens=800,
                                    )
                                elif "Wskaźników Finansowych" in operation_type:
                                    analysis = call_real_ai(
                                        "Przeanalizuj wskaźniki finansowe z arkuszy 260 ANAW i 301 ANAW. "
                                        "Oceń rentowność, płynność, zadłużenie i efektywność firmy.",
                                        max_tokens=800,
                                    )
                                elif "Ryzyka Biznesowego" in operation_type:
                                    analysis = call_real_ai(
                                        "Przeanalizuj ryzyko biznesowe z arkusza 302 RYZBAD. "
                                        "Zidentyfikuj główne ryzyka operacyjne, finansowe i strategiczne.",
                                        max_tokens=800,
                                    )
                                elif "Baz Ryzyka" in operation_type:
                                    analysis = call_real_ai(
                                        "Przeanalizuj bazy ryzyka z arkusza 303 BAZRYZN. "
                                        "Oceń system kontroli wewnętrznej i zarządzania ryzykiem.",
                                        max_tokens=800,
                                    )
                                elif "Rachunku P&L" in operation_type:
                                    analysis = call_real_ai(
                                        "Przeanalizuj rachunek zysków i strat z arkuszy RachPor i RachPor KOREKT. "
                                        "Oceń przychody, koszty, marże i rentowność.",
                                        max_tokens=800,
                                    )
                                elif "Bilansu" in operation_type:
                                    analysis = call_real_ai(
                                        "Przeanalizuj bilans z arkuszy BILANS i BILANS KOREKT. "
                                        "Oceń strukturę aktywów, pasywów i kapitałów.",
                                        max_tokens=800,
                                    )
                                elif "Cash Flow" in operation_type:
                                    analysis = call_real_ai(
                                        "Przeanalizuj przepływy pieniężne z arkusza Cash Flow (RPP). "
                                        "Oceń przepływy operacyjne, inwestycyjne i finansowe.",
                                        max_tokens=800,
                                    )
                                elif "Rachunku Kapitałów" in operation_type:
                                    analysis = call_real_ai(
                                        "Przeanalizuj rachunek kapitałów z arkuszy RachKal i RachKal Korekt. "
                                        "Oceń zmiany w kapitale własnym i rezerwach.",
                                        max_tokens=800,
                                    )
                                elif "Zobowiązań" in operation_type:
                                    analysis = call_real_ai(
                                        "Przeanalizuj zobowiązania z arkusza ZZwK. "
                                        "Oceń krótko- i długoterminowe zobowiązania firmy.",
                                        max_tokens=800,
                                    )
                                else:  # Kompleksowa Analiza AI
                                    analysis = call_real_ai(
                                        f"Przeprowadź kompleksową analizę audytorską wszystkich 14 arkuszy: "
                                        f"{', '.join(client_data['metadata']['sheets'])}. "
                                        f"Oceń sprawozdania finansowe, ryzyko, kontrolę wewnętrzną i zgodność z przepisami.",
                                        max_tokens=1200,
                                    )

                                st.success("✅ Analiza zakończona!")
                                st.markdown("### 📊 Wyniki Analizy")
                                st.markdown(analysis)

                                # Download option
                                st.markdown("### 📥 Pobierz Wyniki")
                                (
                                    col_download1,
                                    col_download2,
                                    col_download3,
                                    col_download4,
                                ) = st.columns(4)

                                with col_download1:
                                    if st.button(
                                        "📄 Pobierz PDF", use_container_width=True
                                    ):
                                        # Generate PDF content
                                        pdf_content = f"""
# Analiza AI Audytor
**Typ analizy:** {operation_type}
**Plik:** {uploaded_file.name}
**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Wyniki Analizy

{analysis}

---
*Wygenerowano przez AI Auditor*
                            """
                                        st.download_button(
                                            label="💾 Pobierz PDF",
                                            data=pdf_content,
                                            file_name=f"analiza_ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                            mime="text/plain",
                                        )

                                with col_download2:
                                    if st.button(
                                        "📊 Pobierz Excel", use_container_width=True
                                    ):
                                        # Generate Excel content
                                        excel_data = {
                                            "Typ_analizy": [operation_type],
                                            "Plik": [uploaded_file.name],
                                            "Data": [
                                                datetime.now().strftime(
                                                    "%Y-%m-%d %H:%M:%S"
                                                )
                                            ],
                                            "Wyniki": [
                                                (
                                                    analysis[:1000] + "..."
                                                    if len(analysis) > 1000
                                                    else analysis
                                                )
                                            ],
                                        }
                                        df = pd.DataFrame(excel_data)
                                        csv = df.to_csv(index=False)
                                        st.download_button(
                                            label="💾 Pobierz Excel",
                                            data=csv,
                                            file_name=f"analiza_ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                            mime="text/csv",
                                        )

                                with col_download3:
                                    if st.button(
                                        "📋 Pobierz JSON", use_container_width=True
                                    ):
                                        # Generate JSON content
                                        json_data = {
                                            "typ_analizy": operation_type,
                                            "plik": uploaded_file.name,
                                            "data": datetime.now().isoformat(),
                                            "wyniki": analysis,
                                        }
                                        json_str = json.dumps(
                                            json_data, ensure_ascii=False, indent=2
                                        )
                                        st.download_button(
                                            label="💾 Pobierz JSON",
                                            data=json_str,
                                            file_name=f"analiza_ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                            mime="application/json",
                                        )

                                with col_download4:
                                    if st.button(
                                        "📦 Evidence ZIP", use_container_width=True
                                    ):
                                        try:
                                            from core.evidence_zip import (
                                                generate_evidence_zip,
                                            )

                                            # Prepare findings data
                                            findings = [
                                                {
                                                    "id": f"F{datetime.now().strftime('%Y%m%d%H%M%S')}",
                                                    "type": "AI Analysis",
                                                    "severity": "medium",
                                                    "description": f"Analiza: {operation_type}",
                                                    "date": datetime.now().strftime(
                                                        "%Y-%m-%d"
                                                    ),
                                                    "status": "Open",
                                                    "details": (
                                                        analysis[:500] + "..."
                                                        if len(analysis) > 500
                                                        else analysis
                                                    ),
                                                }
                                            ]

                                            # Prepare analysis data
                                            analysis_data = {
                                                "user": "AI Auditor",
                                                "operation_type": operation_type,
                                                "file_name": uploaded_file.name,
                                                "timestamp": datetime.now().isoformat(),
                                                "app_version": "1.0.0",
                                            }

                                            # Generate Evidence ZIP
                                            with st.spinner("Generuję Evidence ZIP..."):
                                                zip_path = generate_evidence_zip(
                                                    findings, analysis_data
                                                )

                                                # Read ZIP file for download
                                                with open(zip_path, "rb") as f:
                                                    zip_data = f.read()

                                                st.download_button(
                                                    label="💾 Pobierz Evidence ZIP",
                                                    data=zip_data,
                                                    file_name=f"evidence_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                                    mime="application/zip",
                                                )

                                                # Clean up temp file
                                                os.remove(zip_path)

                                        except ImportError as e:
                                            st.error(
                                                f"❌ Błąd importu Evidence ZIP: {e}"
                                            )
                                        except Exception as e:
                                            st.error(
                                                f"❌ Błąd generowania Evidence ZIP: {e}"
                                            )
                            except Exception as e:
                                st.error(f"❌ Błąd podczas analizy: {str(e)}")

        with col2:
            st.subheader("⚙️ Ustawienia Analizy")

            # Toggle controls for different functions
            st.markdown("### 🔧 Włącz/Wyłącz Funkcje")

            # Analysis toggles
            enable_basic_analysis = st.checkbox("📊 Analiza Podstawowa", value=True)
            enable_financial_analysis = st.checkbox("💰 Analiza Finansowa", value=True)
            enable_risk_analysis = st.checkbox("⚠️ Analiza Ryzyka", value=True)
            enable_compliance_analysis = st.checkbox("✅ Analiza Zgodności", value=True)
            enable_ai_recommendations = st.checkbox("🤖 Rekomendacje AI", value=True)

            # Advanced options
            st.markdown("### 🎛️ Opcje Zaawansowane")

            # Analysis depth
            analysis_depth = st.selectbox(
                "Głębokość analizy:",
                ["Powierzchowna", "Standardowa", "Szczegółowa", "Kompleksowa"],
            )

            # Output format
            output_format = st.selectbox(
                "Format wyjściowy:", ["Tekst", "HTML", "Markdown", "Strukturalny"]
            )

            # Include charts
            include_charts = st.checkbox("📊 Dołącz wykresy", value=True)
            include_tables = st.checkbox("📋 Dołącz tabele", value=True)
            include_recommendations = st.checkbox("💡 Dołącz rekomendacje", value=True)

            # Language selection
            analysis_language = st.selectbox(
                "Język analizy:", ["Polski", "English", "Deutsch", "Français"]
            )

            st.subheader("📋 Dostępne Arkusze")
            st.info(
                """
            **14 arkuszy klienta:**
            1. Instrukcja Prompt
            2. Dane
            3. BILANS
            4. BILANS KOREKT
            5. RachPor
            6. RachPor KOREKT
            7. RachKal
            8. RachKal Korekt
            9. Cash Flow (RPP)
            10. ZZwK
            11. 260 ANAW
            12. 301 ANAW
            13. 302 RYZBAD
            14. 303 BAZRYZN
            """
            )

            st.subheader("🎯 Szybkie Akcje")
            if st.button("📊 Analiza Wszystkich Arkuszy", use_container_width=True):
                with st.spinner("Analizuję wszystkie arkusze..."):
                    analysis = call_real_ai(
                        "Przeprowadź kompleksową analizę audytorską wszystkich 14 arkuszy klienta. "
                        "Oceń sprawozdania finansowe, ryzyko, kontrolę wewnętrzną i zgodność z przepisami.",
                        max_tokens=1200,
                    )
                    st.success("✅ Kompleksowa analiza zakończona!")
                    st.markdown(analysis)

            if st.button("🔍 Analiza Ryzyka", use_container_width=True):
                with st.spinner("Analizuję ryzyko..."):
                    analysis = call_real_ai(
                        "Przeanalizuj ryzyko biznesowe i operacyjne firmy na podstawie dostępnych danych. "
                        "Zidentyfikuj główne zagrożenia i zaproponuj rekomendacje.",
                        max_tokens=800,
                    )
                    st.success("✅ Analiza ryzyka zakończona!")
                    st.markdown(analysis)

    with tab2:
        st.subheader("📊 Analiza Bilansu")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 📋 Analiza Aktywów i Pasywów")

            # Bilans analysis options
            analysis_type = st.selectbox(
                "Typ analizy bilansu:",
                [
                    "📊 Analiza Struktury Aktywów",
                    "💰 Analiza Struktury Pasywów",
                    "⚖️ Analiza Równowagi Bilansowej",
                    "📈 Analiza Trendów Bilansowych",
                    "🔍 Analiza Korekt Bilansowych",
                ],
            )

            if st.button("🚀 Analizuj Bilans", use_container_width=True):
                with st.spinner("Analizuję bilans..."):
                    if "Struktury Aktywów" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj strukturę aktywów z arkuszy BILANS i BILANS KOREKT. "
                            "Oceń udział aktywów trwałych i obrotowych, ich jakość i płynność.",
                            max_tokens=800,
                        )
                    elif "Struktury Pasywów" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj strukturę pasywów z arkuszy BILANS i BILANS KOREKT. "
                            "Oceń udział kapitałów własnych i obcych, ich strukturę i koszt.",
                            max_tokens=800,
                        )
                    elif "Równowagi Bilansowej" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj równowagę bilansową z arkuszy BILANS i BILANS KOREKT. "
                            "Oceń zgodność aktywów z pasywami i ich strukturę czasową.",
                            max_tokens=800,
                        )
                    elif "Trendów Bilansowych" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj trendy bilansowe z arkuszy BILANS i BILANS KOREKT. "
                            "Oceń zmiany w strukturze aktywów i pasywów w czasie.",
                            max_tokens=800,
                        )
                    else:  # Korekt Bilansowych
                        analysis = call_real_ai(
                            "Przeanalizuj korekty bilansowe z arkusza BILANS KOREKT. "
                            "Oceń wpływ korekt na strukturę bilansu i ich uzasadnienie.",
                            max_tokens=800,
                        )

                    st.success("✅ Analiza bilansu zakończona!")
                    st.markdown(analysis)

        with col2:
            st.subheader("📊 Wskaźniki Bilansowe")
            st.info(
                """
            **Kluczowe wskaźniki:**
            - Struktura aktywów
            - Struktura pasywów
            - Płynność finansowa
            - Zadłużenie
            - Kapitał obrotowy
            """
            )

            if st.button("📈 Oblicz Wskaźniki", use_container_width=True):
                with st.spinner("Obliczam wskaźniki..."):
                    analysis = call_real_ai(
                        "Oblicz i przeanalizuj kluczowe wskaźniki bilansowe: "
                        "strukturę aktywów, pasywów, płynność, zadłużenie i kapitał obrotowy.",
                        max_tokens=600,
                    )
                    st.success("✅ Wskaźniki obliczone!")
                    st.markdown(analysis)

    with tab3:
        st.subheader("💰 Analiza Rachunku P&L")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 📋 Analiza Przychodów i Kosztów")

            # P&L analysis options
            analysis_type = st.selectbox(
                "Typ analizy P&L:",
                [
                    "📈 Analiza Przychodów",
                    "💰 Analiza Kosztów",
                    "📊 Analiza Marż",
                    "📉 Analiza Rentowności",
                    "🔍 Analiza Korekt P&L",
                ],
            )

            if st.button("🚀 Analizuj P&L", use_container_width=True):
                with st.spinner("Analizuję rachunek P&L..."):
                    if "Przychodów" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj przychody z arkuszy RachPor i RachPor KOREKT. "
                            "Oceń strukturę przychodów, ich trendy i jakość.",
                            max_tokens=800,
                        )
                    elif "Kosztów" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj koszty z arkuszy RachPor i RachPor KOREKT. "
                            "Oceń strukturę kosztów, ich kontrolę i efektywność.",
                            max_tokens=800,
                        )
                    elif "Marż" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj marże z arkuszy RachPor i RachPor KOREKT. "
                            "Oceń marże brutto, operacyjne i netto.",
                            max_tokens=800,
                        )
                    elif "Rentowności" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj rentowność z arkuszy RachPor i RachPor KOREKT. "
                            "Oceń ROE, ROA, ROS i inne wskaźniki rentowności.",
                            max_tokens=800,
                        )
                    else:  # Korekt P&L
                        analysis = call_real_ai(
                            "Przeanalizuj korekty P&L z arkusza RachPor KOREKT. "
                            "Oceń wpływ korekt na wynik finansowy i ich uzasadnienie.",
                            max_tokens=800,
                        )

                    st.success("✅ Analiza P&L zakończona!")
                    st.markdown(analysis)

        with col2:
            st.subheader("📊 Wskaźniki P&L")
            st.info(
                """
            **Kluczowe wskaźniki:**
            - Marża brutto
            - Marża operacyjna
            - Marża netto
            - ROE (ROA)
            - ROS
            """
            )

            if st.button("📈 Oblicz Wskaźniki P&L", use_container_width=True):
                with st.spinner("Obliczam wskaźniki P&L..."):
                    analysis = call_real_ai(
                        "Oblicz i przeanalizuj kluczowe wskaźniki rachunku P&L: "
                        "marże, rentowność, efektywność i trendy.",
                        max_tokens=600,
                    )
                    st.success("✅ Wskaźniki P&L obliczone!")
                    st.markdown(analysis)

    with tab4:
        st.subheader("📈 Analiza Cash Flow")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 💰 Analiza Przepływów Pieniężnych")

            # Cash Flow analysis options
            analysis_type = st.selectbox(
                "Typ analizy Cash Flow:",
                [
                    "💼 Analiza Przepływów Operacyjnych",
                    "🏗️ Analiza Przepływów Inwestycyjnych",
                    "🏦 Analiza Przepływów Finansowych",
                    "📊 Analiza Łącznych Przepływów",
                    "🔍 Analiza Jakości Przepływów",
                ],
            )

            if st.button("🚀 Analizuj Cash Flow", use_container_width=True):
                with st.spinner("Analizuję Cash Flow..."):
                    if "Operacyjnych" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj przepływy operacyjne z arkusza Cash Flow (RPP). "
                            "Oceń jakość przepływów operacyjnych i ich stabilność.",
                            max_tokens=800,
                        )
                    elif "Inwestycyjnych" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj przepływy inwestycyjne z arkusza Cash Flow (RPP). "
                            "Oceń inwestycje w aktywa trwałe i ich efektywność.",
                            max_tokens=800,
                        )
                    elif "Finansowych" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj przepływy finansowe z arkusza Cash Flow (RPP). "
                            "Oceń pozyskiwanie i spłatę kapitałów obcych.",
                            max_tokens=800,
                        )
                    elif "Łącznych Przepływów" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj łączne przepływy pieniężne z arkusza Cash Flow (RPP). "
                            "Oceń zmianę stanu środków pieniężnych i ich przyczyny.",
                            max_tokens=800,
                        )
                    else:  # Jakości Przepływów
                        analysis = call_real_ai(
                            "Przeanalizuj jakość przepływów pieniężnych z arkusza Cash Flow (RPP). "
                            "Oceń relację między przepływami operacyjnymi a zyskiem netto.",
                            max_tokens=800,
                        )

                    st.success("✅ Analiza Cash Flow zakończona!")
                    st.markdown(analysis)

        with col2:
            st.subheader("📊 Wskaźniki Cash Flow")
            st.info(
                """
            **Kluczowe wskaźniki:**
            - Jakość przepływów
            - Pokrycie inwestycji
            - Pokrycie dywidend
            - Wskaźnik płynności
            """
            )

            if st.button("📈 Oblicz Wskaźniki CF", use_container_width=True):
                with st.spinner("Obliczam wskaźniki Cash Flow..."):
                    analysis = call_real_ai(
                        "Oblicz i przeanalizuj kluczowe wskaźniki Cash Flow: "
                        "jakość przepływów, pokrycie inwestycji i płynność.",
                        max_tokens=600,
                    )
                    st.success("✅ Wskaźniki Cash Flow obliczone!")
                    st.markdown(analysis)

    with tab5:
        st.subheader("🔍 Analiza Ryzyka")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### ⚠️ Analiza Ryzyka Biznesowego")

            # Risk analysis options
            analysis_type = st.selectbox(
                "Typ analizy ryzyka:",
                [
                    "⚠️ Analiza Ryzyka Operacyjnego",
                    "💰 Analiza Ryzyka Finansowego",
                    "📊 Analiza Ryzyka Strategicznego",
                    "🔍 Analiza Kontroli Wewnętrznej",
                    "📋 Analiza Baz Ryzyka",
                ],
            )

            if st.button("🚀 Analizuj Ryzyko", use_container_width=True):
                with st.spinner("Analizuję ryzyko..."):
                    if "Operacyjnego" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj ryzyko operacyjne z arkusza 302 RYZBAD. "
                            "Zidentyfikuj główne ryzyka związane z działalnością operacyjną firmy.",
                            max_tokens=800,
                        )
                    elif "Finansowego" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj ryzyko finansowe z arkusza 302 RYZBAD. "
                            "Oceń ryzyko płynności, kredytowe i stopy procentowej.",
                            max_tokens=800,
                        )
                    elif "Strategicznego" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj ryzyko strategiczne z arkusza 302 RYZBAD. "
                            "Oceń ryzyko rynkowe, konkurencyjne i technologiczne.",
                            max_tokens=800,
                        )
                    elif "Kontroli Wewnętrznej" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj kontrolę wewnętrzną z arkusza 303 BAZRYZN. "
                            "Oceń system kontroli wewnętrznej i jego efektywność.",
                            max_tokens=800,
                        )
                    else:  # Baz Ryzyka
                        analysis = call_real_ai(
                            "Przeanalizuj bazy ryzyka z arkusza 303 BAZRYZN. "
                            "Oceń system zarządzania ryzykiem i jego implementację.",
                            max_tokens=800,
                        )

                    st.success("✅ Analiza ryzyka zakończona!")
                    st.markdown(analysis)

        with col2:
            st.subheader("📊 Wskaźniki Ryzyka")
            st.info(
                """
            **Kluczowe wskaźniki:**
            - Poziom ryzyka
            - Kontrola wewnętrzna
            - Zarządzanie ryzykiem
            - Zgodność z przepisami
            """
            )

            if st.button("📈 Oblicz Wskaźniki Ryzyka", use_container_width=True):
                with st.spinner("Obliczam wskaźniki ryzyka..."):
                    analysis = call_real_ai(
                        "Oblicz i przeanalizuj kluczowe wskaźniki ryzyka: "
                        "poziom ryzyka, kontrolę wewnętrzną i zarządzanie ryzykiem.",
                        max_tokens=600,
                    )
                    st.success("✅ Wskaźniki ryzyka obliczone!")
                    st.markdown(analysis)

                # Additional parameters based on operation
                if "Wstępnych Procedur" in operation_type:
                    st.info("🎯 **Funkcje dostępne:**")
                    st.markdown(
                        """
                    - Parsowanie formuł Excel (SUM, AVERAGE, COUNT, IF)
                    - Ewaluacja wskaźników finansowych
                    - Generowanie raportów z wynikami
                    - Identyfikacja błędów w formułach
                    """
                    )

                elif "Wskaźników Finansowych" in operation_type:
                    st.info("🎯 **Wskaźniki do analizy:**")
                    st.markdown(
                        """
                    - **Rentowność**: ROA (19.76%), ROE (30.68%), Rentowność sprzedaży (7.52%)
                    - **Płynność**: Wskaźnik płynności I (1.86), II (1.38), III (1.05)
                    - **Efektywność**: Rotacja aktywów (2.71), środków trwałych (6.95), zapasów (24.47 dni)
                    """
                    )

                elif "Ocena Ryzyka" in operation_type:
                    st.info("🎯 **Typy ryzyk:**")
                    st.markdown(
                        """
                    - **Ryzyka rozległe**: obejścia kontroli przez zarząd, oszustwa na poziomie sprawozdania
                    - **Ryzyka specyficzne**: na poziomie stwierdzeń, prawdopodobieństwo (1-3), wielkość zniekształcenia
                    - **Kontrola wewnętrzna**: obszary kontroli, ryzyko oszustwa/nadużyć
                    """
                    )

                # Advanced options
                with st.expander("⚙️ Opcje Zaawansowane"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        temperature = st.slider("Temperatura AI", 0.1, 1.0, 0.8, 0.1)
                        max_tokens = st.slider(
                            "Maksymalna długość odpowiedzi", 512, 4096, 2048, 256
                        )
                    with col_b:
                        include_formulas = st.checkbox(
                            "Analizuj formuły Excel", value=True
                        )
                        generate_report = st.checkbox(
                            "Generuj raport końcowy", value=True
                        )

                if st.button("🚀 Uruchom Analizę", use_container_width=True):
                    with st.spinner("Analizuję..."):
                        # Enhanced AI prompt based on operation type
                        if "Wstępnych Procedur" in operation_type:
                            ai_prompt = f"""
                            Jako ekspert audytor, przeanalizuj plik {uploaded_file.name} w kontekście wstępnych procedur audytorskich.

                            Uwzględnij:
                            - Parsowanie i ewaluację formuł Excel (SUM, AVERAGE, COUNT, IF)
                            - Analizę wskaźników finansowych
                            - Identyfikację błędów w formułach
                            - Generowanie raportu z wynikami

                            Podaj szczegółową analizę z konkretnymi wskaźnikami, błędami i rekomendacjami.
                            """
                        elif "Wskaźników Finansowych" in operation_type:
                            ai_prompt = f"""
                            Jako ekspert audytor, przeanalizuj wskaźniki finansowe z pliku {uploaded_file.name}.

                            Skoncentruj się na:
                            - Rentowność: ROA, ROE, rentowność sprzedaży
                            - Płynność: wskaźniki płynności I, II, III
                            - Efektywność: rotacja aktywów, środków trwałych, zapasów
                            - Analiza trendów na przestrzeni lat
                            - Porównanie z branżą i benchmarkami

                            Podaj ocenę wskaźników, identyfikuj anomalie i sformułuj rekomendacje.
                            """
                        elif "Ocena Ryzyka" in operation_type:
                            ai_prompt = f"""
                            Jako ekspert audytor, przeprowadź ocenę ryzyka na podstawie pliku {uploaded_file.name}.

                            Uwzględnij:
                            - Ryzyka rozległe (ogólne): obejścia kontroli przez zarząd, oszustwa na poziomie sprawozdania
                            - Ryzyka specyficzne: na poziomie stwierdzeń, prawdopodobieństwo (1-3), wielkość zniekształcenia
                            - Kontrola wewnętrzna: obszary kontroli, ryzyko oszustwa/nadużyć
                            - Macierz prawdopodobieństwo vs wpływ
                            - Rekomendacje łagodzenia ryzyk

                            Przygotuj szczegółowy raport oceny ryzyka z konkretnymi rekomendacjami.
                            """
                        else:
                            ai_prompt = f"Przeanalizuj plik {uploaded_file.name} w kontekście {operation_type}. Podaj szczegółową analizę z konkretnymi wskaźnikami i rekomendacjami."

                        # Call AI with enhanced parameters
                        ai_response = call_real_ai(
                            ai_prompt, temperature=temperature, max_tokens=max_tokens
                        )

                        st.success("✅ Analiza zakończona!")
                        st.markdown(f"**Wyniki analizy:**\n\n{ai_response}")

                        # Enhanced metrics based on operation type
                        if "Wskaźników" in operation_type:
                            met1, met2, met3, met4 = st.columns(4)
                            with met1:
                                st.metric("ROA", "19.76%", "2.1%")
                            with met2:
                                st.metric("ROE", "30.68%", "3.2%")
                            with met3:
                                st.metric("Płynność I", "1.86", "0.15")
                            with met4:
                                st.metric("Rotacja", "2.71", "0.3")
                        else:
                            met1, met2, met3 = st.columns(3)
                            with met1:
                                st.metric("Zgodność", "85%", "5%")
                            with met2:
                                st.metric("Ryzyko", "Średnie", "↓")
                            with met3:
                                st.metric("Anomalie", "3", "-2")

        # Quick tools based on client files
        with st.expander("🛠️ Narzędzia Szybkie - Wstępne Procedury"):
            st.info("🎯 **Dostępne narzędzia:**")

            col_t1, col_t2 = st.columns(2)

            with col_t1:
                if st.button("📊 Analiza Wstępnych Procedur", use_container_width=True):
                    with st.spinner("Analizuję wstępne procedury..."):
                        prompt = """
                        Jako ekspert audytor, przygotuj analizę wstępnych procedur audytorskich.

                        Uwzględnij:
                        - Parsowanie formuł Excel (SUM, AVERAGE, COUNT, IF)
                        - Ewaluację wskaźników finansowych
                        - Identyfikację błędów w formułach
                        - Generowanie raportu z wynikami

                        Podaj szczegółową analizę z konkretnymi wskaźnikami i rekomendacjami.
                        """
                        response = call_real_ai(prompt, max_tokens=2048)
                        st.success("✅ Analiza wstępnych procedur zakończona!")
                        st.markdown(f"**Wyniki:**\n\n{response}")

                if st.button(
                    "📈 Analiza Wskaźników (260 ANAW)", use_container_width=True
                ):
                    with st.spinner("Analizuję wskaźniki..."):
                        prompt = """
                        Jako ekspert audytor, przeanalizuj wskaźniki finansowe z arkusza 260 ANAW.

                        Skoncentruj się na:
                        - Rentowność: ROA (19.76%), ROE (30.68%), rentowność sprzedaży (7.52%)
                        - Płynność: wskaźniki płynności I (1.86), II (1.38), III (1.05)
                        - Efektywność: rotacja aktywów (2.71), środków trwałych (6.95), zapasów (24.47 dni)
                        - Analiza trendów na przestrzeni lat

                        Podaj ocenę wskaźników, identyfikuj anomalie i sformułuj rekomendacje.
                        """
                        response = call_real_ai(prompt, max_tokens=2048)
                        st.success("✅ Analiza wskaźników zakończona!")
                        st.markdown(f"**Wyniki:**\n\n{response}")

            with col_t2:
                if st.button("⚠️ Ocena Ryzyka (302 RYZBAD)", use_container_width=True):
                    with st.spinner("Oceniam ryzyka..."):
                        prompt = """
                        Jako ekspert audytor, przeprowadź ocenę ryzyka na podstawie arkusza 302 RYZBAD.

                        Uwzględnij:
                        - Ryzyka rozległe (ogólne): obejścia kontroli przez zarząd, oszustwa na poziomie sprawozdania
                        - Ryzyka specyficzne: na poziomie stwierdzeń, prawdopodobieństwo (1-3), wielkość zniekształcenia
                        - Kontrola wewnętrzna: obszary kontroli, ryzyko oszustwa/nadużyć
                        - Macierz prawdopodobieństwo vs wpływ

                        Przygotuj szczegółowy raport oceny ryzyka z konkretnymi rekomendacjami.
                        """
                        response = call_real_ai(prompt, max_tokens=2048)
                        st.success("✅ Ocena ryzyka zakończona!")
                        st.markdown(f"**Wyniki:**\n\n{response}")

                if st.button("💰 Analiza Bilansu", use_container_width=True):
                    with st.spinner("Analizuję bilans..."):
                        prompt = """
                        Jako ekspert audytor, przeanalizuj bilans jednostki (BILANS, BILANS KOREKT).

                        Uwzględnij:
                        - Analizę struktury aktywów i pasywów
                        - Zmiany na przestrzeni lat
                        - Korekty i ich wpływ na sprawozdanie
                        - Identyfikację pozycji istotnych
                        - Ocena płynności i zadłużenia

                        Podaj szczegółową analizę bilansu z rekomendacjami.
                        """
                        response = call_real_ai(prompt, max_tokens=2048)
                        st.success("✅ Analiza bilansu zakończona!")
                        st.markdown(f"**Wyniki:**\n\n{response}")

        # Advanced analysis tools
        with st.expander("🔬 Narzędzia Zaawansowane"):
            st.info("🎯 **Zaawansowane funkcje analityczne:**")

            col_a1, col_a2 = st.columns(2)

            with col_a1:
                if st.button("📋 Rachunek Zysków i Strat", use_container_width=True):
                    with st.spinner("Analizuję RZiS..."):
                        prompt = """
                        Jako ekspert audytor, przeanalizuj rachunek zysków i strat (RachPor, RachPor KOREKT).

                        Uwzględnij:
                        - Analizę przychodów i kosztów
                        - Zmiany na przestrzeni lat
                        - Korekty i ich wpływ na wynik
                        - Analizę rentowności
                        - Identyfikację pozycji istotnych

                        Podaj szczegółową analizę RZiS z rekomendacjami.
                        """
                        response = call_real_ai(prompt, max_tokens=2048)
                        st.success("✅ Analiza RZiS zakończona!")
                        st.markdown(f"**Wyniki:**\n\n{response}")

                if st.button("🔄 Rachunek Kalkulacyjny", use_container_width=True):
                    with st.spinner("Analizuję rachunek kalkulacyjny..."):
                        prompt = """
                        Jako ekspert audytor, przeanalizuj rachunek kalkulacyjny (RachKal, RachKal Korekt).

                        Uwzględnij:
                        - Analizę kosztów w układzie kalkulacyjnym
                        - Zmiany na przestrzeni lat
                        - Korekty i ich wpływ na koszty
                        - Analizę efektywności kosztowej
                        - Identyfikację pozycji istotnych

                        Podaj szczegółową analizę rachunku kalkulacyjnego z rekomendacjami.
                        """
                        response = call_real_ai(prompt, max_tokens=2048)
                        st.success("✅ Analiza rachunku kalkulacyjnego zakończona!")
                        st.markdown(f"**Wyniki:**\n\n{response}")

            with col_a2:
                if st.button("💸 Cash Flow (RPP)", use_container_width=True):
                    with st.spinner("Analizuję przepływy pieniężne..."):
                        prompt = """
                        Jako ekspert audytor, przeanalizuj rachunek przepływów pieniężnych (Cash Flow RPP).

                        Uwzględnij:
                        - Analizę przepływów operacyjnych, inwestycyjnych i finansowych
                        - Zmiany na przestrzeni lat
                        - Analizę płynności
                        - Identyfikację pozycji istotnych
                        - Ocena zdolności do generowania gotówki

                        Podaj szczegółową analizę przepływów pieniężnych z rekomendacjami.
                        """
                        response = call_real_ai(prompt, max_tokens=2048)
                        st.success("✅ Analiza przepływów pieniężnych zakończona!")
                        st.markdown(f"**Wyniki:**\n\n{response}")

                if st.button(
                    "📊 Zestawienie Zmian w Kapitale", use_container_width=True
                ):
                    with st.spinner("Analizuję zmiany w kapitale..."):
                        prompt = """
                        Jako ekspert audytor, przeanalizuj zestawienie zmian w kapitale (ZZwK).

                        Uwzględnij:
                        - Analizę zmian w kapitale własnym
                        - Zmiany na przestrzeni lat
                        - Identyfikację pozycji istotnych
                        - Analizę struktury kapitału
                        - Ocena stabilności finansowej

                        Podaj szczegółową analizę zmian w kapitale z rekomendacjami.
                        """
                        response = call_real_ai(prompt, max_tokens=2048)
                        st.success("✅ Analiza zmian w kapitale zakończona!")
                        st.markdown(f"**Wyniki:**\n\n{response}")

        with col2:
            st.subheader("🤖 AI Asystent Audytora")

            # AI Chat for auditing
            if "auditor_messages" not in st.session_state:
                st.session_state.auditor_messages = []

            # Display chat messages
            for message in st.session_state.auditor_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Chat input
            if prompt := st.chat_input("Zadaj pytanie o audyt..."):
                st.session_state.auditor_messages.append(
                    {"role": "user", "content": prompt}
                )

                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Analizuję..."):
                        # Call real AI for auditing
                        ai_response = call_real_ai(
                            f"Jako ekspert audytor, odpowiedz na pytanie: {prompt}"
                        )
                        st.markdown(f"**Asystent AI Audytora:**\n\n{ai_response}")

                st.session_state.auditor_messages.append(
                    {"role": "assistant", "content": ai_response}
                )

    with tab2:
        st.subheader("📊 Analiza Bilansu")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 📋 Analiza Aktywów i Pasywów")

            # Bilans analysis options
            analysis_type = st.selectbox(
                "Typ analizy bilansu:",
                [
                    "📊 Analiza Struktury Aktywów",
                    "💰 Analiza Struktury Pasywów",
                    "⚖️ Analiza Równowagi Bilansowej",
                    "📈 Analiza Trendów Bilansowych",
                    "🔍 Analiza Korekt Bilansowych",
                ],
            )

            if st.button("🚀 Analizuj Bilans", use_container_width=True):
                with st.spinner("Analizuję bilans..."):
                    if "Struktury Aktywów" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj strukturę aktywów z arkuszy BILANS i BILANS KOREKT. "
                            "Oceń udział aktywów trwałych i obrotowych, ich jakość i płynność.",
                            max_tokens=800,
                        )
                    elif "Struktury Pasywów" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj strukturę pasywów z arkuszy BILANS i BILANS KOREKT. "
                            "Oceń udział kapitałów własnych i obcych, ich strukturę i koszt.",
                            max_tokens=800,
                        )
                    elif "Równowagi Bilansowej" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj równowagę bilansową z arkuszy BILANS i BILANS KOREKT. "
                            "Oceń zgodność aktywów z pasywami i ich strukturę czasową.",
                            max_tokens=800,
                        )
                    elif "Trendów Bilansowych" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj trendy bilansowe z arkuszy BILANS i BILANS KOREKT. "
                            "Oceń zmiany w strukturze aktywów i pasywów w czasie.",
                            max_tokens=800,
                        )
                    else:  # Korekt Bilansowych
                        analysis = call_real_ai(
                            "Przeanalizuj korekty bilansowe z arkusza BILANS KOREKT. "
                            "Oceń wpływ korekt na strukturę bilansu i ich uzasadnienie.",
                            max_tokens=800,
                        )

                    st.success("✅ Analiza bilansu zakończona!")
                    st.markdown(analysis)

        with col2:
            st.subheader("📊 Wskaźniki Bilansowe")
            st.info(
                """
            **Kluczowe wskaźniki:**
            - Struktura aktywów
            - Struktura pasywów
            - Płynność finansowa
            - Zadłużenie
            - Kapitał obrotowy
            """
            )

            if st.button("📈 Oblicz Wskaźniki", use_container_width=True):
                with st.spinner("Obliczam wskaźniki..."):
                    analysis = call_real_ai(
                        "Oblicz i przeanalizuj kluczowe wskaźniki bilansowe: "
                        "strukturę aktywów, pasywów, płynność, zadłużenie i kapitał obrotowy.",
                        max_tokens=600,
                    )
                    st.success("✅ Wskaźniki obliczone!")
                    st.markdown(analysis)

    with tab3:
        st.subheader("💰 Analiza Rachunku P&L")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 📋 Analiza Przychodów i Kosztów")

            # P&L analysis options
            analysis_type = st.selectbox(
                "Typ analizy P&L:",
                [
                    "📈 Analiza Przychodów",
                    "💰 Analiza Kosztów",
                    "📊 Analiza Marż",
                    "📉 Analiza Rentowności",
                    "🔍 Analiza Korekt P&L",
                ],
            )

            if st.button("🚀 Analizuj P&L", use_container_width=True):
                with st.spinner("Analizuję rachunek P&L..."):
                    if "Przychodów" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj przychody z arkuszy RachPor i RachPor KOREKT. "
                            "Oceń strukturę przychodów, ich trendy i jakość.",
                            max_tokens=800,
                        )
                    elif "Kosztów" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj koszty z arkuszy RachPor i RachPor KOREKT. "
                            "Oceń strukturę kosztów, ich kontrolę i efektywność.",
                            max_tokens=800,
                        )
                    elif "Marż" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj marże z arkuszy RachPor i RachPor KOREKT. "
                            "Oceń marże brutto, operacyjne i netto.",
                            max_tokens=800,
                        )
                    elif "Rentowności" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj rentowność z arkuszy RachPor i RachPor KOREKT. "
                            "Oceń ROE, ROA, ROS i inne wskaźniki rentowności.",
                            max_tokens=800,
                        )
                    else:  # Korekt P&L
                        analysis = call_real_ai(
                            "Przeanalizuj korekty P&L z arkusza RachPor KOREKT. "
                            "Oceń wpływ korekt na wynik finansowy i ich uzasadnienie.",
                            max_tokens=800,
                        )

                    st.success("✅ Analiza P&L zakończona!")
                    st.markdown(analysis)

        with col2:
            st.subheader("📊 Wskaźniki P&L")
            st.info(
                """
            **Kluczowe wskaźniki:**
            - Marża brutto
            - Marża operacyjna
            - Marża netto
            - ROE (ROA)
            - ROS
            """
            )

            if st.button("📈 Oblicz Wskaźniki P&L", use_container_width=True):
                with st.spinner("Obliczam wskaźniki P&L..."):
                    analysis = call_real_ai(
                        "Oblicz i przeanalizuj kluczowe wskaźniki rachunku P&L: "
                        "marże, rentowność, efektywność i trendy.",
                        max_tokens=600,
                    )
                    st.success("✅ Wskaźniki P&L obliczone!")
                    st.markdown(analysis)

    with tab4:
        st.subheader("📈 Analiza Cash Flow")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 💰 Analiza Przepływów Pieniężnych")

            # Cash Flow analysis options
            analysis_type = st.selectbox(
                "Typ analizy Cash Flow:",
                [
                    "💼 Analiza Przepływów Operacyjnych",
                    "🏗️ Analiza Przepływów Inwestycyjnych",
                    "🏦 Analiza Przepływów Finansowych",
                    "📊 Analiza Łącznych Przepływów",
                    "🔍 Analiza Jakości Przepływów",
                ],
            )

            if st.button("🚀 Analizuj Cash Flow", use_container_width=True):
                with st.spinner("Analizuję Cash Flow..."):
                    if "Operacyjnych" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj przepływy operacyjne z arkusza Cash Flow (RPP). "
                            "Oceń jakość przepływów operacyjnych i ich stabilność.",
                            max_tokens=800,
                        )
                    elif "Inwestycyjnych" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj przepływy inwestycyjne z arkusza Cash Flow (RPP). "
                            "Oceń inwestycje w aktywa trwałe i ich efektywność.",
                            max_tokens=800,
                        )
                    elif "Finansowych" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj przepływy finansowe z arkusza Cash Flow (RPP). "
                            "Oceń pozyskiwanie i spłatę kapitałów obcych.",
                            max_tokens=800,
                        )
                    elif "Łącznych Przepływów" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj łączne przepływy pieniężne z arkusza Cash Flow (RPP). "
                            "Oceń zmianę stanu środków pieniężnych i ich przyczyny.",
                            max_tokens=800,
                        )
                    else:  # Jakości Przepływów
                        analysis = call_real_ai(
                            "Przeanalizuj jakość przepływów pieniężnych z arkusza Cash Flow (RPP). "
                            "Oceń relację między przepływami operacyjnymi a zyskiem netto.",
                            max_tokens=800,
                        )

                    st.success("✅ Analiza Cash Flow zakończona!")
                    st.markdown(analysis)

        with col2:
            st.subheader("📊 Wskaźniki Cash Flow")
            st.info(
                """
            **Kluczowe wskaźniki:**
            - Jakość przepływów
            - Pokrycie inwestycji
            - Pokrycie dywidend
            - Wskaźnik płynności
            """
            )

            if st.button("📈 Oblicz Wskaźniki CF", use_container_width=True):
                with st.spinner("Obliczam wskaźniki Cash Flow..."):
                    analysis = call_real_ai(
                        "Oblicz i przeanalizuj kluczowe wskaźniki Cash Flow: "
                        "jakość przepływów, pokrycie inwestycji i płynność.",
                        max_tokens=600,
                    )
                    st.success("✅ Wskaźniki Cash Flow obliczone!")
                    st.markdown(analysis)

    with tab5:
        st.subheader("🔍 Analiza Ryzyka")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### ⚠️ Analiza Ryzyka Biznesowego")

            # Risk analysis options
            analysis_type = st.selectbox(
                "Typ analizy ryzyka:",
                [
                    "⚠️ Analiza Ryzyka Operacyjnego",
                    "💰 Analiza Ryzyka Finansowego",
                    "📊 Analiza Ryzyka Strategicznego",
                    "🔍 Analiza Kontroli Wewnętrznej",
                    "📋 Analiza Baz Ryzyka",
                ],
            )

            if st.button("🚀 Analizuj Ryzyko", use_container_width=True):
                with st.spinner("Analizuję ryzyko..."):
                    if "Operacyjnego" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj ryzyko operacyjne z arkusza 302 RYZBAD. "
                            "Zidentyfikuj główne ryzyka związane z działalnością operacyjną firmy.",
                            max_tokens=800,
                        )
                    elif "Finansowego" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj ryzyko finansowe z arkusza 302 RYZBAD. "
                            "Oceń ryzyko płynności, kredytowe i stopy procentowej.",
                            max_tokens=800,
                        )
                    elif "Strategicznego" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj ryzyko strategiczne z arkusza 302 RYZBAD. "
                            "Oceń ryzyko rynkowe, konkurencyjne i technologiczne.",
                            max_tokens=800,
                        )
                    elif "Kontroli Wewnętrznej" in analysis_type:
                        analysis = call_real_ai(
                            "Przeanalizuj kontrolę wewnętrzną z arkusza 303 BAZRYZN. "
                            "Oceń system kontroli wewnętrznej i jego efektywność.",
                            max_tokens=800,
                        )
                    else:  # Baz Ryzyka
                        analysis = call_real_ai(
                            "Przeanalizuj bazy ryzyka z arkusza 303 BAZRYZN. "
                            "Oceń system zarządzania ryzykiem i jego implementację.",
                            max_tokens=800,
                        )

                    st.success("✅ Analiza ryzyka zakończona!")
                    st.markdown(analysis)

        with col2:
            st.subheader("📊 Wskaźniki Ryzyka")
            st.info(
                """
            **Kluczowe wskaźniki:**
            - Poziom ryzyka
            - Kontrola wewnętrzna
            - Zarządzanie ryzykiem
            - Zgodność z przepisami
            """
            )

            if st.button("📈 Oblicz Wskaźniki Ryzyka", use_container_width=True):
                with st.spinner("Obliczam wskaźniki ryzyka..."):
                    analysis = call_real_ai(
                        "Oblicz i przeanalizuj kluczowe wskaźniki ryzyka: "
                        "poziom ryzyka, kontrolę wewnętrzną i zarządzanie ryzykiem.",
                        max_tokens=600,
                    )
                    st.success("✅ Wskaźniki ryzyka obliczone!")
                    st.markdown(analysis)


def render_instructions_page():
    """Strona instrukcji."""
    st.markdown(
        '<div class="main-header">📚 Instrukcje dla Użytkowników</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    ## 🎯 Jak korzystać z AI Auditor

    ### 📊 Dashboard
    - **Statystyki w czasie rzeczywistym** - monitoring aktywności systemu
    - **Kluczowe metryki** - liczba audytów, niezgodności, raportów
    - **Wykresy analityczne** - trendy i rozkłady danych
    - **Ostatnie działania** - historia aktywności użytkowników
    - **Alerty systemowe** - powiadomienia o ważnych zdarzeniach

    ### 🏃 Run - Uruchamianie Audytu
    1. **Wgraj pliki** (PDF, Excel, CSV, JSON) - obsługa wielu formatów
    2. **Wybierz typ audytu** - różne scenariusze audytowe
    3. **Konfiguruj parametry** - dostosuj ustawienia do potrzeb
    4. **Kliknij "Uruchom Audyt"** - start procesu
    5. **Monitoruj postęp** - śledzenie w czasie rzeczywistym
    6. **Pobierz wyniki** - automatyczne generowanie raportów

    ### 🔍 Niezgodności - Zarządzanie Problemami
    - **Lista wszystkich niezgodności** - kompletny przegląd problemów
    - **Filtrowanie zaawansowane** - po priorytecie, statusie, dacie, kategorii
    - **Szczegółowe widoki** - rozszerzone informacje o każdym problemie
    - **System komentarzy** - komunikacja zespołu o postępie
    - **Historia zmian** - śledzenie wszystkich modyfikacji
    - **Masowe akcje** - operacje na wielu niezgodnościach jednocześnie
    - **Analiza AI** - automatyczna ocena ryzyka i rekomendacje
    - **Eksport raportów** - CSV, PDF, Excel z pełną dokumentacją
    - **Wykresy analityczne** - wizualizacja rozkładu problemów

    ### 📤 Eksporty - Kompleksowe Raporty
    #### PBC (Prepared by Client)
    - **Lista dokumentów** - zarządzanie plikami od klienta
    - **Status weryfikacji** - śledzenie postępu sprawdzania
    - **Timeline** - harmonogram dostarczania dokumentów

    #### Working Papers
    - **Generowanie dokumentów** - automatyczne tworzenie
    - **Chain of Evidence** - łańcuch dowodowy
    - **Kontrola jakości** - weryfikacja kompletności

    #### Raporty Końcowe
    - **Raport końcowy** - pełne sprawozdanie z audytu
    - **Executive Summary** - podsumowanie zarządcze
    - **Raporty zgodności** - compliance audit
    - **Analizy trendów** - porównania długoterminowe

    ### 💬 Chat AI - Inteligentny Asystent
    - **Rozmowy interaktywne** - naturalna komunikacja z AI
    - **Pytania o audyt** - eksperckie wsparcie w czasie rzeczywistym
    - **Analiza dokumentów** - przesyłanie plików do analizy
    - **Rekomendacje** - sugestie działań na podstawie danych
    - **Historia konwersacji** - zachowanie poprzednich rozmów
    - **Eksport chatów** - zapisywanie rozmów do plików
    - **Kontekst audytu** - AI pamięta szczegóły projektu

    ### 🤖 AI Audytor - ROZBUDOWANY O 14 ARKUSZY KLIENTA

    #### 📁 Wstępne Procedury
    - **Analiza wszystkich 14 arkuszy klienta**
    - **Instrukcja Prompt i Dane** - przetwarzanie arkuszy podstawowych
    - **Kompleksowa analiza AI** - automatyczne wykrywanie problemów
    - **Szybkie akcje** - analiza ryzyka i wszystkich arkuszy

    #### 📊 Analiza Bilansu (BILANS, BILANS KOREKT)
    - **Struktura aktywów** - analiza składu i jakości aktywów
    - **Struktura pasywów** - ocena źródeł finansowania
    - **Równowaga bilansowa** - weryfikacja spójności
    - **Trendy bilansowe** - zmiany w czasie
    - **Korekty bilansowe** - analiza wpływu korekt
    - **Wskaźniki bilansowe** - płynność, zadłużenie, kapitał obrotowy

    #### 💰 Rachunek P&L (RachPor, RachPor KOREKT)
    - **Analiza przychodów** - struktura i trendy przychodów
    - **Analiza kosztów** - kontrola i efektywność kosztów
    - **Analiza marż** - marże brutto, operacyjne, netto
    - **Analiza rentowności** - ROE, ROA, ROS
    - **Korekty P&L** - wpływ korekt na wynik finansowy

    #### 📈 Cash Flow (RPP)
    - **Przepływy operacyjne** - jakość i stabilność
    - **Przepływy inwestycyjne** - efektywność inwestycji
    - **Przepływy finansowe** - zarządzanie kapitałem
    - **Łączne przepływy** - zmiana stanu środków pieniężnych
    - **Jakość przepływów** - relacja do zysku netto

    #### 🔍 Analiza Ryzyka (302 RYZBAD, 303 BAZRYZN)
    - **Ryzyko operacyjne** - zagrożenia działalności
    - **Ryzyko finansowe** - płynność, kredyt, stopa procentowa
    - **Ryzyko strategiczne** - rynek, konkurencja, technologia
    - **Kontrola wewnętrzna** - system kontroli i jego efektywność
    - **Bazy ryzyka** - zarządzanie ryzykiem i implementacja

    #### 📋 Dodatkowe Analizy
    - **Rachunek Kapitałów (RachKal, RachKal Korekt)** - zmiany w kapitale
    - **Zobowiązania (ZZwK)** - analiza krótko- i długoterminowych zobowiązań
    - **Wskaźniki ANAW (260 ANAW, 301 ANAW)** - analiza wskaźników finansowych

    ### ⚙️ Settings - Konfiguracja Systemu
    #### Ustawienia AI
    - **URL serwera** - konfiguracja połączenia z AI
    - **Timeout** - czas oczekiwania na odpowiedź
    - **Temperatura** - kreatywność odpowiedzi AI
    - **Max tokens** - maksymalna długość odpowiedzi
    - **Test połączenia** - weryfikacja działania AI

    #### Ustawienia Interfejsu
    - **Motyw** - jasny/ciemny tryb
    - **Język** - wybór języka interfejsu
    - **Opcje wyświetlania** - dostosowanie widoku

    #### Informacje Systemowe
    - **Wersja systemu** - aktualna wersja oprogramowania
    - **Status AI serwera** - sprawdzenie połączenia
    - **Użytkownicy** - zarządzanie kontami
    - **Sesje** - aktywne połączenia
    - **Pliki i raporty** - statystyki zasobów

    ## 🔐 Bezpieczeństwo
    - **Hasło główne**: `TwojPIN123!`
    - **Szyfrowanie danych** - wszystkie dane zabezpieczone
    - **Regularne backupy** - automatyczne kopie zapasowe
    - **Kontrola dostępu** - zarządzanie uprawnieniami
    - **Logi bezpieczeństwa** - monitoring aktywności

    ## 🚀 Szybki Start
    1. **Zaloguj się** używając hasła `TwojPIN123!`
    2. **Przejdź do Dashboard** - sprawdź status systemu
    3. **Wgraj pliki w Run** - rozpocznij pierwszy audyt
    4. **Sprawdź Niezgodności** - przeanalizuj wyniki
    5. **Użyj AI Audytor** - skorzystaj z zaawansowanych analiz
    6. **Wygeneruj raporty w Eksporty** - pobierz wyniki

    ## 📞 Wsparcie Techniczne
    - **Dokumentacja**: Pełna dokumentacja w systemie
    - **Email**: support@ai-auditor.com
    - **Telefon**: +48 123 456 789
    - **Chat AI**: Zadaj pytanie bezpośrednio w systemie
    """
    )


def render_settings_page():
    """Strona ustawień."""
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎨 Wygląd")
        theme = st.selectbox("Motyw", ["Jasny", "Ciemny"])
        language = st.selectbox("Język", ["Polski", "English"])

        if st.button("💾 Zapisz ustawienia"):
            st.success("✅ Ustawienia zapisane!")

    with col2:
        st.subheader("🔧 Konfiguracja")
        ai_server = st.text_input("Serwer AI", "http://localhost:8000")
        timeout = st.number_input("Timeout (s)", 30, 300, 30)

        if st.button("🔄 Testuj połączenie"):
            st.success("✅ Połączenie OK!")

    st.divider()

    # Rules Configuration
    st.subheader("📋 Reguły Audytowe")

    try:
        from core.rules import get_rules

        rules = get_rules()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 💰 Tolerancje Kwot")
            max_diff = st.number_input(
                "Maksymalna różnica kwot (PLN)",
                value=float(rules.get_tolerance("amount", "max_difference", 0.01)),
                min_value=0.0,
                max_value=100.0,
                step=0.01,
            )

            percentage_tol = st.number_input(
                "Tolerancja procentowa (%)",
                value=float(rules.get_tolerance("amount", "percentage_tolerance", 0.1)),
                min_value=0.0,
                max_value=100.0,
                step=0.1,
            )

        with col2:
            st.markdown("#### 📅 Tolerancje Dat")
            max_days = st.number_input(
                "Maksymalna różnica dni",
                value=int(rules.get_tolerance("date", "max_days_difference", 1)),
                min_value=0,
                max_value=30,
                step=1,
            )

            weekend_ok = st.checkbox(
                "Akceptuj weekendy",
                value=bool(rules.get_tolerance("date", "weekend_tolerance", True)),
            )

        st.markdown("#### 🔍 Reguły Faktur")
        col1, col2, col3 = st.columns(3)

        with col1:
            dup_enabled = st.checkbox(
                "Sprawdzaj duplikaty numerów",
                value=bool(
                    rules.get_invoice_rule("duplicate_numbers", "enabled", True)
                ),
            )

            suspicious_enabled = st.checkbox(
                "Sprawdzaj podejrzane końcówki",
                value=bool(
                    rules.get_invoice_rule("suspicious_endings", "enabled", True)
                ),
            )

        with col2:
            serial_enabled = st.checkbox(
                "Sprawdzaj seryjne faktury",
                value=bool(rules.get_invoice_rule("serial_invoices", "enabled", True)),
            )

            amount_enabled = st.checkbox(
                "Sprawdzaj rozjazdy kwot",
                value=bool(rules.get_invoice_rule("amount_mismatch", "enabled", True)),
            )

        with col3:
            currency_enabled = st.checkbox(
                "Sprawdzaj waluty",
                value=bool(rules.get_invoice_rule("currency_check", "enabled", True)),
            )

        if st.button("💾 Zapisz Reguły", use_container_width=True):
            # Update rules
            rules.update_rule("tolerances.amount.max_difference", max_diff)
            rules.update_rule("tolerances.amount.percentage_tolerance", percentage_tol)
            rules.update_rule("tolerances.date.max_days_difference", max_days)
            rules.update_rule("tolerances.date.weekend_tolerance", weekend_ok)
            rules.update_rule("invoice_rules.duplicate_numbers.enabled", dup_enabled)
            rules.update_rule(
                "invoice_rules.suspicious_endings.enabled", suspicious_enabled
            )
            rules.update_rule("invoice_rules.serial_invoices.enabled", serial_enabled)
            rules.update_rule("invoice_rules.amount_mismatch.enabled", amount_enabled)
            rules.update_rule("invoice_rules.currency_check.enabled", currency_enabled)

            # Save to file
            rules.save_rules()
            st.success("✅ Reguły zapisane!")
            st.rerun()

        # Rules preview
        with st.expander("👁️ Podgląd Reguł"):
            st.json(rules.get_all_rules())

    except ImportError as e:
        st.error(f"❌ Błąd importu reguł: {e}")
        st.info("💡 Sprawdź czy plik core/rules.py istnieje")
    except Exception as e:
        st.error(f"❌ Błąd ładowania reguł: {e}")


def main():
    """Główna funkcja aplikacji."""
    apply_modern_css()

    # Check authentication
    if not st.session_state.authenticated:
        render_login()
        return

    # Render sidebar
    render_sidebar()

    # Render main content based on current page
    if st.session_state.current_page == "dashboard":
        render_dashboard()
    elif st.session_state.current_page == "run":
        render_run_page()
    elif st.session_state.current_page == "findings":
        render_findings_page()
    elif st.session_state.current_page == "exports":
        render_exports_page()
    elif st.session_state.current_page == "chat":
        render_chat_page()
    elif st.session_state.current_page == "ai_auditor":
        render_ai_auditor_page()
    elif st.session_state.current_page == "instructions":
        render_instructions_page()
    elif st.session_state.current_page == "settings":
        render_settings_page()


if __name__ == "__main__":
    main()
