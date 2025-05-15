# Streamlit front-end for GovCraft Citizen Chat Agent
import streamlit as st

st.set_page_config(page_title="City of Kermit – Pay Utility Bill", layout="centered")
st.title("💬 Pay Your City Bill")

# Session state to track conversation if needed
if "step" not in st.session_state:
    st.session_state.step = 0

if "address" not in st.session_state:
    st.session_state.address = ""

if "bill_found" not in st.session_state:
    st.session_state.bill_found = False

if "email" not in st.session_state:
    st.session_state.email = ""

# Step 0: Greet and ask address
if st.session_state.step == 0:
    st.write("👋 Hello! I can help you pay your utility bill. Please enter your **street address**.")
    address_input = st.text_input("Your Address", placeholder="e.g., 123 South Olive Street")
    if st.button("Search My Bills") and address_input:
        st.session_state.address = address_input
        if "olive" in address_input.lower():
            st.session_state.bill_found = True
        st.session_state.step = 1

# Step 1: Show bill info
if st.session_state.step == 1:
    if st.session_state.bill_found:
        st.success("✅ We found an unpaid bill at this address!")
        st.markdown("""
        **Bill Details**
        - 💧 Service: Water
        - 💵 Amount: $105.75
        - 📅 Due: May 31, 2025
        """)
        if st.button("Yes, I want to pay"):
            st.session_state.step = 2
    else:
        st.warning("❌ Sorry, we couldn’t find any unpaid bills at that address.")
        if st.button("Try Another Address"):
            st.session_state.step = 0

# Step 2: Email + Payment link
if st.session_state.step == 2:
    st.markdown("### 📨 Where should we send your receipt?")
    email_input = st.text_input("Email Address", placeholder="e.g., you@example.com")
    if st.button("Generate Payment Link") and email_input:
        st.session_state.email = email_input
        st.session_state.step = 3

# Step 3: Show payment link
if st.session_state.step == 3:
    st.success(f"✅ Thank you! A receipt will be sent to **{st.session_state.email}** after payment.")
    st.markdown("[💳 Click here to Pay Now](https://pay.kermitcity.gov/checkout?acc=01-00600-00&amt=105.75)", unsafe_allow_html=True)
    if st.button("Start Over"):
        for key in st.session_state:
            st.session_state[key] = None
        st.session_state.step = 0
