from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import sys
import json
import re

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

def clean_output(text: str) -> str:
    """Remove undefined and stray markdown artifacts from agent output."""
    text = text.replace("undefined", "").strip()
    text = re.sub(r'```+', '', text).strip()
    return text

def display_score_result(output: str):
    """Check if output contains scoring data and display it cleanly."""
    try:
        # Try to find JSON in the output
        json_match = re.search(r'\{.*?\}', output, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            if "predicted_ltv" in data or "risk_tier" in data:
                # Display structured score card
                st.subheader("Customer Score")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Predicted LTV", f"${data.get('predicted_ltv', 'N/A')}")
                with col2:
                    tier = data.get('risk_tier', 'unknown')
                    st.metric("Risk Tier", tier.upper())
                with col3:
                    st.metric("Order ID", data.get('order_id', 'N/A'))

                # Risk alert banner
                if tier == "high":
                    st.success("✅ High value customer — consider priority follow-up")
                elif tier == "medium":
                    st.info("ℹ️ Medium value customer — standard handling")
                else:
                    st.warning("⚠️ Low value customer — monitor for churn risk")

                if data.get('explanation'):
                    st.write(data['explanation'])

                return True
    except Exception:
        pass
    return False

# Handle new input
if prompt := st.chat_input("Ask about an order, policy, or product..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.executor.invoke({"input": prompt})
                output = clean_output(response["output"])

                # Try to display as structured score card first
                displayed_as_card = display_score_result(output)

                # If not a score card just display as text
                if not displayed_as_card:
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