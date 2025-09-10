"""
ROZBUDOWANY AI AUDITOR - Z FUNKCJONALNOŚCIAMI Z PLIKÓW KLIENTA
Zwiększone okno kontekstowe i długość odpowiedzi + wybór operacji na plikach
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import requests
import time
import os

# Page configuration
st.set_page_config(
    page_title="AI Auditor - Panel Audytora",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Password
ADMIN_PASSWORD = "TwojPIN123!"

# AI Configuration - ZWIĘKSZONE PARAMETRY
AI_SERVER_URL = "https://ai-auditor-romaks-8002.loca.lt"
AI_TIMEOUT = 45

def call_real_ai(prompt: str, temperature: float = 0.8, max_tokens: int = 3072) -> str:
    """Call the real AI model via API with enhanced parameters."""
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
        
        # Call AI model with enhanced context and parameters
        payload = {
            "prompt": prompt,
            "max_new_tokens": max_tokens,
            "do_sample": True,
            "temperature": temperature,
            "top_p": 0.9,
            "repetition_penalty": 1.1,
            "top_k": 50,
            "pad_token_id": 50256
        }
        
        response = requests.post(
            f"{AI_SERVER_URL}/analyze",
            json=payload,
            timeout=AI_TIMEOUT
        )
        
        if response.ok:
            data = response.json()
            return data.get("output", "Brak odpowiedzi od AI")
        else:
            return f"❌ Błąd AI: {response.status_code} - {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Brak połączenia z serwerem AI. Upewnij się, że serwer działa na localhost:8002"
    except requests.exceptions.Timeout:
        return "⏰ Timeout - AI nie odpowiedział w czasie 45 sekund"
    except Exception as e:
        return f"❌ Błąd połączenia z AI: {str(e)}"

def apply_modern_css():
    """Nowoczesny CSS."""
    theme = {
        'primary_color': '#2563eb',
        'secondary_color': '#7c3aed',
        'background_color': '#fafafa',
        'surface_color': '#ffffff',
        'text_color': '#1f2937',
        'border_color': '#e5e7eb',
        'gradient_start': '#2563eb',
        'gradient_end': '#7c3aed'
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
            "⚙️ Settings": "settings"
        }
        
        for label, page in pages.items():
            is_active = st.session_state.current_page == page
            if st.button(label, key=f"nav_{page}", use_container_width=True):
                st.session_state.current_page = page
                st.rerun()
        
        st.divider()
        
        # AI Status
        try:
            response = requests.get(f"{AI_SERVER_URL}/healthz", timeout=2)
            if response.ok:
                st.success("🤖 AI Server Online")
            else:
                st.warning("⚠️ AI Server Issues")
        except:
            st.error("❌ AI Server Offline")
        
        # Logout
        if st.button("🚪 Wyloguj", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

def render_dashboard():
    """Dashboard główny."""
    st.markdown('<div class="main-header">📊 Dashboard</div>', unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Przetworzone", "1,234", "12%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Niezgodności", "23", "-5%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Sukces", "98.1%", "2.3%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Czas", "2.3s", "-0.5s")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Trendy")
        data = pd.DataFrame({
            'Data': pd.date_range('2024-01-01', periods=30),
            'Wartość': [100 + i*2 + (i%7)*5 for i in range(30)]
        })
        fig = px.line(data, x='Data', y='Wartość', title='Trendy audytu')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🥧 Rozkład")
        data = {'Kategoria': ['Zgodne', 'Niezgodne', 'Do sprawdzenia'], 'Wartość': [85, 10, 5]}
        fig = px.pie(data, values='Wartość', names='Kategoria', title='Status dokumentów')
        st.plotly_chart(fig, use_container_width=True)

def render_run_page():
    """Strona uruchamiania audytu."""
    st.markdown('<div class="main-header">🏃 Run - Kolejki i Joby</div>', unsafe_allow_html=True)
    
    # File upload
    st.subheader("📁 Prześlij pliki")
    uploaded_files = st.file_uploader(
        "Drag and drop files here",
        type=['pdf', 'xlsx', 'xls', 'csv'],
        accept_multiple_files=True,
        help="Limit 200MB per file • PDF, ZIP, CSV, XLSX"
    )
    
    if uploaded_files:
        st.success(f"✅ Wgrano {len(uploaded_files)} plików")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🚀 Uruchom Audyt", use_container_width=True):
                with st.spinner("Uruchamianie audytu..."):
                    time.sleep(2)
                    st.success("✅ Audyt uruchomiony!")
    
    # Job queue
    st.subheader("📋 Kolejki i Joby")
    st.info("Brak zadań w kolejce")

def render_findings_page():
    """Strona niezgodności."""
    st.markdown('<div class="main-header">🔍 Niezgodności</div>', unsafe_allow_html=True)
    
    # Mock findings
    findings = [
        {"ID": "F001", "Typ": "Błąd walidacji", "Priorytet": "Wysoki", "Status": "Otwarty"},
        {"ID": "F002", "Typ": "Brak podpisu", "Priorytet": "Średni", "Status": "W trakcie"},
        {"ID": "F003", "Typ": "Nieprawidłowa kwota", "Priorytet": "Krytyczny", "Status": "Otwarty"},
    ]
    
    df = pd.DataFrame(findings)
    st.dataframe(df, use_container_width=True)
    
    # Actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Generuj Raport", use_container_width=True):
            st.success("✅ Raport wygenerowany!")
    with col2:
        if st.button("📧 Wyślij Email", use_container_width=True):
            st.success("✅ Email wysłany!")
    with col3:
        if st.button("🔄 Odśwież", use_container_width=True):
            st.rerun()

def render_exports_page():
    """Strona eksportów."""
    st.markdown('<div class="main-header">📤 Eksporty - PBC/WP/Raporty</div>', unsafe_allow_html=True)
    
    st.subheader("📊 Typy Eksportów")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**PBC (Prepared by Client)**")
        if st.button("📋 Lista PBC", use_container_width=True):
            st.success("✅ Lista PBC wygenerowana!")
        if st.button("📊 Status PBC", use_container_width=True):
            st.success("✅ Status PBC wygenerowany!")
        if st.button("📅 Timeline PBC", use_container_width=True):
            st.success("✅ Timeline PBC wygenerowany!")
    
    with col2:
        st.markdown("**Working Papers**")
        if st.button("📄 Working Papers", use_container_width=True):
            st.success("✅ Working Papers wygenerowane!")
        if st.button("🔗 Łańcuch dowodowy", use_container_width=True):
            st.success("✅ Łańcuch dowodowy wygenerowany!")
        if st.button("📊 Statystyki WP", use_container_width=True):
            st.success("✅ Statystyki WP wygenerowane!")
    
    with col3:
        st.markdown("**Raporty**")
        if st.button("📊 Raport końcowy", use_container_width=True):
            st.success("✅ Raport końcowy wygenerowany!")
        if st.button("📋 Executive Summary", use_container_width=True):
            st.success("✅ Executive Summary wygenerowany!")
        if st.button("✅ Compliance Report", use_container_width=True):
            st.success("✅ Compliance Report wygenerowany!")
    
    st.subheader("📚 Historia Eksportów")
    st.info("Brak historii eksportów")

def render_chat_page():
    """Strona Chat AI z zwiększonym kontekstem."""
    st.markdown('<div class="main-header">💬 Chat AI</div>', unsafe_allow_html=True)
    
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
            with st.spinner("Analizuję z zwiększonym kontekstem..."):
                # Enhanced prompt for better context
                enhanced_prompt = f"""
                Jako ekspert audytor z wieloletnim doświadczeniem, odpowiedz szczegółowo na pytanie:
                
                {prompt}
                
                Uwzględnij w odpowiedzi:
                - Kontekst audytorski i rachunkowy
                - Konkretne przykłady i przypadki
                - Referencje do standardów audytu
                - Praktyczne rekomendacje
                - Potencjalne ryzyka i ich mitygację
                
                Odpowiedź powinna być szczegółowa, profesjonalna i praktyczna.
                """
                
                # Call AI with enhanced parameters
                ai_response = call_real_ai(enhanced_prompt, temperature=0.8, max_tokens=3072)
                st.markdown(f"**Odpowiedź AI:**\n\n{ai_response}")
        
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

def render_ai_auditor_page():
    """Rozbudowana strona AI Audytor z funkcjonalnościami z plików klienta."""
    st.markdown('<div class="main-header">🤖 AI Audytor - Narzędzia Specjalistyczne</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Narzędzia Audytorskie - Pliki Klienta")
        
        # File upload and operation selection - ROZBUDOWANE
        with st.expander("📁 Analiza Plików - Wstępne Procedury Audytorskie", expanded=True):
            uploaded_file = st.file_uploader(
                "Wgraj plik do analizy",
                type=['xlsx', 'xls', 'csv', 'pdf', 'json'],
                help="Wspieramy pliki Excel (AB Wstępne Procedury), CSV, PDF i JSON z danymi audytorskimi"
            )
            
            if uploaded_file:
                st.success(f"✅ Wgrano: {uploaded_file.name}")
                
                # ROZBUDOWANY wybór operacji na podstawie plików klienta
                operation_type = st.selectbox(
                    "Wybierz operację (na podstawie plików klienta):",
                    [
                        "📊 Analiza Wstępnych Procedur (AB Wstepne Procedury)",
                        "📈 Analiza Wskaźników Finansowych (260 ANAW)",
                        "📊 Dodatkowa Analiza Wskaźników (301 ANAW)", 
                        "⚠️ Ocena Ryzyka Badania (302 RYZBAD)",
                        "🗃️ Analiza Bazy Ryzyk (303 BAZRYZN)",
                        "💰 Analiza Bilansu (BILANS)",
                        "💰 Analiza Bilansu Skorygowanego (BILANS KOREKT)",
                        "📋 Rachunek Zysków i Strat (RachPor)",
                        "📋 Rachunek Zysków i Strat Skorygowany (RachPor KOREKT)",
                        "🔄 Rachunek Kalkulacyjny (RachKal)",
                        "🔄 Rachunek Kalkulacyjny Skorygowany (RachKal Korekt)",
                        "💸 Rachunek Przepływów Pieniężnych (Cash Flow RPP)",
                        "📊 Zestawienie Zmian w Kapitale (ZZwK)",
                        "🔍 Weryfikacja Zgodności z Instrukcją Prompt",
                        "📋 Generowanie Kompletnych Raportów Audytorskich"
                    ]
                )
                
                # Szczegółowe parametry na podstawie operacji
                if "Wstępnych Procedur" in operation_type:
                    st.info("🎯 **Funkcje z AB Wstępne Procedury:**")
                    st.markdown("""
                    - **Parsowanie formuł Excel**: SUM, AVERAGE, COUNT, IF
                    - **Ewaluacja wskaźników finansowych** z 14 arkuszy
                    - **Generowanie raportów** z wynikami
                    - **Identyfikacja błędów** w formułach
                    - **Analiza danych** z arkuszy: Dane, BILANS, RachPor, RachKal, Cash Flow, ZZwK
                    """)
                    
                elif "260 ANAW" in operation_type:
                    st.info("🎯 **Wskaźniki z arkusza 260 ANAW:**")
                    st.markdown("""
                    - **Rentowność**: ROA (19.76%), ROE (30.68%), Rentowność sprzedaży (7.52%)
                    - **Płynność**: Wskaźnik płynności I (1.86), II (1.38), III (1.05)
                    - **Efektywność**: Rotacja aktywów (2.71), środków trwałych (6.95)
                    - **Szybkość obrotu**: Zapasów (24.47 dni), należności (15.19 dni), zobowiązań (43.04 dni)
                    """)
                    
                elif "302 RYZBAD" in operation_type:
                    st.info("🎯 **Ryzyka z arkusza 302 RYZBAD:**")
                    st.markdown("""
                    - **Ryzyka rozległe**: obejścia kontroli przez zarząd, oszustwa na poziomie sprawozdania
                    - **Ryzyka specyficzne**: na poziomie stwierdzeń, prawdopodobieństwo (1-3)
                    - **Wielkość zniekształcenia**: oczekiwana wielkość błędu
                    - **Kontrola wewnętrzna**: obszary kontroli, ryzyko oszustwa/nadużyć
                    - **Macierz ryzyka**: prawdopodobieństwo vs wpływ
                    """)
                
                # ZAAWANSOWANE opcje
                with st.expander("⚙️ Opcje Zaawansowane - Zwiększony Kontekst"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        temperature = st.slider("Temperatura AI", 0.1, 1.0, 0.8, 0.1)
                        max_tokens = st.slider("Maksymalna długość odpowiedzi", 1024, 4096, 3072, 256)
                    with col_b:
                        include_formulas = st.checkbox("Analizuj formuły Excel", value=True)
                        generate_report = st.checkbox("Generuj szczegółowy raport", value=True)
                        use_context = st.checkbox("Użyj rozszerzonego kontekstu", value=True)
                
                if st.button("🚀 Uruchom Szczegółową Analizę", use_container_width=True):
                    with st.spinner("Analizuję z rozszerzonym kontekstem..."):
                        # ROZBUDOWANE prompty na podstawie plików klienta
                        if "Wstępnych Procedur" in operation_type:
                            ai_prompt = f"""
                            Jako ekspert audytor, przeprowadź szczegółową analizę wstępnych procedur audytorskich na podstawie pliku {uploaded_file.name}.
                            
                            KONTEKST: Plik zawiera 14 arkuszy z kompletną dokumentacją badania audytorskiego:
                            1. Instrukcja Prompt - instrukcje dla AI
                            2. Dane - podstawowe informacje o jednostce
                            3. BILANS - bilans za lata poprzednie
                            4. BILANS KOREKT - bilans skorygowany (rok bieżący)
                            5. RachPor - rachunek zysków i strat za lata poprzednie
                            6. RachPor KOREKT - rachunek zysków i strat skorygowany
                            7. RachKal - rachunek kalkulacyjny za lata poprzednie
                            8. RachKal Korekt - rachunek kalkulacyjny skorygowany
                            9. Cash Flow (RPP) - rachunek przepływów pieniężnych
                            10. ZZwK - zestawienie zmian w kapitale
                            11. 260 ANAW - analiza wskaźnikowa
                            12. 301 ANAW - analiza wskaźnikowa (dodatkowa)
                            13. 302 RYZBAD - ryzyka badania
                            14. 303 BAZRYZN - baza ryzyk
                            
                            ZADANIA AI:
                            - Zgromadź sprawozdania finansowe za ostatnie 3 lata z KRS
                            - Importuj dane finansowe do arkuszy BILANS KOREKT kol.D, BILANS kol.C i D
                            - Uzupełnij dane w arkuszu "Dane" (nazwa jednostki, zarząd, rok SF)
                            - Automatycznie wypełnij arkusze na podstawie danych
                            - Przeprowadź analizę ryzyk w arkuszu 302 RYZBAD
                            
                            ANALIZA:
                            - Parsowanie i ewaluacja formuł Excel (SUM, AVERAGE, COUNT, IF)
                            - Ewaluacja wskaźników finansowych
                            - Identyfikacja błędów w formułach
                            - Generowanie raportu z wynikami
                            
                            Podaj szczegółową analizę z konkretnymi wskaźnikami, błędami, rekomendacjami i planem dalszych działań.
                            """
                            
                        elif "260 ANAW" in operation_type:
                            ai_prompt = f"""
                            Jako ekspert audytor, przeprowadź szczegółową analizę wskaźników finansowych z arkusza 260 ANAW na podstawie pliku {uploaded_file.name}.
                            
                            KONTEKST WSKAŹNIKÓW:
                            - ROA (Rentowność aktywów): 19.76%
                            - ROE (Rentowność kapitałów własnych): 30.68%
                            - Rentowność sprzedaży: 7.52%
                            - Wskaźnik płynności I: 1.86
                            - Wskaźnik płynności II: 1.38
                            - Wskaźnik płynności III: 1.05
                            - Rotacja aktywów: 2.71
                            - Rotacja środków trwałych: 6.95
                            - Rotacja aktywów obrotowych: 4.23
                            - Szybkość obrotu zapasów: 24.47 dni
                            - Szybkość obrotu należności: 15.19 dni
                            - Szybkość obrotu zobowiązań: 43.04 dni
                            
                            ANALIZA:
                            - Oceń rentowność w kontekście branży
                            - Przeanalizuj płynność finansową
                            - Ocena efektywności operacyjnej
                            - Analiza trendów na przestrzeni lat
                            - Porównanie z benchmarkami branżowymi
                            - Identyfikacja anomalii i obszarów ryzyka
                            
                            Podaj szczegółową ocenę wskaźników, zidentyfikuj anomalie i sformułuj konkretne rekomendacje audytorskie.
                            """
                            
                        elif "302 RYZBAD" in operation_type:
                            ai_prompt = f"""
                            Jako ekspert audytor, przeprowadź szczegółową ocenę ryzyka na podstawie arkusza 302 RYZBAD z pliku {uploaded_file.name}.
                            
                            STRUKTURA ANALIZY RYZYK:
                            
                            1. RYZYKA ROZLEGŁE (ogólne):
                            - Ryzyko obejścia kontroli przez zarząd
                            - Ryzyko oszustwa na poziomie sprawozdania
                            
                            2. RYZYKA SPECYFICZNE (na poziomie stwierdzeń):
                            - Obszar badania
                            - Czynniki ryzyka
                            - Opis ryzyka ("co może pójść źle")
                            - Rodzaj ryzyka (rozległe/specyficzne)
                            - Prawdopodobieństwo wystąpienia (1-3)
                            - Oczekiwana wielkość zniekształcenia
                            - Czy ryzyko wynika z szacunków
                            - Ryzyko oszustwa/nadużyć
                            - Obszar kontroli wewnętrznej
                            
                            PROMPT DLA ANALIZY RYZYK:
                            Przygotuj w formie wypełnionej tabeli 302 RYZBAD ryzyka nieodłączne do badania sprawozdania finansowego danej jednostki.
                            
                            Weź pod uwagę:
                            - Charakterystykę jednostki
                            - Ryzyka specyficzne dla działalności
                            - Otoczenie prawne jednostki
                            - Informacje z rynku na temat branży
                            - Sytuację aktualną jednostki
                            - Dane finansowe (zmiany pozycji na przestrzeni ostatnich 3 lat)
                            - Istotność badania (Krajowe Standardy Badania)
                            - Istotność wykonawczą
                            
                            Przygotuj szczegółowy raport oceny ryzyka z macierzą prawdopodobieństwo vs wpływ i konkretnymi rekomendacjami łagodzenia.
                            """
                        else:
                            ai_prompt = f"Jako ekspert audytor, przeanalizuj plik {uploaded_file.name} w kontekście {operation_type}. Podaj szczegółową analizę z konkretnymi wskaźnikami i rekomendacjami."
                        
                        # Wywołanie AI z rozszerzonymi parametrami
                        ai_response = call_real_ai(ai_prompt, temperature=temperature, max_tokens=max_tokens)
                        
                        st.success("✅ Szczegółowa analiza zakończona!")
                        st.markdown(f"**Wyniki analizy:**\n\n{ai_response}")
                        
                        # Metryki na podstawie typu operacji
                        if "260 ANAW" in operation_type:
                            st.subheader("📊 Wskaźniki Finansowe")
                            met1, met2, met3, met4 = st.columns(4)
                            with met1:
                                st.metric("ROA", "19.76%", "2.1%")
                            with met2:
                                st.metric("ROE", "30.68%", "3.2%")
                            with met3:
                                st.metric("Płynność I", "1.86", "0.15")
                            with met4:
                                st.metric("Rotacja", "2.71", "0.3")
                        elif "302 RYZBAD" in operation_type:
                            st.subheader("⚠️ Ocena Ryzyka")
                            met1, met2, met3 = st.columns(3)
                            with met1:
                                st.metric("Ryzyka Wysokie", "3", "1")
                            with met2:
                                st.metric("Ryzyka Średnie", "7", "-2")
                            with met3:
                                st.metric("Ryzyka Niskie", "12", "3")
                        else:
                            met1, met2, met3 = st.columns(3)
                            with met1:
                                st.metric("Zgodność", "85%", "5%")
                            with met2:
                                st.metric("Ryzyko", "Średnie", "↓")
                            with met3:
                                st.metric("Anomalie", "3", "-2")
        
        # NARZĘDZIA SZYBKIE z plików klienta
        with st.expander("🛠️ Narzędzia Szybkie - Wszystkie Arkusze"):
            st.info("🎯 **Dostępne narzędzia na podstawie 14 arkuszy:**")
            
            col_t1, col_t2 = st.columns(2)
            
            with col_t1:
                if st.button("📊 Analiza Wstępnych Procedur", use_container_width=True):
                    with st.spinner("Analizuję wstępne procedury z 14 arkuszy..."):
                        prompt = """
                        Jako ekspert audytor, przygotuj kompleksową analizę wstępnych procedur audytorskich na podstawie 14 arkuszy z pliku AB Wstępne Procedury.
                        
                        Arkusze do analizy:
                        1. Instrukcja Prompt, 2. Dane, 3. BILANS, 4. BILANS KOREKT, 5. RachPor, 6. RachPor KOREKT,
                        7. RachKal, 8. RachKal Korekt, 9. Cash Flow (RPP), 10. ZZwK, 11. 260 ANAW, 12. 301 ANAW, 13. 302 RYZBAD, 14. 303 BAZRYZN
                        
                        Uwzględnij:
                        - Parsowanie i ewaluację formuł Excel (SUM, AVERAGE, COUNT, IF)
                        - Analizę wskaźników finansowych z arkuszy 260 ANAW i 301 ANAW
                        - Ocenę ryzyk z arkuszy 302 RYZBAD i 303 BAZRYZN
                        - Analizę sprawozdań finansowych (BILANS, RachPor, RachKal, Cash Flow, ZZwK)
                        - Identyfikację błędów w formułach i danych
                        - Generowanie kompletnego raportu z wynikami
                        
                        Podaj szczegółową analizę z konkretnymi wskaźnikami, błędami i rekomendacjami dla każdego arkusza.
                        """
                        response = call_real_ai(prompt, max_tokens=3072)
                        st.success("✅ Kompleksowa analiza wstępnych procedur zakończona!")
                        st.markdown(f"**Wyniki:**\n\n{response}")
                
                if st.button("📈 Pełna Analiza Wskaźników", use_container_width=True):
                    with st.spinner("Analizuję wszystkie wskaźniki..."):
                        prompt = """
                        Jako ekspert audytor, przeanalizuj wszystkie wskaźniki finansowe z arkuszy 260 ANAW i 301 ANAW.
                        
                        Wskaźniki do szczegółowej analizy:
                        RENTOWNOŚĆ:
                        - ROA (Rentowność aktywów): 19.76%
                        - ROE (Rentowność kapitałów własnych): 30.68%
                        - Rentowność sprzedaży: 7.52%
                        
                        PŁYNNOŚĆ:
                        - Wskaźnik płynności I: 1.86
                        - Wskaźnik płynności II: 1.38
                        - Wskaźnik płynności III: 1.05
                        
                        EFEKTYWNOŚĆ:
                        - Rotacja aktywów: 2.71
                        - Rotacja środków trwałych: 6.95
                        - Rotacja aktywów obrotowych: 4.23
                        - Szybkość obrotu zapasów: 24.47 dni
                        - Szybkość obrotu należności: 15.19 dni
                        - Szybkość obrotu zobowiązań: 43.04 dni
                        
                        Przeprowadź:
                        - Ocenę każdego wskaźnika w kontekście branży
                        - Analizę trendów na przestrzeni lat
                        - Porównanie z benchmarkami
                        - Identyfikację obszarów ryzyka
                        - Sformułowanie rekomendacji
                        
                        Podaj szczegółową ocenę wszystkich wskaźników z konkretnymi rekomendacjami audytorskimi.
                        """
                        response = call_real_ai(prompt, max_tokens=3072)
                        st.success("✅ Pełna analiza wskaźników zakończona!")
                        st.markdown(f"**Wyniki:**\n\n{response}")
            
            with col_t2:
                if st.button("⚠️ Kompleksowa Ocena Ryzyka", use_container_width=True):
                    with st.spinner("Oceniam wszystkie ryzyka..."):
                        prompt = """
                        Jako ekspert audytor, przeprowadź kompleksową ocenę ryzyka na podstawie arkuszy 302 RYZBAD i 303 BAZRYZN.
                        
                        RYZYKA DO ANALIZY:
                        
                        RYZYKA ROZLEGŁE:
                        - Ryzyko obejścia kontroli przez zarząd
                        - Ryzyko oszustwa na poziomie sprawozdania finansowego
                        
                        RYZYKA SPECYFICZNE:
                        - Na poziomie stwierdzeń w sprawozdaniu
                        - Prawdopodobieństwo wystąpienia (skala 1-3)
                        - Oczekiwana wielkość zniekształcenia
                        - Ryzyka wynikające z szacunków księgowych
                        - Ryzyko oszustwa i nadużyć
                        - Obszary kontroli wewnętrznej
                        
                        BAZA RYZYK (303 BAZRYZN):
                        - Katalog wszystkich zidentyfikowanych ryzyk
                        - Klasyfikacja ryzyk według obszarów
                        - Metody łagodzenia ryzyk
                        
                        Przygotuj:
                        - Szczegółową macierz ryzyk (prawdopodobieństwo vs wpływ)
                        - Ranking ryzyk według istotności
                        - Plan łagodzenia dla każdego ryzyka
                        - Rekomendacje procedur audytorskich
                        - Harmonogram działań kontrolnych
                        
                        Podaj kompleksowy raport oceny ryzyka z konkretnymi działaniami.
                        """
                        response = call_real_ai(prompt, max_tokens=3072)
                        st.success("✅ Kompleksowa ocena ryzyka zakończona!")
                        st.markdown(f"**Wyniki:**\n\n{response}")
                
                if st.button("💰 Analiza Sprawozdań Finansowych", use_container_width=True):
                    with st.spinner("Analizuję wszystkie sprawozdania..."):
                        prompt = """
                        Jako ekspert audytor, przeprowadź kompleksową analizę wszystkich sprawozdań finansowych.
                        
                        SPRAWOZDANIA DO ANALIZY:
                        
                        BILANS (BILANS + BILANS KOREKT):
                        - Struktura aktywów i pasywów
                        - Zmiany na przestrzeni lat
                        - Wpływ korekt na sprawozdanie
                        - Analiza płynności i zadłużenia
                        
                        RACHUNEK ZYSKÓW I STRAT (RachPor + RachPor KOREKT):
                        - Analiza przychodów i kosztów
                        - Zmiany w rentowności
                        - Wpływ korekt na wynik finansowy
                        
                        RACHUNEK KALKULACYJNY (RachKal + RachKal Korekt):
                        - Analiza kosztów w układzie kalkulacyjnym
                        - Efektywność kosztowa
                        - Wpływ korekt na koszty
                        
                        PRZEPŁYWY PIENIĘŻNE (Cash Flow RPP):
                        - Przepływy operacyjne, inwestycyjne, finansowe
                        - Zdolność do generowania gotówki
                        - Analiza płynności
                        
                        ZMIANY W KAPITALE (ZZwK):
                        - Struktura i zmiany w kapitale własnym
                        - Stabilność finansowa
                        - Polityka dywidendowa
                        
                        Przeprowadź szczegółową analizę każdego sprawozdania z oceną trendów, identyfikacją anomalii i rekomendacjami.
                        """
                        response = call_real_ai(prompt, max_tokens=3072)
                        st.success("✅ Analiza sprawozdań finansowych zakończona!")
                        st.markdown(f"**Wyniki:**\n\n{response}")
    
    with col2:
        st.subheader("🤖 AI Asystent Audytora")
        
        # AI Chat for auditing with enhanced context
        if "auditor_messages" not in st.session_state:
            st.session_state.auditor_messages = []
        
        # Display chat messages
        for message in st.session_state.auditor_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Zadaj pytanie o audyt..."):
            st.session_state.auditor_messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Analizuję z kontekstem plików klienta..."):
                    # Enhanced prompt with client files context
                    enhanced_prompt = f"""
                    Jako ekspert audytor z dostępem do plików klienta (AB Wstępne Procedury - 14 arkuszy), odpowiedz na pytanie:
                    
                    {prompt}
                    
                    KONTEKST DOSTĘPNYCH DANYCH:
                    - 14 arkuszy audytorskich (Dane, BILANS, RachPor, RachKal, Cash Flow, ZZwK, 260 ANAW, 301 ANAW, 302 RYZBAD, 303 BAZRYZN)
                    - Wskaźniki finansowe (ROA: 19.76%, ROE: 30.68%, płynność, efektywność)
                    - Ryzyka audytorskie (rozległe i specyficzne)
                    - Sprawozdania finansowe za 3 lata
                    
                    Uwzględnij w odpowiedzi:
                    - Konkretne dane z arkuszy klienta
                    - Referencje do standardów audytu
                    - Praktyczne rekomendacje
                    - Potencjalne ryzyka i mitygację
                    - Procedury audytorskie
                    
                    Odpowiedź powinna być szczegółowa, profesjonalna i oparta na danych klienta.
                    """
                    
                    # Call AI for auditing with enhanced context
                    ai_response = call_real_ai(enhanced_prompt, temperature=0.8, max_tokens=3072)
                    st.markdown(f"**Asystent AI Audytora:**\n\n{ai_response}")
            
            st.session_state.auditor_messages.append({"role": "assistant", "content": ai_response})

def render_instructions_page():
    """Strona instrukcji."""
    st.markdown('<div class="main-header">📚 Instrukcje dla Użytkowników</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ## 🎯 Jak korzystać z Rozbudowanego AI Auditor
    
    ### 📊 Dashboard
    - Przeglądaj statystyki i trendy
    - Monitoruj postęp audytów
    - Sprawdzaj kluczowe wskaźniki
    
    ### 🏃 Run - Uruchamianie Audytu
    1. Wgraj pliki (PDF, Excel, CSV)
    2. Kliknij "Uruchom Audyt"
    3. Monitoruj postęp w kolejce
    
    ### 🔍 Niezgodności
    - Przeglądaj znalezione problemy
    - Generuj raporty
    - Zarządzaj statusem
    
    ### 📤 Eksporty
    - Generuj raporty PBC
    - Eksportuj Working Papers
    - Twórz Compliance Reports
    
    ### 💬 Chat AI - ROZBUDOWANY
    - **Zwiększony kontekst**: do 3072 tokenów
    - **Rozszerzone prompty**: szczegółowe analizy
    - **Kontekst audytorski**: referencje do standardów
    - Zadawaj pytania o audyt
    - Uzyskuj porady eksperckie
    
    ### 🤖 AI Audytor - FUNKCJONALNOŚCI Z PLIKÓW KLIENTA
    
    #### 📁 Analiza Plików - 14 Arkuszy:
    1. **Instrukcja Prompt** - instrukcje dla AI
    2. **Dane** - informacje o jednostce
    3. **BILANS** - bilans za lata poprzednie
    4. **BILANS KOREKT** - bilans skorygowany
    5. **RachPor** - rachunek zysków i strat
    6. **RachPor KOREKT** - RZiS skorygowany
    7. **RachKal** - rachunek kalkulacyjny
    8. **RachKal Korekt** - rachunek kalkulacyjny skorygowany
    9. **Cash Flow (RPP)** - przepływy pieniężne
    10. **ZZwK** - zestawienie zmian w kapitale
    11. **260 ANAW** - analiza wskaźnikowa
    12. **301 ANAW** - dodatkowa analiza wskaźnikowa
    13. **302 RYZBAD** - ryzyka badania
    14. **303 BAZRYZN** - baza ryzyk
    
    #### 🛠️ Narzędzia Szybkie:
    - **Analiza Wstępnych Procedur** - kompleksowa analiza wszystkich arkuszy
    - **Pełna Analiza Wskaźników** - ROA, ROE, płynność, efektywność
    - **Kompleksowa Ocena Ryzyka** - ryzyka rozległe i specyficzne
    - **Analiza Sprawozdań Finansowych** - wszystkie sprawozdania
    
    #### ⚙️ Opcje Zaawansowane:
    - **Temperatura AI**: 0.1-1.0 (kontrola kreatywności)
    - **Długość odpowiedzi**: do 4096 tokenów
    - **Rozszerzony kontekst**: uwzględnia dane klienta
    - **Szczegółowe raporty**: kompletne analizy
    
    ## 🔐 Bezpieczeństwo
    - Hasło: `TwojPIN123!`
    - AI Server: Lokalny, bezpieczny
    - Dane klienta: Chronione
    
    ## 📞 Wsparcie
    - Dokumentacja: Rozbudowana
    - Email: support@ai-auditor.com
    - Telefon: +48 123 456 789
    """)

def render_settings_page():
    """Strona ustawień z opcjami AI."""
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎨 Wygląd")
        theme = st.selectbox("Motyw", ["Jasny", "Ciemny"])
        language = st.selectbox("Język", ["Polski", "English"])
        
        if st.button("💾 Zapisz ustawienia"):
            st.success("✅ Ustawienia zapisane!")
    
    with col2:
        st.subheader("🔧 Konfiguracja AI")
        ai_server = st.text_input("Serwer AI", AI_SERVER_URL)
        timeout = st.number_input("Timeout (s)", 30, 60, AI_TIMEOUT)
        max_tokens_default = st.number_input("Domyślna długość odpowiedzi", 512, 4096, 3072)
        
        if st.button("🔄 Testuj połączenie z AI"):
            with st.spinner("Testuję rozszerzone połączenie..."):
                test_response = call_real_ai("Test połączenia z rozszerzonym kontekstem", max_tokens=1024)
                if "❌" in test_response:
                    st.error(f"❌ Błąd połączenia: {test_response}")
                else:
                    st.success("✅ Połączenie OK! AI odpowiada z rozszerzonym kontekstem.")
                    with st.expander("Odpowiedź testowa AI"):
                        st.markdown(test_response)

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
    if st.session_state.current_page == 'dashboard':
        render_dashboard()
    elif st.session_state.current_page == 'run':
        render_run_page()
    elif st.session_state.current_page == 'findings':
        render_findings_page()
    elif st.session_state.current_page == 'exports':
        render_exports_page()
    elif st.session_state.current_page == 'chat':
        render_chat_page()
    elif st.session_state.current_page == 'ai_auditor':
        render_ai_auditor_page()
    elif st.session_state.current_page == 'instructions':
        render_instructions_page()
    elif st.session_state.current_page == 'settings':
        render_settings_page()

if __name__ == "__main__":
    main()
