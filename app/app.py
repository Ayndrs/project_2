import streamlit as st

metrics_page = st.Page("pages/metrics.py", title="Metrics")
chat_page = st.Page("pages/chat.py", title="Chat")

pg = st.navigation([metrics_page, chat_page])
pg.run()
