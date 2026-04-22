import streamlit as st

st.title("Databricks Streamlit App")
st.write("Welcome to your simple Databricks Streamlit app!")

data = {"Name": ["Alice", "Bob", "Charlie"], "Score": [85, 92, 78]}
st.table(data)