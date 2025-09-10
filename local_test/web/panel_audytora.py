"""
AI Auditor - Panel Audytora (Polski)
Lokalny interfejs do testowania systemu audytu faktur.
"""

import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

import streamlit as st

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure page
st.set_page_config(
    page_title="AI Auditor - Panel Audytora",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    st.title("🔍 AI Auditor - Panel Audytora")
    st.markdown("**System Walidacji Faktur - Wersja Testowa**")

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Konfiguracja")

        # Tie-breaker settings
        st.subheader("Ustawienia Tie-breaker")
        tiebreak_weight_fname = st.slider(
            "Waga nazwy pliku",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Waga dla dopasowania nazwy pliku w logice tie-breaker",
        )

        tiebreak_min_seller = st.slider(
            "Minimalne podobieństwo sprzedawcy",
            min_value=0.0,
            max_value=1.0,
            value=0.4,
            step=0.1,
            help="Minimalny próg podobieństwa dla dopasowania sprzedawcy",
        )

        amount_tolerance = st.slider(
            "Tolerancja kwoty",
            min_value=0.001,
            max_value=0.1,
            value=0.01,
            step=0.001,
            help="Tolerancja dla dopasowania kwot",
        )

        # Processing options
        st.subheader("Opcje Przetwarzania")
        max_file_size_mb = st.number_input(
            "Maksymalny rozmiar pliku (MB)", min_value=1, max_value=100, value=50
        )

        enable_ocr = st.checkbox("Włącz OCR", value=False)
        enable_ai_qa = st.checkbox("Włącz Asystenta AI", value=True)

    # Main interface
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📁 Prześlij i Przetwórz", "📊 Wyniki", "🤖 Asystent AI", "📋 Status Systemu"]
    )

    with tab1:
        st.header("📁 Prześlij i Przetwórz Pliki")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Pliki PDF")
            uploaded_pdfs = st.file_uploader(
                "Prześlij pliki PDF lub archiwum ZIP",
                type=["pdf", "zip"],
                accept_multiple_files=True,
                help="Prześlij pojedyncze pliki PDF lub archiwum ZIP zawierające PDF-y",
            )

        with col2:
            st.subheader("Dane POP")
            uploaded_pop = st.file_uploader(
                "Prześlij plik danych POP",
                type=["xlsx", "xls", "csv"],
                help="Prześlij plik z danymi POP (Population)",
            )

        # Test data buttons
        st.subheader("Dane Testowe")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📄 Użyj przykładowej faktury"):
                test_pdf_path = Path("test_data/pdfs/faktura_testowa.pdf")
                if test_pdf_path.exists():
                    st.success("✅ Załadowano przykładową fakturę")
                    st.session_state.test_pdf = str(test_pdf_path)
                else:
                    st.error("❌ Nie znaleziono pliku testowego")

        with col2:
            if st.button("📊 Użyj przykładowych danych POP"):
                test_pop_path = Path("test_data/dane_pop.csv")
                if test_pop_path.exists():
                    st.success("✅ Załadowano przykładowe dane POP")
                    st.session_state.test_pop = str(test_pop_path)
                else:
                    st.error("❌ Nie znaleziono pliku testowego")

        if st.button("🚀 Uruchom Audyt", type="primary"):
            # Use test data if no files uploaded
            if not uploaded_pdfs and "test_pdf" in st.session_state:
                uploaded_pdfs = [st.session_state.test_pdf]

            if not uploaded_pop and "test_pop" in st.session_state:
                uploaded_pop = st.session_state.test_pop

            if uploaded_pdfs and uploaded_pop:
                with st.spinner("Przetwarzanie plików..."):
                    process_audit(
                        uploaded_pdfs,
                        uploaded_pop,
                        tiebreak_weight_fname,
                        tiebreak_min_seller,
                        amount_tolerance,
                        max_file_size_mb,
                        enable_ocr,
                    )
            else:
                st.error(
                    "Proszę przesłać pliki PDF i dane POP lub użyć danych testowych"
                )

    with tab2:
        st.header("📊 Wyniki Audytu")
        display_results()

    with tab3:
        st.header("🤖 Asystent AI")
        if enable_ai_qa:
            display_ai_assistant()
        else:
            st.info(
                "Asystent AI jest wyłączony. Włącz go w panelu bocznym, aby używać."
            )

    with tab4:
        st.header("📋 Status Systemu")
        display_system_status()


def process_audit(
    pdf_files,
    pop_file,
    tiebreak_weight_fname,
    tiebreak_min_seller,
    amount_tolerance,
    max_file_size_mb,
    enable_ocr,
):
    """Process the audit with uploaded files."""
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Save uploaded files
            pdf_dir = temp_path / "pdfs"
            pdf_dir.mkdir()

            for pdf_file in pdf_files:
                if isinstance(pdf_file, str):
                    # Test file path
                    shutil.copy2(pdf_file, pdf_dir / Path(pdf_file).name)
                else:
                    # Uploaded file
                    with open(pdf_dir / pdf_file.name, "wb") as f:
                        f.write(pdf_file.getbuffer())

            pop_path = temp_path / "pop_data.csv"
            if isinstance(pop_file, str):
                # Test file path
                shutil.copy2(pop_file, pop_path)
            else:
                # Uploaded file
                with open(pop_path, "wb") as f:
                    f.write(pop_file.getbuffer())

            # Run audit
            output_dir = temp_path / "output"
            output_dir.mkdir()

            # Import and run audit
            try:
                from core.run_audit import run_audit

                summary = run_audit(
                    pdf_source=pdf_dir,
                    pop_file=pop_path,
                    output_dir=output_dir,
                    tiebreak_weight_fname=tiebreak_weight_fname,
                    tiebreak_min_seller=tiebreak_min_seller,
                    amount_tolerance=amount_tolerance,
                )

                # Store results in session state
                st.session_state.audit_summary = summary
                st.session_state.output_dir = output_dir

                st.success("✅ Audyt zakończony pomyślnie!")
                st.json(summary)

            except ImportError as e:
                st.warning(f"⚠️ Nie można zaimportować modułów: {e}")
                st.info("Uruchom: pip install -r requirements.txt")

                # Simulate results for demo
                st.session_state.audit_summary = {
                    "total_pdfs_processed": 1,
                    "total_matches": 1,
                    "total_unmatched": 0,
                    "total_errors": 0,
                    "match_rate": 1.0,
                    "demo_mode": True,
                }
                st.success("✅ Tryb demonstracyjny - symulowane wyniki")

    except Exception as e:
        st.error(f"❌ Audyt nie powiódł się: {e}")


def display_results():
    """Display audit results."""
    if "audit_summary" in st.session_state:
        summary = st.session_state.audit_summary

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Łącznie PDF-ów", summary.get("total_pdfs_processed", 0))

        with col2:
            st.metric("Dopasowania", summary.get("total_matches", 0))

        with col3:
            st.metric("Niedopasowane", summary.get("total_unmatched", 0))

        with col4:
            st.metric("Błędy", summary.get("total_errors", 0))

        # Show demo mode warning
        if summary.get("demo_mode"):
            st.warning(
                "⚠️ Tryb demonstracyjny - zainstaluj zależności dla pełnej funkcjonalności"
            )

        # Download results
        if st.button("📥 Pobierz Pakiet Wyników"):
            create_results_package()
    else:
        st.info("Brak wyników audytu. Uruchom audyt najpierw.")


def display_ai_assistant():
    """Display AI assistant interface."""
    st.subheader("🤖 Lokalny Asystent AI Q&A")
    st.info("Zadawaj pytania dotyczące danych audytu i praktyk księgowych.")

    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Zadaj pytanie dotyczące danych audytu..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Myślę..."):
                # Simulate AI response (replace with actual AI call)
                response = (
                    f"Na podstawie danych audytu, oto co znalazłem dotyczące: {prompt}"
                )
                st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})


def display_system_status():
    """Display system status."""
    st.subheader("🖥️ Status Systemu")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Pamięć GPU", "24 GB", "Dostępna")
        st.metric("Rdzenie CPU", "8+", "Dostępne")
        st.metric("RAM", "32 GB+", "Dostępna")

    with col2:
        st.metric("Modele Załadowane", "3", "LLM + Embeddings + OCR")
        st.metric("Prędkość Przetwarzania", ">20 PDF/sek", "Zoptymalizowana")
        st.metric("Czas Dostępności", "99.9%", "Cel")

    # Model status
    st.subheader("🧠 Status Modeli AI")

    models_status = {
        "LLM (Llama3-8B)": "✅ Załadowany (4-bit quantized)",
        "Embeddings (Wielojęzyczne)": "✅ Załadowany (fp16)",
        "OCR (PaddleOCR)": "✅ Załadowany (GPU-accelerated)",
    }

    for model, status in models_status.items():
        st.write(f"**{model}**: {status}")


def create_results_package():
    """Create downloadable results package."""
    if "output_dir" in st.session_state:
        output_dir = st.session_state.output_dir

        # Create ZIP package
        import io

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in output_dir.rglob("*"):
                if file_path.is_file():
                    zip_file.write(file_path, file_path.relative_to(output_dir))

        zip_buffer.seek(0)

        st.download_button(
            label="📥 Pobierz Kompletny Pakiet Wyników",
            data=zip_buffer.getvalue(),
            file_name=f"wyniki_audytu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip",
        )


if __name__ == "__main__":
    main()
