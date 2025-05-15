# Streamlined Streamlit UI for LIA – Chat-Only Version with Full Flow
import streamlit as st

st.set_page_config(page_title="LIA – City Assistant", layout="centered")
st.image("https://cdn-icons-png.flaticon.com/512/4712/4712107.png", width=80)
st.title("🤖 Meet LIA – Your City of Kermit Assistant")

if "step" not in st.session_state:
    st.session_state.step = 0
if "intent" not in st.session_state:
    st.session_state.intent = None

# Chat style
st.markdown("""<style>
.chat-bubble {
  background-color: #f1f1f1;
  padding: 15px;
  border-radius: 15px;
  margin: 10px 0;
  font-size: 16px;
}
</style>""", unsafe_allow_html=True)

user_input = st.text_input("💬 Type what you'd like to do:", key="user_input")

if st.session_state.step == 0:
    if user_input:
        st.success(f"You said: {user_input}")
        user_lower = user_input.lower()
        if "bill" in user_lower:
            st.session_state.intent = "Pay a utility bill"
            st.session_state.step = 1
        elif "ticket" in user_lower:
            st.session_state.intent = "Pay a ticket"
            st.session_state.step = 1
        elif "permit" in user_lower:
            st.session_state.intent = "Apply for a permit"
            st.session_state.step = 1
        elif "report" in user_lower or "issue" in user_lower:
            st.session_state.intent = "Report a city issue"
            st.session_state.step = 1
        else:
            st.session_state.intent = "Something else"
            st.session_state.step = 1

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

# Step 1: Flows based on intent
if st.session_state.step == 1:
    if st.session_state.intent == "Pay a utility bill":
        st.markdown("### 💧 Let's help you pay your utility bill")
        address = st.text_input("Please enter your service address:", key="address")
        if address:
            st.success(f"Bill found for {address}. Amount due: $82.35")
            st.button("💳 Pay Now")
        st.button("⬅️ Go Back", on_click=lambda: st.session_state.update(step=0))

    elif st.session_state.intent == "Pay a ticket":
        st.markdown("### 🚓 Enter your ticket number or plate:")
        ticket = st.text_input("Ticket Number or Plate", key="ticket")
        if ticket:
            st.success(f"Ticket {ticket} found. Amount due: $45.00")
            st.button("💳 Pay Now")
        st.button("⬅️ Go Back", on_click=lambda: st.session_state.update(step=0))

    elif st.session_state.intent == "Apply for a permit":
        st.markdown("### 📝 Select Permit Type")
        permit = st.selectbox("Permit Type", ["Garage Sale", "Construction", "Event", "Other"])
        st.text_input("Enter address for permit")
        st.date_input("Start Date")
        st.date_input("End Date")
        st.button("Submit Application")
        st.button("⬅️ Go Back", on_click=lambda: st.session_state.update(step=0))

    elif st.session_state.intent == "Report a city issue":
        st.markdown("### 🛠️ Report an issue")
        issue = st.selectbox("Issue Type", ["Pothole", "Streetlight Out", "Water Leak", "Other"])
        location = st.text_input("Issue Location")
        description = st.text_area("Describe the issue")
        st.button("Submit Report")
        st.button("⬅️ Go Back", on_click=lambda: st.session_state.update(step=0))

    else:
        st.text_area("Please describe your issue")
        st.button("Send to City Clerk")
        st.button("⬅️ Go Back", on_click=lambda: st.session_state.update(step=0))

# Optional reset
st.sidebar.button("🔁 Restart", on_click=lambda: st.session_state.clear())
