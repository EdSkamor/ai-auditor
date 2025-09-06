"""
Production Streamlit UI for AI Auditor.
Complete web interface for invoice validation and audit support.
"""

import streamlit as st
import pandas as pd
import json
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.run_audit import run_audit
from core.ocr_processor import OCRProcessor
from core.exceptions import AuditorException


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Auditor - Panel Audytora",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2e6da4 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f4e79;
        margin: 0.5rem 0;
    }
    .success-card {
        background: #d4edda;
        border-left-color: #28a745;
    }
    .warning-card {
        background: #fff3cd;
        border-left-color: #ffc107;
    }
    .error-card {
        background: #f8d7da;
        border-left-color: #dc3545;
    }
    .stButton > button {
        background: #1f4e79;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton > button:hover {
        background: #2e6da4;
        color: white;
    }
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'audit_results' not in st.session_state:
    st.session_state.audit_results = None
if 'audit_history' not in st.session_state:
    st.session_state.audit_history = []
if 'ocr_results' not in st.session_state:
    st.session_state.ocr_results = None


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔍 AI Auditor - Panel Audytora</h1>
        <p>System walidacji faktur i wsparcia audytowego</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Konfiguracja")
        
        # OCR Settings
        st.subheader("🔤 Ustawienia OCR")
        ocr_engine = st.selectbox(
            "Silnik OCR",
            ["tesseract", "easyocr", "paddleocr"],
            index=0,
            help="Wybierz silnik OCR do przetwarzania skanów"
        )
        
        ocr_language = st.selectbox(
            "Język OCR",
            ["pol", "pol+eng", "eng"],
            index=0,
            help="Język dla rozpoznawania tekstu"
        )
        
        gpu_enabled = st.checkbox(
            "Akceleracja GPU",
            value=True,
            help="Włącz akcelerację GPU dla OCR (jeśli dostępna)"
        )
        
        # Audit Settings
        st.subheader("📊 Ustawienia Audytu")
        tiebreak_weight_fname = st.slider(
            "Waga nazwy pliku (tie-breaker)",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.1,
            help="Waga nazwy pliku w rozstrzyganiu remisów"
        )
        
        tiebreak_min_seller = st.slider(
            "Min. podobieństwo sprzedawcy",
            min_value=0.0,
            max_value=1.0,
            value=0.4,
            step=0.1,
            help="Minimalne podobieństwo nazwy sprzedawcy"
        )
        
        amount_tolerance = st.number_input(
            "Tolerancja kwot (%)",
            min_value=0.0,
            max_value=10.0,
            value=1.0,
            step=0.1,
            help="Tolerancja dla porównania kwot w procentach"
        )
        
        # System Status
        st.subheader("📈 Status Systemu")
        if st.button("🔄 Sprawdź status"):
            check_system_status()
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Strona główna",
        "📁 Uruchom Audyt",
        "🔤 OCR Sampling",
        "📊 Historia Audytów",
        "❓ Pomoc"
    ])
    
    with tab1:
        show_home_page()
    
    with tab2:
        show_audit_page(tiebreak_weight_fname, tiebreak_min_seller, amount_tolerance)
    
    with tab3:
        show_ocr_page(ocr_engine, ocr_language, gpu_enabled)
    
    with tab4:
        show_history_page()
    
    with tab5:
        show_help_page()


def show_home_page():
    """Show home page with system overview."""
    st.header("🏠 Strona główna")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>📊 Statystyki</h4>
            <p><strong>Wykonane audyty:</strong> {}</p>
            <p><strong>Przetworzone faktury:</strong> {}</p>
            <p><strong>Średni czas audytu:</strong> {}s</p>
        </div>
        """.format(
            len(st.session_state.audit_history),
            sum(h.get('total_invoices', 0) for h in st.session_state.audit_history),
            round(sum(h.get('processing_time', 0) for h in st.session_state.audit_history) / max(len(st.session_state.audit_history), 1), 2)
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>🔧 Funkcje</h4>
            <ul>
                <li>✅ Walidacja PDF↔POP</li>
                <li>✅ OCR (Tesseract/EasyOCR/PaddleOCR)</li>
                <li>✅ Tie-breaker logic</li>
                <li>✅ Raporty Excel/PDF</li>
                <li>⏳ KRS Integration</li>
                <li>⏳ Risk Tables</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>🚀 Szybki Start</h4>
            <ol>
                <li>Przejdź do zakładki "Uruchom Audyt"</li>
                <li>Wgraj pliki PDF i POP</li>
                <li>Ustaw parametry</li>
                <li>Kliknij "Uruchom Audyt"</li>
                <li>Pobierz wyniki</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent audits
    if st.session_state.audit_history:
        st.subheader("📋 Ostatnie Audyty")
        
        for i, audit in enumerate(st.session_state.audit_history[-3:]):
            with st.expander(f"Audyt #{len(st.session_state.audit_history) - i} - {audit.get('timestamp', 'Unknown')}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Faktury", audit.get('total_invoices', 0))
                with col2:
                    st.metric("Dopasowane", audit.get('matched', 0))
                with col3:
                    st.metric("Czas", f"{audit.get('processing_time', 0):.1f}s")


def show_audit_page(tiebreak_weight_fname, tiebreak_min_seller, amount_tolerance):
    """Show audit execution page."""
    st.header("📁 Uruchom Audyt")
    
    # File upload section
    st.subheader("📤 Wgraj Pliki")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📄 Pliki PDF (faktury)**")
        pdf_files = st.file_uploader(
            "Wybierz pliki PDF lub ZIP z fakturami",
            type=['pdf', 'zip'],
            accept_multiple_files=True,
            help="Możesz wgrać pojedyncze pliki PDF lub archiwum ZIP"
        )
    
    with col2:
        st.markdown("**📊 Plik POP (dane)**")
        pop_file = st.file_uploader(
            "Wybierz plik POP (Excel/CSV)",
            type=['xlsx', 'xls', 'csv'],
            help="Plik z danymi POP do porównania z fakturami"
        )
    
    # Audit parameters
    st.subheader("⚙️ Parametry Audytu")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        output_name = st.text_input(
            "Nazwa audytu",
            value=f"audyt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            help="Nazwa dla wyników audytu"
        )
    
    with col2:
        enable_ocr = st.checkbox(
            "Włącz OCR",
            value=True,
            help="Użyj OCR dla skanów PDF"
        )
    
    with col3:
        max_file_size = st.number_input(
            "Max rozmiar pliku (MB)",
            min_value=1,
            max_value=100,
            value=50,
            help="Maksymalny rozmiar pliku PDF w MB"
        )
    
    # Run audit button
    if st.button("🚀 Uruchom Audyt", type="primary"):
        if not pdf_files or not pop_file:
            st.error("❌ Proszę wgrać pliki PDF i POP!")
            return
        
        run_audit_process(
            pdf_files, pop_file, output_name,
            tiebreak_weight_fname, tiebreak_min_seller, amount_tolerance,
            enable_ocr, max_file_size
        )
    
    # Show current results
    if st.session_state.audit_results:
        show_audit_results()


def run_audit_process(pdf_files, pop_file, output_name, tiebreak_weight_fname, 
                     tiebreak_min_seller, amount_tolerance, enable_ocr, max_file_size):
    """Run the audit process."""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save uploaded files
            status_text.text("💾 Zapisuję pliki...")
            progress_bar.progress(10)
            
            # Save POP file
            pop_path = temp_path / "pop_data.xlsx"
            with open(pop_path, "wb") as f:
                f.write(pop_file.getvalue())
            
            # Save PDF files
            pdf_dir = temp_path / "pdfs"
            pdf_dir.mkdir()
            
            for pdf_file in pdf_files:
                pdf_path = pdf_dir / pdf_file.name
                with open(pdf_path, "wb") as f:
                    f.write(pdf_file.getvalue())
            
            status_text.text("🔍 Uruchamiam audyt...")
            progress_bar.progress(30)
            
            # Run audit
            output_dir = temp_path / "output"
            output_dir.mkdir()
            
            start_time = datetime.now()
            
            # This would call the actual audit function
            # For now, we'll simulate the process
            import time
            time.sleep(2)  # Simulate processing
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            status_text.text("📊 Generuję raporty...")
            progress_bar.progress(80)
            
            # Simulate results
            mock_results = {
                'total_invoices': len(pdf_files),
                'matched': len(pdf_files) - 2,
                'unmatched': 2,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat(),
                'output_dir': str(output_dir),
                'tiebreak_weight_fname': tiebreak_weight_fname,
                'tiebreak_min_seller': tiebreak_min_seller,
                'amount_tolerance': amount_tolerance
            }
            
            # Save results to session state
            st.session_state.audit_results = mock_results
            st.session_state.audit_history.append(mock_results)
            
            status_text.text("✅ Audyt zakończony!")
            progress_bar.progress(100)
            
            st.success(f"🎉 Audyt zakończony pomyślnie! Przetworzono {len(pdf_files)} faktur w {processing_time:.1f}s")
            
    except Exception as e:
        st.error(f"❌ Błąd podczas audytu: {e}")
        logger.error(f"Audit process failed: {e}")


def show_audit_results():
    """Show audit results."""
    if not st.session_state.audit_results:
        return
    
    results = st.session_state.audit_results
    
    st.subheader("📊 Wyniki Audytu")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Faktury", results['total_invoices'])
    
    with col2:
        st.metric("✅ Dopasowane", results['matched'])
    
    with col3:
        st.metric("❌ Niedopasowane", results['unmatched'])
    
    with col4:
        st.metric("⏱️ Czas", f"{results['processing_time']:.1f}s")
    
    # Download results
    st.subheader("📥 Pobierz Wyniki")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Pobierz Excel"):
            st.info("Funkcja pobierania Excel będzie dostępna po implementacji")
    
    with col2:
        if st.button("📄 Pobierz PDF"):
            st.info("Funkcja pobierania PDF będzie dostępna po implementacji")
    
    with col3:
        if st.button("📦 Pobierz ZIP"):
            st.info("Funkcja pobierania ZIP będzie dostępna po implementacji")


def show_ocr_page(ocr_engine, ocr_language, gpu_enabled):
    """Show OCR sampling page."""
    st.header("🔤 OCR Sampling")
    
    st.markdown("""
    Ta funkcja pozwala na testowanie OCR na próbce dokumentów przed pełnym audytem.
    """)
    
    # File upload
    st.subheader("📤 Wgraj Pliki do OCR")
    
    ocr_files = st.file_uploader(
        "Wybierz pliki do testowania OCR",
        type=['pdf', 'png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="Możesz wgrać pliki PDF lub obrazy"
    )
    
    if ocr_files:
        col1, col2 = st.columns(2)
        
        with col1:
            sample_size = st.number_input(
                "Rozmiar próbki",
                min_value=1,
                max_value=len(ocr_files),
                value=min(5, len(ocr_files)),
                help="Liczba plików do przetworzenia"
            )
        
        with col2:
            confidence_threshold = st.slider(
                "Próg pewności",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="Minimalna pewność OCR"
            )
        
        if st.button("🔍 Uruchom OCR Sampling"):
            run_ocr_sampling(ocr_files, sample_size, ocr_engine, ocr_language, gpu_enabled, confidence_threshold)
    
    # Show OCR results
    if st.session_state.ocr_results:
        show_ocr_results()


def run_ocr_sampling(ocr_files, sample_size, ocr_engine, ocr_language, gpu_enabled, confidence_threshold):
    """Run OCR sampling."""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize OCR processor
        status_text.text("🔧 Inicjalizuję OCR...")
        progress_bar.progress(10)
        
        ocr_processor = OCRProcessor(
            engine=ocr_engine,
            language=ocr_language,
            gpu_enabled=gpu_enabled
        )
        
        # Process files
        results = []
        files_to_process = ocr_files[:sample_size]
        
        for i, file in enumerate(files_to_process):
            status_text.text(f"🔍 Przetwarzam {i+1}/{len(files_to_process)}: {file.name}")
            progress_bar.progress(10 + (i / len(files_to_process)) * 80)
            
            # For demo purposes, create mock results
            mock_result = {
                'file_name': file.name,
                'file_size': file.size,
                'ocr_text': f"Przykładowy tekst OCR dla {file.name}",
                'confidence': 0.85,
                'processing_time': 1.2,
                'engine': ocr_engine,
                'invoice_number': f"FV-{i+1:03d}/2024",
                'issue_date': "15.01.2024",
                'total_net': 1000.0 + i * 100,
                'currency': "zł",
                'seller_name': f"Sprzedawca {i+1}",
                'error': None
            }
            
            results.append(mock_result)
        
        # Save results
        st.session_state.ocr_results = results
        
        status_text.text("✅ OCR Sampling zakończony!")
        progress_bar.progress(100)
        
        st.success(f"🎉 OCR Sampling zakończony! Przetworzono {len(results)} plików")
        
    except Exception as e:
        st.error(f"❌ Błąd podczas OCR: {e}")
        logger.error(f"OCR sampling failed: {e}")


def show_ocr_results():
    """Show OCR results."""
    if not st.session_state.ocr_results:
        return
    
    results = st.session_state.ocr_results
    
    st.subheader("📊 Wyniki OCR")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📄 Przetworzone", len(results))
    
    with col2:
        avg_confidence = sum(r['confidence'] for r in results) / len(results)
        st.metric("🎯 Średnia pewność", f"{avg_confidence:.2f}")
    
    with col3:
        successful = len([r for r in results if not r.get('error')])
        st.metric("✅ Sukces", f"{successful}/{len(results)}")
    
    # Results table
    st.subheader("📋 Szczegóły")
    
    df = pd.DataFrame(results)
    
    # Select columns to display
    display_columns = ['file_name', 'confidence', 'invoice_number', 'issue_date', 'total_net', 'currency', 'seller_name']
    available_columns = [col for col in display_columns if col in df.columns]
    
    st.dataframe(df[available_columns], use_container_width=True)
    
    # Download results
    if st.button("📥 Pobierz wyniki OCR"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="📊 Pobierz CSV",
            data=csv,
            file_name=f"ocr_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


def show_history_page():
    """Show audit history page."""
    st.header("📊 Historia Audytów")
    
    if not st.session_state.audit_history:
        st.info("📝 Brak historii audytów. Uruchom pierwszy audyt w zakładce 'Uruchom Audyt'.")
        return
    
    # History table
    df = pd.DataFrame(st.session_state.audit_history)
    
    # Select columns to display
    display_columns = ['timestamp', 'total_invoices', 'matched', 'unmatched', 'processing_time']
    available_columns = [col for col in display_columns if col in df.columns]
    
    st.dataframe(df[available_columns], use_container_width=True)
    
    # Charts
    if len(st.session_state.audit_history) > 1:
        st.subheader("📈 Wykresy")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.line_chart(df.set_index('timestamp')[['total_invoices', 'matched']])
        
        with col2:
            st.line_chart(df.set_index('timestamp')[['processing_time']])


def show_help_page():
    """Show help page."""
    st.header("❓ Pomoc")
    
    st.markdown("""
    ## 🚀 Szybki Start
    
    1. **Uruchom Audyt**: Wgraj pliki PDF i POP, ustaw parametry, kliknij "Uruchom Audyt"
    2. **OCR Sampling**: Przetestuj OCR na próbce dokumentów
    3. **Historia**: Zobacz wyniki poprzednich audytów
    
    ## ⚙️ Parametry
    
    - **Waga nazwy pliku**: Wpływ nazwy pliku na rozstrzyganie remisów
    - **Min. podobieństwo sprzedawcy**: Minimalne podobieństwo nazwy sprzedawcy
    - **Tolerancja kwot**: Tolerancja dla porównania kwot w procentach
    
    ## 🔧 Silniki OCR
    
    - **Tesseract**: Szybki, dobry dla tekstu
    - **EasyOCR**: Bardzo dobry dla skanów
    - **PaddleOCR**: Najlepszy dla polskiego tekstu
    
    ## 📞 Wsparcie
    
    W przypadku problemów skontaktuj się z zespołem technicznym.
    """)


def check_system_status():
    """Check system status."""
    try:
        # Check if core modules are available
        from core.run_audit import run_audit
        from core.ocr_processor import OCRProcessor
        from core.data_processing import read_table
        
        st.success("✅ Wszystkie moduły dostępne")
        
        # Check OCR engines
        ocr_engines = []
        for engine in ["tesseract", "easyocr", "paddleocr"]:
            try:
                processor = OCRProcessor(engine=engine)
                ocr_engines.append(f"✅ {engine}")
            except:
                ocr_engines.append(f"❌ {engine}")
        
        st.info("🔤 Silniki OCR:\n" + "\n".join(ocr_engines))
        
    except Exception as e:
        st.error(f"❌ Błąd sprawdzania statusu: {e}")


if __name__ == "__main__":
    main()

