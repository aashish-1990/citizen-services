import streamlit as st
import uuid
import time

st.set_page_config(page_title="LIA – City Assistant", layout="centered")
st.image("https://cdn-icons-png.flaticon.com/512/4712/4712107.png", width=80)
st.title("🤖 Meet LIA – Your City of Kermit Assistant")

# Initialize state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat" not in st.session_state:
    st.session_state.chat = []
if "step" not in st.session_state:
    st.session_state.step = 0
if "intent" not in st.session_state:
    st.session_state.intent = None
if "context" not in st.session_state:
    st.session_state.context = {}

# Utility: Add chat messages
def lia_say(text):
    st.session_state.chat.append(("LIA", text))

def user_say(text):
    st.session_state.chat.append(("User", text))

# Render chat
for speaker, message in st.session_state.chat:
    if speaker == "LIA":
        st.markdown(f"🟣 **LIA**: {message}")
    else:
        st.markdown(f"🟢 **You**: {message}")

# Step 0 – Greet and wait for user message
if st.session_state.step == 0:
    if not st.session_state.chat:
        lia_say("Hi there! I’m LIA — your City of Kermit Assistant. How can I help you today?\n\nYou can say things like:\n- I want to pay my bill\n- I want to apply for a permit\n- I have a ticket to pay\n- I want to report a water leak")

    user_input = st.chat_input("Type your request...")
    if user_input:
        user_say(user_input)
        text = user_input.lower()
        if "bill" in text:
            st.session_state.intent = "pay_bill"
            st.session_state.step = 1
            lia_say("Sure! Please enter your address to look up your bill.")
        elif "ticket" in text:
            st.session_state.intent = "pay_ticket"
            st.session_state.step = 100
            lia_say("Ticket flow coming soon.")
        else:
            lia_say("I didn’t quite catch that. You can ask me to pay a bill, pay a ticket, apply for a permit, or report an issue.")

# Step 1 – Pay Bill: Ask for Address
elif st.session_state.step == 1:
    user_input = st.chat_input("Your address...")
    if user_input:
        user_say(user_input)
        st.session_state.context["address"] = user_input
        # Simulate address match and show bill
        lia_say(f"Found a bill for **$82.35** at *{user_input}*.\nIs this correct?")
        st.session_state.step = 2

# Step 2 – Confirm Bill Details
elif st.session_state.step == 2:
    user_input = st.chat_input("Is the bill correct? (Yes/No)")
    if user_input:
        user_say(user_input)
        if "yes" in user_input.lower():
            lia_say("Great! Please check your SMS and email for the payment link. Once you've completed the payment, let me know.")
            st.session_state.step = 3
        else:
            lia_say("Okay, let’s try again. Please re-enter your address.")
            st.session_state.step = 1

# Step 3 – Simulate Payment Status
elif st.session_state.step == 3:
    user_input = st.chat_input("Type 'done' once you’ve paid.")
    if user_input:
        user_say(user_input)
        if "done" in user_input.lower():
            with st.spinner("Verifying payment with city systems..."):
                time.sleep(2)
            lia_say("✅ Your payment has been successfully received.")
            st.session_state.step = 4
        else:
            lia_say("No worries — take your time. Let me know when done.")

# Step 4 – Receipt + Restart Options
elif st.session_state.step == 4:
    lia_say("Would you like to download your receipt or do something else?")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🧾 Download Receipt"):
            lia_say("Receipt downloaded (demo).")
    with col2:
        if st.button("💧 Pay Another Bill"):
            st.session_state.step = 1
            lia_say("Sure! Please enter the next address.")
    with col3:
        if st.button("🏠 Main Menu"):
            st.session_state.clear()
