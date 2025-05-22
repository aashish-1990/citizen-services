import streamlit as st
import uuid

st.set_page_config(page_title="LIA – City Assistant", layout="centered")

# --- Init Session State ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "intent" not in st.session_state:
    st.session_state.intent = None
if "step" not in st.session_state:
    st.session_state.step = 0
if "context" not in st.session_state:
    st.session_state.context = {}

# --- Utility Functions ---
def add_message(sender, text):
    icon = "🟣" if sender == "LIA" else "🟢"
    st.session_state.messages.append(f"{icon} **{sender}**: {text}")

def reset_convo():
    st.session_state.messages = []
    st.session_state.intent = None
    st.session_state.step = 0
    st.session_state.context = {}

def simulate_bill_lookup(address):
    if "olive" in address.lower():
        return f"✅ Found bill for **{address}**. Amount due: **$82.35**"
    return f"❌ No bill found for {address}"

def simulate_payment():
    return "✅ Payment successful! Receipt sent via SMS and email."

# --- Initial Greeting ---
if st.session_state.step == 0 and not st.session_state.messages:
    add_message("LIA", "Hi there! I’m LIA — your City of Kermit Assistant. How can I help you today?")
    add_message("LIA", "You can say things like:\n\n- I want to pay my bill\n- I want to apply for a permit\n- I have a ticket to pay\n- I want to report a water leak")

# --- Chat Interface ---
st.title("🤖 Meet LIA – Your City of Kermit Assistant")
for msg in st.session_state.messages:
    st.markdown(msg, unsafe_allow_html=True)

user_input = st.chat_input("Type your request...")

if user_input:
    add_message("You", user_input)
    user_text = user_input.lower()

    if st.session_state.step == 0:
        if "bill" in user_text:
            st.session_state.intent = "pay_bill"
            st.session_state.step = 1
            add_message("LIA", "Great! Please enter your address to locate your bill.")
        elif "ticket" in user_text:
            st.session_state.intent = "pay_ticket"
            st.session_state.step = 1
            add_message("LIA", "Sure, what’s your ticket or plate number?")
        elif "permit" in user_text:
            st.session_state.intent = "apply_permit"
            st.session_state.step = 1
            add_message("LIA", "What type of permit do you want to apply for?")
        elif "report" in user_text or "issue" in user_text:
            st.session_state.intent = "report_issue"
            st.session_state.step = 1
            add_message("LIA", "Please describe the issue and its location.")
        else:
            add_message("LIA", "I didn’t quite catch that. You can ask me to pay a bill, pay a ticket, apply for a permit, or report an issue.")

    elif st.session_state.step == 1:
        if st.session_state.intent == "pay_bill":
            st.session_state.context["address"] = user_input
            lookup_msg = simulate_bill_lookup(user_input)
            add_message("LIA", lookup_msg)
            if "No bill" not in lookup_msg:
                st.session_state.step = 2
                add_message("LIA", "Would you like to proceed with payment? (yes/no)")

        elif st.session_state.intent == "pay_ticket":
            add_message("LIA", f"✅ Ticket {user_input} found. Fine: $45.00")
            st.session_state.step = 2
            add_message("LIA", "Would you like to pay it now? (yes/no)")

        elif st.session_state.intent == "apply_permit":
            st.session_state.context["permit_type"] = user_input
            st.session_state.step = 2
            add_message("LIA", "Please provide the address for this permit.")

        elif st.session_state.intent == "report_issue":
            add_message("LIA", f"✅ Thank you! The issue has been logged: '{user_input}'")
            st.session_state.step = 3
            add_message("LIA", "Would you like to report another issue or do something else?")

    elif st.session_state.step == 2:
        if st.session_state.intent == "pay_bill" or st.session_state.intent == "pay_ticket":
            if "yes" in user_text.lower():
                add_message("LIA", "📩 Sending payment link to your phone and email...")
                add_message("LIA", simulate_payment())
                st.session_state.step = 3
                add_message("LIA", "Would you like to do anything else?")
            else:
                add_message("LIA", "No problem. Let me know if you need help with anything else.")
                st.session_state.step = 3

        elif st.session_state.intent == "apply_permit":
            st.session_state.context["permit_address"] = user_input
            add_message("LIA", f"✅ Your {st.session_state.context['permit_type']} permit for {user_input} has been submitted.")
            st.session_state.step = 3
            add_message("LIA", "Would you like to apply for another permit or do something else?")

    elif st.session_state.step == 3:
        if "yes" in user_text or "another" in user_text or "menu" in user_text:
            reset_convo()
            add_message("LIA", "Happy to help! What would you like to do next?")
        else:
            add_message("LIA", "Thanks for using LIA. Have a great day!")

# Restart
st.sidebar.button("🔁 Restart", on_click=reset_convo)
