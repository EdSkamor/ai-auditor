from __future__ import annotations
from typing import Mapping, Dict, Any, Iterable, Optional

# Streamlit jest opcjonalny – moduł działa także bez niego
try:
    import streamlit as st  # type: ignore
    _HAVE_ST = True
except Exception:
    _HAVE_ST = False

# Matplotlib w trybie headless
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _counts_from_values(values: Iterable[Any]) -> Dict[str, int]:
    """Zlicz wystąpienia; None/NaN traktuj jako pusty string."""
    out: Dict[str, int] = {}
    for v in values:
        k = "" if v is None else str(v)
        out[k] = out.get(k, 0) + 1
    return out


def donut_figure(counts: Mapping[str, int], title: str = "") -> plt.Figure:
    """Zwraca figurę Matplotlib z wykresem donut (kołowy z dziurą)."""
    labels = [str(k) for k in counts.keys()]
    vals = [int(v) for v in counts.values()]
    if not vals or sum(vals) <= 0:
        labels, vals = ["brak danych"], [1]

    fig = plt.figure(figsize=(4.5, 4.5), dpi=120)
    ax = fig.add_subplot(111)
    wedges, _texts = ax.pie(vals, wedgeprops=dict(width=0.35), startangle=90, normalize=True)
    total = sum(vals)
    autopcts = [f"{(v/total*100):.0f}%" if total else "0%" for v in vals]
    legend_labels = [f"{l} – {v} ({p})" for l, v, p in zip(labels, vals, autopcts)]
    ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0.5), frameon=False)
    centre_circle = plt.Circle((0, 0), 0.65, fc="white")
    ax.add_artist(centre_circle)
    ax.set(aspect="equal")
    if title:
        ax.set_title(title)
    fig.tight_layout()
    return fig


def donut_save_png(counts: Mapping[str, int], out_path: str, title: str = "") -> str:
    """Rysuje donut i zapisuje do PNG. Zwraca ścieżkę."""
    fig = donut_figure(counts, title=title)
    fig.savefig(out_path, format="png", bbox_inches="tight")
    plt.close(fig)
    return out_path


def st_donut_from_series(values: Iterable[Any], title: str = "Statusy") -> Optional[plt.Figure]:
    """
    Wersja pod Streamlit: przyjmuje sekwencję wartości (np. df['status']),
    rysuje donut i (jeśli Streamlit dostępny) osadza go w UI. Zwraca figurę.
    """
    counts = _counts_from_values(values)
    fig = donut_figure(counts, title=title)
    if _HAVE_ST:
        st.pyplot(fig, use_container_width=False)
    return fig


def _safe_rerun() -> None:
    if not _HAVE_ST:
        return
    try:
        st.rerun()
    except Exception:
        try:
            st.experimental_rerun()  # starsze wersje
        except Exception:
            pass


def st_reset_filters_button(keys_to_clear: Iterable[str], label: str = "🔄 Reset filtrów") -> bool:
    """
    Dodaje przycisk „Reset filtrów”, który czyści wskazane klucze w st.session_state
    i robi rerun. Zwraca True, jeżeli wykonał się reset.
    """
    if not _HAVE_ST:
        return False
    if st.button(label):
        for k in keys_to_clear:
            if k in st.session_state:
                del st.session_state[k]
        _safe_rerun()
        return True
    return False
