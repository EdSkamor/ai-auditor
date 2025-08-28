import streamlit as st
def back(label="← Wróć", target="Home.py"):
    if isinstance(target, str) and target.startswith("app/"):
        target = target.split("/", 1)[1]
    st.page_link(target, label=label, icon="⬅️")
