import streamlit as st
 
st.set_page_config(
    page_title="Gold Tables Dashboard",
    layout="wide",
)

metrics_page = st.Page("pages/metrics.py", title="Metrics")
chat_page = st.Page("pages/chat.py", title="Chat")

pg = st.navigation([metrics_page, chat_page])
pg.run()
