# app.py – Final MVP Version for LIA (Streamlit-Only, No FastAPI)

import streamlit as st
import uuid

# Setup
st.set_page_config(page_title="LIA – City of Kermit Assistant", layout="centered")
st.image("https://cdn-icons-png.flaticon.com/512/4712/4712107.png", width=80)
st.title("🤖 Meet LIA – Your City of Kermit Assistant")

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "step" not in st.session_state:
    st.session_state.step = 0
if "intent" not in st.session_state:
    st.session_state.intent = None
if "context" not in st.session_state:
    st.session_state.context = {}

# STEP 0: Welcome & Menu
if st.session_state.step == 0:
    st.success("Hi there! I’m LIA — your City of Kermit Assistant.\n\nI can help you with:")
    st.markdown("### 👇 Choose a service to get started:")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("💧 Pay Bill"):
            st.session_state.intent = "pay_bill"
            st.session_state.step = 1
    with col2:
        if st.button("🚓 Pay Ticket"):
            st.session_state.intent = "pay_ticket"
            st.session_state.step = 1
    with col3:
        if st.button("📝 Apply Permit"):
            st.session_state.intent = "apply_permit"
            st.session_state.step = 1
    with col4:
        if st.button("🔧 Report Issue"):
            st.session_state.intent = "report_issue"
            st.session_state.step = 1

# STEP 1: Flow Based on Intent
elif st.session_state.step == 1:
    intent = st.session_state.intent

    if intent == "pay_bill":
        address = st.text_input("📍 Please enter your address to find your bill:")
        if address:
            st.session_state.context["address"] = address
            st.success(f"✅ Found bill for {address}: **$82.35**")
            if st.button("💳 Pay Now"):
                st.session_state.step = 2

    elif intent == "pay_ticket":
        ticket = st.text_input("🔢 Enter your ticket number or license plate:")
        if ticket:
            st.session_state.context["ticket"] = ticket
            st.success(f"✅ Ticket {ticket} found. Fine: **$45.00**")
            if st.button("💳 Pay Ticket"):
                st.session_state.step = 2

    elif intent == "apply_permit":
        ptype = st.selectbox("📄 Select permit type:", ["Garage Sale", "Construction", "Event"])
        location = st.text_input("📍 Enter location for the permit:")
        if ptype and location:
            st.session_state.context.update({"permit_type": ptype, "location": location})
            if st.button("📤 Submit Application"):
                st.success(f"✅ Your {ptype} permit for {location} has been submitted.")
                st.session_state.step = 2

    elif intent == "report_issue":
        issue = st.selectbox("🛠 What would you like to report?", ["Pothole", "Water Leak", "Streetlight Out"])
        loc = st.text_input("📍 Location of the issue:")
        if issue and loc:
            st.success("✅ Report submitted! Our city team will look into it.")
            st.session_state.step = 2

# STEP 2: Completion + Reset Options
elif st.session_state.step == 2:
    st.success("✅ Done! Would you like to do something else?")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏠 Main Menu"):
            st.session_state.step = 0
            st.session_state.intent = None
            st.session_state.context = {}
    with col2:
        if st.button("🔁 Repeat This Task"):
            st.session_state.step = 1
    with col3:
        if st.button("❌ Exit"):
            st.info("Thank you for using LIA. Have a great day! 👋")
