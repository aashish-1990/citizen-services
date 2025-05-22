import streamlit as st
import uuid

st.set_page_config(page_title="LIA – City Assistant", layout="centered")

# --- Session Setup ---
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

# --- Helper Functions ---
def add_message(sender, text):
    icon = "🟣" if sender == "LIA" else "🟢"
    st.session_state.messages.append(f"{icon} **{sender}**: {text}")

def reset_convo():
    st.session_state.messages = []
    st.session_state.intent = None
    st.session_state.step = 0
    st.session_state.context = {}

def is_valid_address(text):
    text = text.lower()
    return any(keyword in text for keyword in ["olive", "main", "pine", "123"])

def simulate_bill_lookup(address):
    if is_valid_address(address):
        st.session_state.context["amount_due"] = "$82.35"
        return f"✅ Found bill for **{address}**. Amount due: **$82.35**"
    return f"❌ No bill found for {address}"

def simulate_payment():
    return "✅ Payment successful! Receipt sent via SMS and email."

# --- Initial Greeting ---
if st.session_state.step == 0 and not st.session_state.messages:
    add_message("LIA", "Hi there! I’m LIA — your City of Kermit Assistant. How can I help you today?")
    add_message("LIA", "You can say things like:\n\n- I want to pay my bill\n- I want to apply for a permit\n- I have a ticket to pay\n- I want to report a water leak")

# --- Title + Message Display ---
st.title("🤖 Meet LIA – Your City of Kermit Assistant")
for msg in st.session_state.messages:
    st.markdown(msg, unsafe_allow_html=True)

# --- Chat Input ---
user_input = st.chat_input("Type your request...")

if user_input:
    add_message("You", user_input)
    text = user_input.lower()

    # Step 0: Detect intent
    if st.session_state.step == 0:
        if "bill" in text:
            st.session_state.intent = "pay_bill"
            st.session_state.step = 1
            add_message("LIA", "Great! Please enter your address to locate your bill (e.g., 123 Olive Street).")
        elif "ticket" in text:
            st.session_state.intent = "pay_ticket"
            st.session_state.step = 1
            add_message("LIA", "Sure, what’s your ticket or plate number?")
        elif "permit" in text:
            st.session_state.intent = "apply_permit"
            st.session_state.step = 1
            add_message("LIA", "What type of permit do you want to apply for?")
        elif "report" in text:
            st.session_state.intent = "report_issue"
            st.session_state.step = 1
            add_message("LIA", "Please describe the issue and its location.")
        else:
            add_message("LIA", "I didn’t quite catch that. You can say things like 'pay my bill' or 'apply for a permit'.")

    # Step 1: Collect address or details
    elif st.session_state.step == 1:
        if st.session_state.intent == "pay_bill":
            if "bill" in text:
                add_message("LIA", "You’ve already told me you want to pay a bill. Now please share your address (e.g., 123 Olive Street).")
            elif not is_valid_address(text):
                add_message("LIA", "❌ That doesn’t look like a valid address. Try something like '123 Olive Street'.")
            else:
                st.session_state.context["address"] = text
                msg = simulate_bill_lookup(text)
                add_message("LIA", msg)
                if "✅" in msg:
                    st.session_state.step = 2
                    add_message("LIA", f"Do you want to proceed with payment of {st.session_state.context['amount_due']}? (yes/no)")

        elif st.session_state.intent == "pay_ticket":
            st.session_state.context["ticket"] = text
            add_message("LIA", f"✅ Ticket {text} found. Fine: $45.00")
            st.session_state.step = 2
            add_message("LIA", "Would you like to pay it now? (yes/no)")

        elif st.session_state.intent == "apply_permit":
            st.session_state.context["permit_type"] = text
            st.session_state.step = 2
            add_message("LIA", "Please enter the address for this permit.")

        elif st.session_state.intent == "report_issue":
            add_message("LIA", f"✅ Issue noted: {text}")
            st.session_state.step = 3
            add_message("LIA", "Would you like to report anything else or return to the main menu?")

    # Step 2: Confirmation step
    elif st.session_state.step == 2:
        if text.strip() in ["yes", "y"]:
            add_message("LIA", "📩 Sending payment link to your phone and email...")
            add_message("LIA", simulate_payment())
            st.session_state.step = 3
            add_message("LIA", "Would you like to do anything else?")
        elif text.strip() in ["no", "n"]:
            add_message("LIA", "Okay! Let me know if you need anything else.")
            st.session_state.step = 3
        elif st.session_state.intent == "apply_permit":
            st.session_state.context["permit_address"] = text
            add_message("LIA", f"✅ Your {st.session_state.context['permit_type']} permit at {text} has been submitted.")
            st.session_state.step = 3
            add_message("LIA", "Would you like to do anything else?")
        else:
            add_message("LIA", "Please reply 'yes' or 'no'.")

    # Step 3: Wrap up / Restart
    elif st.session_state.step == 3:
        if "yes" in text or "menu" in text or "another" in text:
            reset_convo()
            add_message("LIA", "Sure, what would you like to do next?")
        else:
            add_message("LIA", "Thanks for using LIA. Have a great day!")

# --- Restart Button ---
st.sidebar.button("🔁 Restart", on_click=reset_convo)
