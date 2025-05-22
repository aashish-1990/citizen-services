import streamlit as st
import uuid
import time

st.set_page_config(page_title="LIA – Kermit Assistant", layout="centered")

# --- Session State ---
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
def log_event(msg):
    st.write(f"🛠️ [log] {msg}")

def add_message(speaker, text):
    icon = "🟣" if speaker == "LIA" else "🟢"
    st.session_state.messages.append(f"{icon} **{speaker}**: {text}")

def reset_convo():
    st.session_state.messages = []
    st.session_state.intent = None
    st.session_state.step = 0
    st.session_state.context = {}

# --- Initial Greeting ---
if st.session_state.step == 0 and not st.session_state.messages:
    add_message("LIA", "Hi there! I’m LIA — your City of Kermit Assistant.")
    add_message("LIA", "You can say things like:\n- I want to pay my bill\n- I want to apply for a permit\n- I want to report an issue")
    log_event("Greeting and options sent.")
    st.session_state.step = 0

# --- Title + Message Display ---
st.title("🤖 Meet LIA – Your City of Kermit Assistant")
for msg in st.session_state.messages:
    st.markdown(msg, unsafe_allow_html=True)

# --- Chat Input ---
user_input = st.chat_input("Type your request...")

if user_input:
    add_message("You", user_input)
    log_event(f"User said: {user_input}")
    text = user_input.lower()

    # Step 0 – Intent Detection
    if st.session_state.step == 0:
        if "bill" in text:
            st.session_state.intent = "pay_bill"
            st.session_state.step = 1
            add_message("LIA", "Sure! Please enter your address to locate your bill.")
            log_event("Intent = pay_bill")
        elif "permit" in text:
            st.session_state.intent = "apply_permit"
            st.session_state.step = 1
            add_message("LIA", "What type of permit do you want to apply for?")
            log_event("Intent = apply_permit")
        elif "report" in text:
            st.session_state.intent = "report_issue"
            st.session_state.step = 1
            add_message("LIA", "Please describe the issue and its location.")
            log_event("Intent = report_issue")
        else:
            add_message("LIA", "Sorry, I didn’t understand. Try saying 'pay my bill' or 'report a leak'.")
            log_event("Intent = unknown")

    # Step 1 – Collect Details Based on Intent
    elif st.session_state.step == 1:
        intent = st.session_state.intent

        if intent == "pay_bill":
            st.session_state.context["address"] = user_input
            if any(x in text for x in ["olive", "main", "123", "pine"]):
                amount = "$82.35"
                st.session_state.context["amount"] = amount
                add_message("LIA", f"✅ Found bill for {user_input}. Amount due: {amount}")
                add_message("LIA", "Do you want to proceed with payment? (yes/no)")
                st.session_state.step = 2
                log_event(f"Address matched. Simulated bill: {amount}")
            else:
                add_message("LIA", f"❌ No bill found for {user_input}. Try again.")
                log_event("Address not matched.")

        elif intent == "apply_permit":
            st.session_state.context["permit_type"] = user_input
            add_message("LIA", f"Noted: {user_input} permit. What’s the address?")
            st.session_state.step = 2
            log_event("Permit type collected.")

        elif intent == "report_issue":
            add_message("LIA", f"✅ Thanks for reporting: '{user_input}'. Our team will check it.")
            st.session_state.step = 3
            add_message("LIA", "Do you want to do anything else?")
            log_event("Issue reported.")

    # Step 2 – Confirm Action or Collect More
    elif st.session_state.step == 2:
        intent = st.session_state.intent
        text = user_input.lower()

        if intent == "pay_bill":
            if "yes" in text:
                add_message("LIA", "📩 Please check your SMS and email for the payment link.")
                time.sleep(1)
                add_message("LIA", "✅ Payment received! Your receipt is sent.")
                add_message("LIA", "Would you like to pay another bill or return to the menu?")
                st.session_state.step = 3
                log_event("Payment simulated and confirmed.")
            elif "no" in text:
                add_message("LIA", "Okay, the payment has been cancelled. Anything else I can help with?")
                st.session_state.step = 3
                log_event("User declined payment.")
            else:
                add_message("LIA", "Please reply 'yes' or 'no' to continue.")
                log_event("Waiting for payment confirmation.")

        elif intent == "apply_permit":
            st.session_state.context["permit_address"] = user_input
            add_message("LIA", f"✅ Your permit for {st.session_state.context['permit_address']} has been submitted.")
            add_message("LIA", "Would you like to apply for another permit or go back to the menu?")
            st.session_state.step = 3
            log_event("Permit submitted.")

    # Step 3 – Final Options
    elif st.session_state.step == 3:
        if "yes" in text or "menu" in text or "another" in text:
            reset_convo()
            add_message("LIA", "Awesome! What would you like to do next?")
            log_event("Conversation restarted.")
        else:
            add_message("LIA", "Thanks for using LIA. See you next time!")
            log_event("Conversation ended.")

# --- Debug / Restart ---
with st.sidebar:
    if st.button("🔁 Restart Conversation"):
        reset_convo()
        add_message("LIA", "Hi again! What would you like to do?")
        log_event("Manual reset triggered.")
