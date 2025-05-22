# streamlit_chatbot.py
import streamlit as st
import requests
import uuid

st.set_page_config(page_title="LIA – Chat Assistant", layout="centered")
st.title("🤖 Talk to LIA")

# Initialize session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input box
user_input = st.text_input("You:", key="user_input")

if user_input:
    # Optional context mock
    context = {}
    if "olive" in user_input.lower():
        context["address"] = "123 Olive Street"
    elif "ticket" in user_input.lower():
        context["ticket_id"] = "123"
    elif "permit" in user_input.lower():
        context = {
            "permit_type": "garage sale",
            "location": "210 Ash Street"
        }

    # Send to FastAPI
    payload = {
        "user_input": user_input,
        "context": context,
        "session_id": st.session_state.session_id
    }

    try:
        response = requests.post("http://127.0.0.1:8000/chat", json=payload)
        data = response.json()
        reply = data["response"]

        st.session_state.chat_history.append(f"👤 You: {user_input}")
        st.session_state.chat_history.append(f"🤖 LIA: {reply}")

    except Exception as e:
        st.error(f"Failed to connect to LIA backend: {e}")

# Display chat history
for msg in st.session_state.chat_history:
    st.markdown(msg)
