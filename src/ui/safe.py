"""
Safe UI execution with error handling
"""

import logging
import traceback

import streamlit as st

def safe_run(fn, *, section="main"):
    """
    Safely run a function with error handling.
    Shows user-friendly error messages and logs details.
    """
    try:
        return fn()
    except Exception as e:
        logging.exception("UI error in %s", section)
        st.error(f"Wystąpił nieoczekiwany błąd w sekcji: {section}")
        
        with st.expander("🔍 Pokaż szczegóły techniczne"):
            st.code("".join(traceback.format_exc()))
            
        # Return None to indicate failure
        return None
