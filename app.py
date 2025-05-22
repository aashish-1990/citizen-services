# LIA – Agentic Assistant (Streamlit-Only Version for Render Hosting)

import streamlit as st
import uuid
import time
import logging

# === Logging Setup ===
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("lia-streamlit")

# === Session State Initialization ===
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "step" not in st.session_state:
    st.session_state.step = 0
if "intent" not in st.session_state:
    st.session_state.intent = None
if "context" not in st.session_state:
    st.session_state.context = {}
if "messages" not in st.session_state:
    st.session_state.messages = []

# === UI Functions ===
def lia_say(message):
    st.session_state.messages.append(("LIA", message))
    logger.info(f"LIA: {message}")

def user_say(message):
    st.session_state.messages.append(("User", message))
    logger.info(f"User: {message}")

def reset_conversation():
    st.session_state.step = 0
    st.session_state.intent = None
    st.session_state.context = {}
    st.session_state.messages = []
    st.rerun()

# === Layout ===
st.set_page_config(page_title="LIA – City Assistant", layout="centered")
st.sidebar.button("🔁 Restart Conversation", on_click=reset_conversation)
st.title("🤖 Meet LIA – Your City of Kermit Assistant")

# === Display Messages ===
for sender, msg in st.session_state.messages:
    if sender == "LIA":
        with st.chat_message("assistant"):
            st.markdown(f"**🟣 LIA:** {msg}")
    else:
        with st.chat_message("user"):
            st.markdown(f"**🟢 You:** {msg}")

# === Chat Logic ===
def process_input(user_input):
    user_say(user_input)
    step = st.session_state.step
    intent = st.session_state.intent
    context = st.session_state.context

    if step == 0:
        # Show welcome + get intent
        if any(x in user_input.lower() for x in ["bill", "pay"]):
            st.session_state.intent = "pay_bill"
            st.session_state.step = 1
            lia_say("Sure! Please enter your address to locate your bill.")
        elif "permit" in user_input.lower():
            st.session_state.intent = "apply_permit"
            st.session_state.step = 1
            lia_say("What type of permit are you applying for?")
        elif "ticket" in user_input.lower():
            st.session_state.intent = "pay_ticket"
            st.session_state.step = 1
            lia_say("Please provide your ticket or plate number.")
        elif "report" in user_input.lower() or "issue" in user_input.lower():
            st.session_state.intent = "report_issue"
            st.session_state.step = 1
            lia_say("What issue would you like to report?")
        else:
            lia_say("I didn’t quite catch that. You can ask me to pay a bill, apply for a permit, or report an issue.")

    elif step == 1:
        # Handle next step based on intent
        if intent == "pay_bill":
            context["address"] = user_input
            if any(x in user_input.lower() for x in ["olive", "pine", "main", "123"]):
                lia_say(f"✅ Bill found for {user_input}. Amount due: $82.35. Is this correct?")
                st.session_state.step = 2
            else:
                lia_say(f"❌ No bill found for {user_input}. Try again.")
        elif intent == "apply_permit":
            context["permit_type"] = user_input
            lia_say("Got it. What is the address for the permit?")
            st.session_state.step = 2
        elif intent == "pay_ticket":
            context["ticket_id"] = user_input
            lia_say(f"✅ Ticket {user_input} found. Fine: $45.00. Do you want to proceed to payment?")
            st.session_state.step = 2
        elif intent == "report_issue":
            context["issue"] = user_input
            lia_say("Please provide the location of this issue.")
            st.session_state.step = 2

    elif step == 2:
        if intent == "pay_bill":
            if "yes" in user_input.lower():
                lia_say("💳 A payment link has been sent to your email and phone. Please complete the payment.")
                time.sleep(1.5)
                lia_say("✅ Payment confirmed. You can now download your receipt.")
                st.download_button("📥 Download Receipt", data="Receipt#123-Kermit", file_name="kermit-receipt.txt")
                lia_say("Do you want to do anything else?")
                st.session_state.step = 0
            else:
                lia_say("Okay, let’s try again. What’s your address?")
                st.session_state.step = 1
        elif intent == "apply_permit":
            context["address"] = user_input
            lia_say(f"📄 Your {context['permit_type']} permit request for {context['address']} has been submitted.")
            st.session_state.step = 0
        elif intent == "pay_ticket":
            if "yes" in user_input.lower():
                lia_say("💳 Payment link sent. After payment confirmation, you will receive a receipt.")
                time.sleep(1)
                lia_say("✅ Ticket paid successfully. Anything else I can help with?")
                st.session_state.step = 0
            else:
                lia_say("Okay. Ticket not paid.")
                st.session_state.step = 0
        elif intent == "report_issue":
            context["location"] = user_input
            lia_say(f"🛠️ Issue reported at {context['location']}. Our team will investigate.")
            st.session_state.step = 0

# === Chat Input ===
user_input = st.chat_input("Type your request...")
if user_input:
    process_input(user_input)

# === Initial Greeting ===
if st.session_state.step == 0 and len(st.session_state.messages) == 0:
    lia_say("Hi there! I’m LIA — your City of Kermit Assistant. How can I help you today?")
    time.sleep(0.5)
    lia_say("You can say things like:\n\n- I want to pay my bill\n- I want to apply for a permit\n- I have a ticket to pay\n- I want to report an issue")
