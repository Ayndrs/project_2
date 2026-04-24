import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Business Assistant", page_icon="💬")
st.title("Internal Business Assistant")
st.caption("Look up orders, score customers, check policy, and find product info.")

# Initialize agent once per session
if "executor" not in st.session_state:
    with st.spinner("Loading agent..."):
        from agent.executor import build_executor
        st.session_state.executor = build_executor()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Handle new input
if prompt := st.chat_input("Ask about an order, policy, or product..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.executor.invoke({"input": prompt})
                output = response["output"]

                # Risk alert banner for high tier scores
                if "high" in output.lower() and "tier" in output.lower():
                    st.warning("⚠️ High value customer — consider priority follow-up")

                st.write(output)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": output
                })

            except Exception as e:
                error_msg = f"Something went wrong: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })