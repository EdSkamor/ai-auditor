"""
Analiza POP - Strona analizy dokumentów księgowych
"""

from datetime import datetime

import pandas as pd
import streamlit as st

from app.ui_utils import (
    apply_modern_css,
    render_navigation,
    render_page_header,
)


def render_analysis_page():
    """Render analysis page."""
    render_page_header("Analiza Dokumentów Księgowych", "📊")

    # File upload section
    st.markdown("### 📁 Wgraj pliki do analizy")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_files = st.file_uploader(
            "Wybierz pliki do analizy",
            type=["pdf", "zip", "csv", "xlsx", "xml"],
            accept_multiple_files=True,
            help="Obsługiwane formaty: PDF, ZIP, CSV, Excel, XML",
        )

    with col2:
        if st.button("🚀 Uruchom Analizę", type="primary", use_container_width=True):
            if uploaded_files:
                run_analysis(uploaded_files)
            else:
                st.warning("Wybierz pliki do analizy")

    # Analysis settings
    st.markdown("### ⚙️ Ustawienia Analizy")

    col1, col2, col3 = st.columns(3)

    with col1:
        analysis_type = st.selectbox(
            "Typ analizy:",
            ["Kompleksowa", "Faktury", "Kontrahenci", "Płatności", "Zgodność"],
        )

        analysis_depth = st.selectbox(
            "Głębokość analizy:", ["Podstawowa", "Szczegółowa", "Głęboka"]
        )

    with col2:
        include_ai = st.checkbox("Użyj AI do analizy", value=True)

        include_risk = st.checkbox("Analiza ryzyka", value=True)

        include_compliance = st.checkbox("Sprawdzenie zgodności", value=True)

    with col3:
        output_format = st.selectbox(
            "Format wyniku:", ["Excel", "PDF", "JSON", "Wszystkie"]
        )

        include_charts = st.checkbox("Włącz wykresy", value=True)

    # Analysis results
    if "analysis_results" in st.session_state:
        render_analysis_results()

    # Analysis history
    if "analysis_history" in st.session_state and st.session_state.analysis_history:
        render_analysis_history()


def run_analysis(uploaded_files):
    """Run analysis on uploaded files."""
    with st.spinner("Analizuję pliki..."):
        # Simulate analysis progress
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i in range(100):
            progress_bar.progress(i + 1)
            if i < 30:
                status_text.text("Wczytywanie plików...")
            elif i < 60:
                status_text.text("Przetwarzanie danych...")
            elif i < 90:
                status_text.text("Analiza AI...")
            else:
                status_text.text("Generowanie raportu...")

        # Generate mock results
        results = generate_mock_results(uploaded_files)
        st.session_state.analysis_results = results

        # Add to history
        if "analysis_history" not in st.session_state:
            st.session_state.analysis_history = []

        st.session_state.analysis_history.append(
            {
                "timestamp": datetime.now(),
                "files": [f.name for f in uploaded_files],
                "results": results,
            }
        )

        progress_bar.empty()
        status_text.empty()
        st.success("✅ Analiza zakończona pomyślnie!")


def generate_mock_results(uploaded_files):
    """Generate mock analysis results."""
    return {
        "total_files": len(uploaded_files),
        "findings": [
            {
                "id": "F001",
                "type": "Duplikat faktury",
                "severity": "high",
                "description": "Znaleziono duplikat faktury FV/2024/001",
                "file": uploaded_files[0].name if uploaded_files else "unknown.pdf",
                "confidence": 0.95,
            },
            {
                "id": "F002",
                "type": "Brakujący NIP",
                "severity": "medium",
                "description": "Brakuje NIP dla kontrahenta ABC Corp",
                "file": uploaded_files[0].name if uploaded_files else "unknown.pdf",
                "confidence": 0.87,
            },
            {
                "id": "F003",
                "type": "Podejrzana transakcja",
                "severity": "low",
                "description": "Transakcja w weekend o dużej kwocie",
                "file": uploaded_files[0].name if uploaded_files else "unknown.pdf",
                "confidence": 0.72,
            },
        ],
        "summary": {
            "total_findings": 3,
            "high_risk": 1,
            "medium_risk": 1,
            "low_risk": 1,
            "files_processed": len(uploaded_files),
        },
    }


def render_analysis_results():
    """Render analysis results."""
    st.markdown("### 📊 Wyniki Analizy")

    results = st.session_state.analysis_results
    summary = results["summary"]

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Pliki", summary["files_processed"])

    with col2:
        st.metric("Znalezione", summary["total_findings"])

    with col3:
        st.metric("Wysokie ryzyko", summary["high_risk"])

    with col4:
        st.metric("Średnie ryzyko", summary["medium_risk"])

    # Findings list
    st.markdown("### 🔍 Znalezione Niezgodności")

    for finding in results["findings"]:
        severity_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}

        with st.expander(
            f"{severity_color[finding['severity']]} {finding['type']} - {finding['id']}"
        ):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Opis:** {finding['description']}")
                st.write(f"**Plik:** {finding['file']}")
                st.write(f"**Pewność:** {finding['confidence']:.0%}")

            with col2:
                if st.button("👁️ Szczegóły", key=f"details_{finding['id']}"):
                    show_finding_details(finding)

                if st.button("📝 Komentarz", key=f"comment_{finding['id']}"):
                    add_finding_comment(finding)

    # Download options
    st.markdown("### 📥 Pobierz Wyniki")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📊 Excel", use_container_width=True):
            download_excel_results(results)

    with col2:
        if st.button("📄 PDF", use_container_width=True):
            download_pdf_results(results)

    with col3:
        if st.button("📋 JSON", use_container_width=True):
            download_json_results(results)

    with col4:
        if st.button("📦 ZIP", use_container_width=True):
            download_zip_results(results)


def show_finding_details(finding):
    """Show detailed information about a finding."""
    st.info(f"Szczegóły dla {finding['id']}: {finding['description']}")


def add_finding_comment(finding):
    """Add comment to a finding."""
    comment = st.text_input(f"Komentarz dla {finding['id']}:")
    if comment:
        st.success(f"Komentarz dodany: {comment}")


def download_excel_results(results):
    """Download results as Excel."""
    st.success("📊 Pobieranie Excel...")
    # Mock download
    df = pd.DataFrame(results["findings"])
    csv = df.to_csv(index=False)
    st.download_button(
        label="💾 Pobierz Excel",
        data=csv,
        file_name=f"analiza_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )


def download_pdf_results(results):
    """Download results as PDF."""
    st.success("📄 Pobieranie PDF...")


def download_json_results(results):
    """Download results as JSON."""
    st.success("📋 Pobieranie JSON...")
    import json

    json_str = json.dumps(results, indent=2, ensure_ascii=False)
    st.download_button(
        label="💾 Pobierz JSON",
        data=json_str,
        file_name=f"analiza_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
    )


def download_zip_results(results):
    """Download results as ZIP."""
    st.success("📦 Pobieranie ZIP...")


def render_analysis_history():
    """Render analysis history."""
    st.markdown("### 📚 Historia Analiz")

    history = st.session_state.analysis_history

    for i, analysis in enumerate(reversed(history[-5:])):  # Show last 5
        with st.expander(
            f"Analiza {i+1} - {analysis['timestamp'].strftime('%Y-%m-%d %H:%M')}"
        ):
            st.write(f"**Pliki:** {', '.join(analysis['files'])}")
            st.write(
                f"**Znalezione:** {analysis['results']['summary']['total_findings']}"
            )

            if st.button("🔄 Powtórz", key=f"repeat_{i}"):
                st.info("Analiza zostanie powtórzona...")


def main():
    """Main function for Analysis page."""
    apply_modern_css()
    render_navigation()
    render_analysis_page()


if __name__ == "__main__":
    main()
