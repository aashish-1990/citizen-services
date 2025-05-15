# Enhanced Streamlit UI for LIA – Gov2Biz-style Multi-Service Chatbot with Avatars & Help
import streamlit as st

st.set_page_config(page_title="LIA – City Assistant", layout="centered")
st.image("https://cdn-icons-png.flaticon.com/512/4712/4712107.png", width=80)
st.title("🤖 Meet LIA – Your City of Kermit Assistant")

if "step" not in st.session_state:
    st.session_state.step = 0
if "intent" not in st.session_state:
    st.session_state.intent = None

st.markdown("""<style>
.chat-bubble {
  background-color: #f1f1f1;
  padding: 15px;
  border-radius: 15px;
  margin: 10px 0;
  font-size: 16px;
}
</style>""", unsafe_allow_html=True)

# Step 0: Friendly multi-intent welcome message
if st.session_state.step == 0:
    st.markdown('<div class="chat-bubble">👋 Hello there! I\'m <b>LIA</b>, your friendly assistant from the City of Kermit.<br><br>'
                'I can help you with:<br>'
                '1️⃣ Pay a utility bill<br>'
                '2️⃣ Pay a traffic or parking ticket<br>'
                '3️⃣ Apply for a permit (like garage sale or construction)<br>'
                '4️⃣ Report an issue (e.g., pothole, light outage)<br>'
                '5️⃣ Something else</div>', unsafe_allow_html=True)

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
    st.button("❓ Help", help="You can click Go Back to return to the home menu at any time.")

    if intent == "Pay a utility bill":
        st.markdown('<div class="chat-bubble">💧 Great! Let\'s look up your bill.<br>'
                    'Could you please enter the address where you receive the service?</div>', unsafe_allow_html=True)
        address_input = st.text_input("Service Address", placeholder="e.g., 123 South Olive Street")
        if st.button("Find My Bill") and address_input:
            if "olive" in address_input.lower():
                st.success("✅ Found one unpaid Water bill for $105.75 due May 31.")
                st.markdown("[💳 Pay Now](https://pay.kermitcity.gov/checkout?acc=01-00600-00&amt=105.75)", unsafe_allow_html=True)
                st.button("⬅️ Go Back", on_click=lambda: st.session_state.update(step=0))
            else:
                st.warning("No unpaid bills found for that address.")
                st.button("⬅️ Try Another Address", on_click=lambda: st.session_state.update(step=1))

    elif intent == "Pay a ticket":
        st.markdown('<div class="chat-bubble">🚓 No worries — I can help you pay your ticket.<br>'
                    'Can you enter your ticket number or license plate?</div>', unsafe_allow_html=True)
        ticket_id = st.text_input("Ticket Number / Plate")
        if st.button("Check Ticket") and ticket_id:
            st.success("✅ You have a parking ticket for $65.00 issued on May 2. Due: May 30.")
            st.markdown("[💳 Pay Ticket Now](https://pay.kermitcity.gov/ticket/checkout?ref=XYZ123)", unsafe_allow_html=True)
            st.button("⬅️ Go Back", on_click=lambda: st.session_state.update(step=0))

    elif intent == "Apply for a permit":
        st.markdown('<div class="chat-bubble">📝 I can help you apply for a permit. What kind?</div>', unsafe_allow_html=True)
        permit_type = st.selectbox("Permit Type", ["Garage Sale", "Event", "Construction", "Other"])
        if st.button("Start Application"):
            st.info(f"Permit form for **{permit_type}** will be opened here soon. (Prototype stub)")
            st.button("⬅️ Go Back", on_click=lambda: st.session_state.update(step=0))

    elif intent == "Report a city issue":
        st.markdown('<div class="chat-bubble">📌 What would you like to report and where?</div>', unsafe_allow_html=True)
        issue_type = st.selectbox("Issue Type", ["Pothole", "Streetlight Out", "Water Leak", "Graffiti", "Other"])
        location = st.text_input("Issue Location")
        if st.button("Submit Report") and location:
            st.success(f"📨 Your report about '{issue_type}' at '{location}' has been submitted to the City. Thank you!")
            st.button("⬅️ Report Another Issue", on_click=lambda: st.session_state.update(step=0))

    elif intent == "Something else":
        st.text_area("Please describe your issue or request")
        if st.button("Send to City Clerk"):
            st.success("Thank you! A city staff member will review and follow up shortly.")
            st.button("⬅️ Back to Main Menu", on_click=lambda: st.session_state.update(step=0))

# Optional reset
st.sidebar.button("🔁 Restart", on_click=lambda: st.session_state.clear())
