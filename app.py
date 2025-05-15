# Enhanced Streamlit UI for LIA – Gov2Biz-style Multi-Service Chatbot
import streamlit as st

st.set_page_config(page_title="LIA – City Assistant", layout="centered")
st.title("🤖 Meet LIA – Your City of Kermit Assistant")

if "step" not in st.session_state:
    st.session_state.step = 0
if "intent" not in st.session_state:
    st.session_state.intent = None

# Step 0: Friendly multi-intent welcome message
if st.session_state.step == 0:
    st.markdown("""
    👋 Hello there! I'm **LIA**, your friendly assistant from the City of Kermit.
    
    I can help you with:
    
    1️⃣ Pay a utility bill  
    2️⃣ Pay a traffic or parking ticket  
    3️⃣ Apply for a permit (like garage sale or construction)  
    4️⃣ Report an issue (e.g., pothole, light outage)  
    5️⃣ Something else
    """)

    st.session_state.intent = st.radio("What would you like help with?", [
        "Pay a utility bill",
        "Pay a ticket",
        "Apply for a permit",
        "Report a city issue",
        "Something else"
    ])

    if st.button("Continue"):
        st.session_state.step = 1

# Step 1: Route by Intent
if st.session_state.step == 1:
    intent = st.session_state.intent

    if intent == "Pay a utility bill":
        st.markdown("""
        💧 Great! Let's look up your bill.
        Could you please enter the address where you receive the service?
        """)
        address_input = st.text_input("Service Address", placeholder="e.g., 123 South Olive Street")
        if st.button("Find My Bill") and address_input:
            if "olive" in address_input.lower():
                st.success("✅ Found one unpaid Water bill for $105.75 due May 31.")
                st.markdown("[💳 Pay Now](https://pay.kermitcity.gov/checkout?acc=01-00600-00&amt=105.75)", unsafe_allow_html=True)
                st.session_state.step = 2
            else:
                st.warning("No unpaid bills found for that address.")

    elif intent == "Pay a ticket":
        st.markdown("""
        🚓 No worries — I can help you pay your ticket.
        Can you enter your ticket number or license plate?
        """)
        ticket_id = st.text_input("Ticket Number / Plate")
        if st.button("Check Ticket") and ticket_id:
            st.success("✅ You have a parking ticket for $65.00 issued on May 2. Due: May 30.")
            st.markdown("[💳 Pay Ticket Now](https://pay.kermitcity.gov/ticket/checkout?ref=XYZ123)", unsafe_allow_html=True)

    elif intent == "Apply for a permit":
        st.markdown("""
        📝 I can help you apply for a permit. What kind?
        """)
        permit_type = st.selectbox("Permit Type", ["Garage Sale", "Event", "Construction", "Other"])
        if st.button("Start Application"):
            st.info(f"Permit form for **{permit_type}** will be opened here soon. (Prototype stub)")

    elif intent == "Report a city issue":
        issue_type = st.selectbox("What would you like to report?", ["Pothole", "Streetlight Out", "Water Leak", "Graffiti", "Other"])
        location = st.text_input("Where is the issue located?")
        if st.button("Submit Report") and location:
            st.success(f"📨 Your report about '{issue_type}' at '{location}' has been submitted to the City. Thank you!")

    elif intent == "Something else":
        st.text_area("Please describe your issue or request")
        if st.button("Send to City Clerk"):
            st.success("Thank you! A city staff member will review and follow up shortly.")

# Optional reset
st.sidebar.button("🔁 Restart", on_click=lambda: st.session_state.clear())
