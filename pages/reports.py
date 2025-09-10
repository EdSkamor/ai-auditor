"""
Raporty - Strona generowania i zarządzania raportami
"""

from datetime import datetime, timedelta

import streamlit as st

from app.ui_utils import apply_modern_css, render_navigation, render_page_header


def render_reports_page():
    """Render reports page."""
    render_page_header("Generowanie Raportów", "📋")

    # Report types
    st.markdown("### 📊 Typy Raportów")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 PBC", "📁 Working Papers", "📈 Raporty", "📦 Evidence ZIP"]
    )

    with tab1:
        render_pbc_reports()

    with tab2:
        render_working_papers()

    with tab3:
        render_final_reports()

    with tab4:
        render_evidence_zip()

    # Report history
    if "report_history" in st.session_state and st.session_state.report_history:
        render_report_history()


def render_pbc_reports():
    """Render PBC (Prepared by Client) reports."""
    st.markdown("#### 📋 PBC (Prepared by Client)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Lista PBC**")
        st.write("Lista dokumentów, które klient musi przygotować")

        if st.button("📅 Generuj Listę PBC", use_container_width=True):
            generate_pbc_list()

        st.markdown("**Status PBC**")
        st.write("Status dostarczonych dokumentów")

        if st.button("📊 Generuj Status PBC", use_container_width=True):
            generate_pbc_status()

    with col2:
        st.markdown("**Timeline PBC**")
        st.write("Harmonogram dostaw dokumentów")

        if st.button("📈 Generuj Timeline PBC", use_container_width=True):
            generate_pbc_timeline()

        # PBC Settings
        st.markdown("**Ustawienia PBC**")
        pbc_deadline = st.date_input(
            "Termin dostawy PBC", value=datetime.now() + timedelta(days=30)
        )
        pbc_priority = st.selectbox(
            "Priorytet", ["Niski", "Średni", "Wysoki", "Krytyczny"]
        )


def render_working_papers():
    """Render Working Papers reports."""
    st.markdown("#### 📁 Working Papers")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Working Papers**")
        st.write("Dokumenty robocze audytu")

        if st.button("📁 Generuj Working Papers", use_container_width=True):
            generate_working_papers()

        st.markdown("**Łańcuch Dowodowy**")
        st.write("Dowody na każdy wniosek audytowy")

        if st.button("🔗 Generuj Łańcuch Dowodowy", use_container_width=True):
            generate_evidence_chain()

    with col2:
        st.markdown("**Statystyki WP**")
        st.write("Podsumowanie dokumentów roboczych")

        if st.button("📊 Generuj Statystyki WP", use_container_width=True):
            generate_wp_statistics()

        # WP Settings
        st.markdown("**Ustawienia WP**")
        wp_format = st.selectbox("Format WP", ["Excel", "PDF", "Word"])
        include_formulas = st.checkbox("Uwzględnij formuły", value=True)


def render_final_reports():
    """Render final reports."""
    st.markdown("#### 📈 Raporty Końcowe")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Raport Końcowy**")
        st.write("Główny raport audytu")

        if st.button("📄 Generuj Raport Końcowy", use_container_width=True):
            generate_final_report()

        st.markdown("**Executive Summary**")
        st.write("Podsumowanie dla zarządu")

        if st.button("📋 Generuj Executive Summary", use_container_width=True):
            generate_executive_summary()

    with col2:
        st.markdown("**Compliance Report**")
        st.write("Raport zgodności z przepisami")

        if st.button("📊 Generuj Compliance Report", use_container_width=True):
            generate_compliance_report()

        # Report Settings
        st.markdown("**Ustawienia Raportu**")
        report_language = st.selectbox("Język raportu", ["Polski", "English"])
        include_charts = st.checkbox("Uwzględnij wykresy", value=True)
        include_recommendations = st.checkbox("Uwzględnij rekomendacje", value=True)


def render_evidence_zip():
    """Render Evidence ZIP section."""
    st.markdown("#### 📦 Evidence ZIP")

    st.info("📦 **Evidence ZIP** - Kompletny pakiet dowodów audytowych")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Zawartość ZIP:**")
        st.write("• report.xlsx - Raport w Excel")
        st.write("• findings.json - Znalezione niezgodności")
        st.write("• decision_log.csv - Log decyzji audytowych")
        st.write("• manifest.json - Manifest z hashami")
        st.write("• audit_trail.txt - Ślad audytowy")
        st.write("• summary.txt - Podsumowanie wykonawcze")

    with col2:
        st.markdown("**Ustawienia ZIP:**")
        include_pii = st.checkbox("Uwzględnij PII", value=False)
        encrypt_zip = st.checkbox("Zaszyfruj ZIP", value=False)
        compression_level = st.slider("Poziom kompresji", 1, 9, 6)

        if st.button(
            "📦 Generuj Evidence ZIP", type="primary", use_container_width=True
        ):
            generate_evidence_zip(include_pii, encrypt_zip, compression_level)


def generate_pbc_list():
    """Generate PBC list."""
    with st.spinner("Generuję listę PBC..."):
        # Mock generation
        st.success("✅ Lista PBC wygenerowana!")
        add_to_history("Lista PBC", "PBC")


def generate_pbc_status():
    """Generate PBC status."""
    with st.spinner("Generuję status PBC..."):
        st.success("✅ Status PBC wygenerowany!")
        add_to_history("Status PBC", "PBC")


def generate_pbc_timeline():
    """Generate PBC timeline."""
    with st.spinner("Generuję timeline PBC..."):
        st.success("✅ Timeline PBC wygenerowany!")
        add_to_history("Timeline PBC", "PBC")


def generate_working_papers():
    """Generate Working Papers."""
    with st.spinner("Generuję Working Papers..."):
        st.success("✅ Working Papers wygenerowane!")
        add_to_history("Working Papers", "WP")


def generate_evidence_chain():
    """Generate evidence chain."""
    with st.spinner("Generuję łańcuch dowodowy..."):
        st.success("✅ Łańcuch dowodowy wygenerowany!")
        add_to_history("Łańcuch Dowodowy", "WP")


def generate_wp_statistics():
    """Generate WP statistics."""
    with st.spinner("Generuję statystyki WP..."):
        st.success("✅ Statystyki WP wygenerowane!")
        add_to_history("Statystyki WP", "WP")


def generate_final_report():
    """Generate final report."""
    with st.spinner("Generuję raport końcowy..."):
        st.success("✅ Raport końcowy wygenerowany!")
        add_to_history("Raport Końcowy", "Report")


def generate_executive_summary():
    """Generate executive summary."""
    with st.spinner("Generuję Executive Summary..."):
        st.success("✅ Executive Summary wygenerowany!")
        add_to_history("Executive Summary", "Report")


def generate_compliance_report():
    """Generate compliance report."""
    with st.spinner("Generuję Compliance Report..."):
        st.success("✅ Compliance Report wygenerowany!")
        add_to_history("Compliance Report", "Report")


def generate_evidence_zip(include_pii=False, encrypt=False, compression=6):
    """Generate Evidence ZIP."""
    with st.spinner("Generuję Evidence ZIP..."):
        try:
            from core.evidence_zip import generate_evidence_zip

            # Prepare mock findings
            findings = [
                {
                    "id": f"F{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "type": "Audit Finding",
                    "severity": "medium",
                    "description": "Przykładowa niezgodność",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "status": "Open",
                    "details": "Szczegóły niezgodności...",
                }
            ]

            # Prepare analysis data
            analysis_data = {
                "user": "AI Auditor",
                "operation_type": "Evidence ZIP Generation",
                "file_name": "audit_evidence",
                "timestamp": datetime.now().isoformat(),
                "app_version": "1.0.0",
            }

            # Generate ZIP
            zip_path = generate_evidence_zip(findings, analysis_data)

            # Download button
            with open(zip_path, "rb") as f:
                zip_data = f.read()

            st.download_button(
                label="💾 Pobierz Evidence ZIP",
                data=zip_data,
                file_name=f"evidence_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
            )

            st.success("✅ Evidence ZIP wygenerowany!")
            add_to_history("Evidence ZIP", "ZIP")

        except ImportError as e:
            st.error(f"❌ Błąd importu Evidence ZIP: {e}")
        except Exception as e:
            st.error(f"❌ Błąd generowania Evidence ZIP: {e}")


def add_to_history(report_name, report_type):
    """Add report to history."""
    if "report_history" not in st.session_state:
        st.session_state.report_history = []

    st.session_state.report_history.append(
        {
            "name": report_name,
            "type": report_type,
            "timestamp": datetime.now(),
            "size": f"{len(report_name) * 0.1:.1f} MB",  # Mock size
        }
    )


def render_report_history():
    """Render report history."""
    st.markdown("### 📚 Historia Raportów")

    history = st.session_state.report_history

    # Summary
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Wszystkie raporty", len(history))

    with col2:
        pbc_count = len([r for r in history if r["type"] == "PBC"])
        st.metric("PBC", pbc_count)

    with col3:
        wp_count = len([r for r in history if r["type"] == "WP"])
        st.metric("Working Papers", wp_count)

    with col4:
        report_count = len([r for r in history if r["type"] == "Report"])
        st.metric("Raporty", report_count)

    # History list
    for i, report in enumerate(reversed(history[-10:])):  # Show last 10
        with st.expander(
            f"{report['name']} - {report['timestamp'].strftime('%Y-%m-%d %H:%M')}"
        ):
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.write(f"**Typ:** {report['type']}")
                st.write(f"**Rozmiar:** {report['size']}")

            with col2:
                if st.button("⬇️ Pobierz", key=f"download_{i}"):
                    st.info("Pobieranie rozpoczęte...")

            with col3:
                if st.button("🗑️ Usuń", key=f"delete_{i}"):
                    st.session_state.report_history.pop(len(history) - 1 - i)
                    st.rerun()


def main():
    """Main function for Reports page."""
    apply_modern_css()
    render_navigation()
    render_reports_page()


if __name__ == "__main__":
    main()
