# Streamlit UI for LIA – Prototype to Showcase Conversational Flows
import streamlit as st
import uuid

st.set_page_config(page_title="LIA – City Assistant Prototype", layout="centered")
st.image("https://cdn-icons-png.flaticon.com/512/4712/4712107.png", width=80)
st.title("🤖 Meet LIA – Your City of Kermit Assistant")

# Session state initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "step" not in st.session_state:
    st.session_state.step = 0
if "intent" not in st.session_state:
    st.session_state.intent = None
if "context" not in st.session_state:
    st.session_state.context = {}
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "email" not in st.session_state:
    st.session_state.email = ""

# Admin toggle
st.sidebar.markdown("### Admin Panel")
st.session_state.is_admin = st.sidebar.toggle("Switch to Admin Mode")
st.sidebar.button("🔁 Restart", on_click=lambda: st.session_state.clear())

# Citizen Mode: Intent detection and flows
if not st.session_state.is_admin:
    user_input = st.text_input("💬 What would you like to do today?")

    if st.session_state.step == 0:
        if user_input:
            user_lower = user_input.lower()
            if "bill" in user_lower:
                st.session_state.intent = "pay_bill"
                st.session_state.step = 1
            elif "ticket" in user_lower:
                st.session_state.intent = "pay_ticket"
                st.session_state.step = 1
            elif "permit" in user_lower:
                st.session_state.intent = "apply_permit"
                st.session_state.step = 1
            elif "report" in user_lower or "issue" in user_lower:
                st.session_state.intent = "report_issue"
                st.session_state.step = 1
            else:
                st.session_state.intent = "unknown"
                st.session_state.step = 1

    if st.session_state.step == 0:
        st.markdown("""
        <div class='chat-bubble'>
        👋 Hi! I’m LIA, your local assistant. You can ask me to:
        <ul>
            <li>💧 Pay a utility bill</li>
            <li>🚓 Pay a ticket</li>
            <li>📝 Apply for a permit</li>
            <li>🔧 Report a city issue</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    elif st.session_state.step == 1:
        intent = st.session_state.intent

        if intent == "pay_bill":
            address = st.text_input("📍 Enter your address to locate your bill:")
            if address:
                st.session_state.context['address'] = address
                st.success(f"✅ Bill found for {address}. Amount due: $82.35")
                if st.button("💳 Pay Now"):
                    st.session_state.step = 1.1

        elif intent == "pay_ticket":
            ticket = st.text_input("🚓 Enter your ticket or plate number:")
            if ticket:
                st.session_state.context['ticket'] = ticket
                st.success(f"✅ Ticket {ticket} found. Fine: $45.00")
                if st.button("💳 Pay Ticket"):
                    st.session_state.step = 1.2

        elif intent == "apply_permit":
            permit_type = st.selectbox("📝 Select permit type:", ["Garage Sale", "Construction", "Event", "Other"])
            address = st.text_input("📍 Enter address for the permit:")
            date_range = st.date_input("📅 Permit Date Range", [])
            if permit_type and address and len(date_range) == 2:
                if st.button("Submit Application"):
                    st.success(f"Permit request for {permit_type} submitted for {address}.")
                    st.session_state.step = 1.3

        elif intent == "report_issue":
            issue_type = st.selectbox("⚠️ Issue Type", ["Pothole", "Streetlight Out", "Water Leak", "Other"])
            location = st.text_input("📍 Issue Location")
            details = st.text_area("📝 Describe the issue")
            if issue_type and location:
                if st.button("Report Issue"):
                    st.success(f"Thanks! Your report has been submitted to the city team.")
                    st.session_state.step = 1.4

        elif intent == "unknown":
            st.warning("🤔 I’m not sure how to help with that. Try saying 'pay my bill' or 'get a permit'.")
            if st.button("⬅️ Start Over"):
                st.session_state.step = 0

    elif st.session_state.step == 1.1:  # After Pay Bill
        email = st.text_input("📧 Where should we send the receipt?")
        if email:
            st.session_state.email = email
            st.success(f"Payment successful! Receipt sent to {email}.")
            st.session_state.step = 2

    elif st.session_state.step == 1.2:  # After Pay Ticket
        email = st.text_input("📧 Where should we send the ticket confirmation?")
        if email and "@" in email and "." in email:
            st.session_state.email = email
            if st.button("Confirm Payment"):
                st.success(f"Ticket payment successful! Confirmation sent to {email}.")
                st.session_state.step = 2

    elif st.session_state.step == 1.3:  # After Permit Submission
        email = st.text_input("📧 Enter your email for confirmation:")
        if email:
            st.session_state.email = email
            st.success(f"Permit confirmation sent to {email}.")
            st.session_state.step = 2

    elif st.session_state.step == 1.4:  # After Report Submission
        email = st.text_input("📧 Enter your email for update notifications:")
        if email:
            st.session_state.email = email
            st.success(f"Issue report logged. Updates will be sent to {email}.")
            st.session_state.step = 2

    elif st.session_state.step == 2:
        st.markdown("""
        <div class='chat-bubble'>
        🎉 Thanks for using LIA! Here’s what we helped you with today:
        </div>
        """, unsafe_allow_html=True)
        for k, v in st.session_state.context.items():
            st.markdown(f"**{k.capitalize()}:** {v}")
        if st.session_state.email:
            st.markdown(f"**Receipt sent to:** {st.session_state.email}")
        st.markdown("""
        ---
        Would you like to do anything else?
        """)
        if st.button("💧 Pay another utility bill"):
            st.session_state.update(step=1, intent="pay_bill")
        if st.button("🚓 Pay another ticket"):
            st.session_state.update(step=1, intent="pay_ticket")
        if st.button("📝 Apply for a permit"):
            st.session_state.update(step=1, intent="apply_permit")
        if st.button("🔧 Report an issue"):
            st.session_state.update(step=1, intent="report_issue")
        if st.button("🏠 Return to main menu"):
            st.session_state.clear()

# Admin Mode: Placeholder mock view
else:
    st.markdown("""
    ### 🧑‍💼 Admin Console
    View recent citizen intents and simulate approvals.
    """)
    st.success("💧 Citizen request: Pay Bill for 123 Olive Street → $82.35")
    st.success("📝 Permit request: Garage Sale at 25 Elm Road")
    st.success("⚠️ Issue reported: Pothole at Main & 3rd")
    st.button("Approve Permit")
    st.button("Mark Issue as Resolved")
