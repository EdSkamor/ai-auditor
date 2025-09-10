"""
Diagnostyka - Strona diagnostyki systemu i połączeń
"""

import os
import time
from datetime import datetime

import psutil
import requests
import streamlit as st

from app.ui_utils import get_ai_status, render_page_header


def render_diagnostics_page():
    """Render diagnostics page."""
    render_page_header("Diagnostyka Systemu", "🔧")

    # System overview
    render_system_overview()

    # AI Connection diagnostics
    render_ai_diagnostics()

    # Performance metrics
    render_performance_metrics()

    # Network diagnostics
    render_network_diagnostics()

    # System logs
    render_system_logs()

    # Maintenance actions
    render_maintenance_actions()


def render_system_overview():
    """Render system overview."""
    st.markdown("### 🖥️ Przegląd Systemu")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # System uptime
        uptime = get_system_uptime()
        st.metric("Czas działania", uptime)

    with col2:
        # Memory usage
        memory = psutil.virtual_memory()
        st.metric(
            "Pamięć RAM",
            f"{memory.percent}%",
            f"{memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB",
        )

    with col3:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        st.metric("CPU", f"{cpu_percent}%")

    with col4:
        # Disk usage
        disk = psutil.disk_usage("/")
        st.metric(
            "Dysk",
            f"{disk.percent}%",
            f"{disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB",
        )


def render_ai_diagnostics():
    """Render AI connection diagnostics."""
    st.markdown("### 🤖 Diagnostyka AI")

    # AI Status
    ai_status = get_ai_status()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Status Połączenia")

        if ai_status["available"]:
            st.success(f"✅ AI Online ({ai_status['rtt_avg']:.1f}ms)")
        else:
            st.error("❌ AI Offline")

        st.write(f"**Serwer:** {ai_status['server_url']}")
        st.write(f"**Status Code:** {ai_status['status_code']}")

        # Connection test
        if st.button("🔄 Testuj Połączenie"):
            test_ai_connection()

    with col2:
        st.markdown("#### Szczegółowe Testy")

        # Health check
        if st.button("🏥 Health Check"):
            perform_health_check()

        # Ready check
        if st.button("⚡ Ready Check"):
            perform_ready_check()

        # Model test
        if st.button("🧠 Test Modelu"):
            test_ai_model()

    # RTT History
    if "rtt_history" not in st.session_state:
        st.session_state.rtt_history = []

    if ai_status["rtt_avg"]:
        st.session_state.rtt_history.append(
            {"timestamp": datetime.now(), "rtt": ai_status["rtt_avg"]}
        )

        # Keep only last 20 measurements
        if len(st.session_state.rtt_history) > 20:
            st.session_state.rtt_history = st.session_state.rtt_history[-20:]

    if st.session_state.rtt_history:
        render_rtt_chart()


def render_rtt_chart():
    """Render RTT chart."""
    st.markdown("#### 📊 Historia RTT")

    import pandas as pd
    import plotly.express as px

    df = pd.DataFrame(st.session_state.rtt_history)
    df["time"] = df["timestamp"].dt.strftime("%H:%M:%S")

    fig = px.line(df, x="time", y="rtt", title="RTT w czasie")
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


def render_performance_metrics():
    """Render performance metrics."""
    st.markdown("### 📊 Metryki Wydajności")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Procesy")

        # Top processes
        processes = []
        for proc in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_percent"]
        ):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Sort by CPU usage
        processes.sort(key=lambda x: x["cpu_percent"], reverse=True)

        for proc in processes[:5]:
            st.write(
                f"**{proc['name']}** - CPU: {proc['cpu_percent']:.1f}%, RAM: {proc['memory_percent']:.1f}%"
            )

    with col2:
        st.markdown("#### Sieć")

        # Network stats
        net_io = psutil.net_io_counters()
        st.write(f"**Wysłane:** {net_io.bytes_sent // (1024**2)} MB")
        st.write(f"**Odebrane:** {net_io.bytes_recv // (1024**2)} MB")
        st.write(f"**Pakiety wysłane:** {net_io.packets_sent}")
        st.write(f"**Pakiety odebrane:** {net_io.packets_recv}")


def render_network_diagnostics():
    """Render network diagnostics."""
    st.markdown("### 🌐 Diagnostyka Sieci")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Testy Połączenia")

        # Ping test
        if st.button("🏓 Test Ping"):
            test_ping()

        # DNS test
        if st.button("🌍 Test DNS"):
            test_dns()

        # Port test
        if st.button("🔌 Test Portów"):
            test_ports()

    with col2:
        st.markdown("#### Konfiguracja")

        # Environment variables
        st.write("**Zmienne środowiskowe:**")
        env_vars = ["AI_SERVER_URL", "AI_TIMEOUT", "STREAMLIT_SERVER_PORT"]
        for var in env_vars:
            value = os.getenv(var, "Nie ustawiona")
            st.write(f"• {var}: {value}")


def render_system_logs():
    """Render system logs."""
    st.markdown("### 📝 Logi Systemu")

    # Log level selector
    log_level = st.selectbox("Poziom logów:", ["DEBUG", "INFO", "WARNING", "ERROR"])

    # Mock logs
    logs = [
        {
            "timestamp": "2024-01-15 10:30:15",
            "level": "INFO",
            "message": "System uruchomiony",
        },
        {
            "timestamp": "2024-01-15 10:30:16",
            "level": "INFO",
            "message": "AI server połączony",
        },
        {
            "timestamp": "2024-01-15 10:31:20",
            "level": "WARNING",
            "message": "Wysokie użycie CPU",
        },
        {
            "timestamp": "2024-01-15 10:32:45",
            "level": "ERROR",
            "message": "Błąd połączenia z AI",
        },
        {
            "timestamp": "2024-01-15 10:33:10",
            "level": "INFO",
            "message": "Połączenie przywrócone",
        },
    ]

    # Filter logs by level
    filtered_logs = [
        log
        for log in logs
        if log["level"]
        in ["DEBUG", "INFO", "WARNING", "ERROR"][
            : ["DEBUG", "INFO", "WARNING", "ERROR"].index(log_level) + 1
        ]
    ]

    # Display logs
    for log in filtered_logs:
        level_color = {"DEBUG": "🔍", "INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "❌"}

        st.write(
            f"{level_color[log['level']]} **{log['timestamp']}** [{log['level']}] {log['message']}"
        )

    # Clear logs button
    if st.button("🗑️ Wyczyść Logi"):
        st.info("Logi wyczyszczone")


def render_maintenance_actions():
    """Render maintenance actions."""
    st.markdown("### 🔧 Akcje Konserwacyjne")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### System")

        if st.button("🔄 Restart Aplikacji", use_container_width=True):
            restart_application()

        if st.button("💾 Wyczyść Cache", use_container_width=True):
            clear_cache()

        if st.button("🗑️ Wyczyść Sesję", use_container_width=True):
            clear_session()

    with col2:
        st.markdown("#### AI")

        if st.button("🤖 Restart AI", use_container_width=True):
            restart_ai_server()

        if st.button("🧠 Reload Model", use_container_width=True):
            reload_ai_model()

        if st.button("📊 Reset Metryki", use_container_width=True):
            reset_metrics()

    with col3:
        st.markdown("#### Dane")

        if st.button("💾 Backup", use_container_width=True):
            create_backup()

        if st.button("🗂️ Archiwizuj", use_container_width=True):
            archive_data()

        if st.button("🔍 Sprawdź Integralność", use_container_width=True):
            check_integrity()


# Helper functions
def get_system_uptime():
    """Get system uptime."""
    uptime = time.time() - psutil.boot_time()
    days = int(uptime // 86400)
    hours = int((uptime % 86400) // 3600)
    minutes = int((uptime % 3600) // 60)
    return f"{days}d {hours}h {minutes}m"


def test_ai_connection():
    """Test AI connection."""
    with st.spinner("Testuję połączenie z AI..."):
        try:
            response = requests.get(
                "https://ai-auditor-romaks-8002.loca.lt/healthz", timeout=5
            )
            if response.ok:
                st.success("✅ Połączenie z AI działa poprawnie")
            else:
                st.error(f"❌ Błąd połączenia: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Błąd: {e}")


def perform_health_check():
    """Perform health check."""
    with st.spinner("Wykonuję health check..."):
        try:
            response = requests.get(
                "https://ai-auditor-romaks-8002.loca.lt/healthz", timeout=5
            )
            if response.ok:
                data = response.json()
                st.success("✅ Health check przeszedł pomyślnie")
                st.json(data)
            else:
                st.error(f"❌ Health check nie powiódł się: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Błąd health check: {e}")


def perform_ready_check():
    """Perform ready check."""
    with st.spinner("Wykonuję ready check..."):
        try:
            response = requests.get(
                "https://ai-auditor-romaks-8002.loca.lt/ready", timeout=5
            )
            if response.ok:
                data = response.json()
                st.success("✅ Ready check przeszedł pomyślnie")
                st.json(data)
            else:
                st.error(f"❌ Ready check nie powiódł się: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Błąd ready check: {e}")


def test_ai_model():
    """Test AI model."""
    with st.spinner("Testuję model AI..."):
        try:
            payload = {"prompt": "Test", "max_tokens": 10, "temperature": 0.1}
            response = requests.post(
                "https://ai-auditor-romaks-8002.loca.lt/analyze",
                json=payload,
                timeout=10,
            )
            if response.ok:
                st.success("✅ Model AI odpowiada poprawnie")
            else:
                st.error(f"❌ Model AI nie odpowiada: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Błąd testu modelu: {e}")


def test_ping():
    """Test ping."""
    st.info("🏓 Test ping - funkcja w trakcie implementacji")


def test_dns():
    """Test DNS."""
    st.info("🌍 Test DNS - funkcja w trakcie implementacji")


def test_ports():
    """Test ports."""
    st.info("🔌 Test portów - funkcja w trakcie implementacji")


def restart_application():
    """Restart application."""
    st.info("🔄 Restart aplikacji - funkcja w trakcie implementacji")


def clear_cache():
    """Clear cache."""
    st.cache_data.clear()
    st.success("✅ Cache wyczyszczony")


def clear_session():
    """Clear session."""
    st.session_state.clear()
    st.success("✅ Sesja wyczyszczona")
    st.rerun()


def restart_ai_server():
    """Restart AI server."""
    st.info("🤖 Restart AI server - funkcja w trakcie implementacji")


def reload_ai_model():
    """Reload AI model."""
    st.info("🧠 Reload model - funkcja w trakcie implementacji")


def reset_metrics():
    """Reset metrics."""
    if "rtt_history" in st.session_state:
        st.session_state.rtt_history = []
    st.success("✅ Metryki zresetowane")


def create_backup():
    """Create backup."""
    st.info("💾 Backup - funkcja w trakcie implementacji")


def archive_data():
    """Archive data."""
    st.info("🗂️ Archiwizacja - funkcja w trakcie implementacji")


def check_integrity():
    """Check integrity."""
    st.info("🔍 Sprawdzanie integralności - funkcja w trakcie implementacji")
