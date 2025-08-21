import streamlit as st

def back(label="← Wróć", target="Home.py"):
    # Akceptuj stare wywołania typu target='app/Home.py'
    if isinstance(target, str) and target.startswith("app/"):
        target = target.split("/", 1)[1]
    cols = st.columns([1,6,1])
    with cols[0]:
        st.page_link(target, label=label, icon="⬅️")
