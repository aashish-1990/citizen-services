# Streamlit UI for LIA – Simplified & Smooth Prototype
import streamlit as st
import uuid

st.set_page_config(page_title="LIA – City Assistant Prototype", layout="centered")
st.image("https://cdn-icons-png.flaticon.com/512/4712/4712107.png", width=80)
st.title("🤖 Meet LIA – Your City of Kermit Assistant")

# Session state
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

# Sidebar controls
st.sidebar.markdown("### Admin Panel")
st.session_state.is_admin = st.sidebar.toggle("Switch to Admin Mode")
st.sidebar.button("🔁 Restart", on_click=lambda: st.session_state.clear())

# Citizen Mode
if not st.session_state.is_admin:
    if st.session_state.step == 0:
        st.markdown("""
        👋 Hi! I’m LIA, your assistant. You can ask me to:
        - 💧 Pay a utility bill
        - 🚓 Pay a ticket
        - 📝 Apply for a permit
        - 🔧 Report an issue
        """)
        user_input = st.text_input("💬 What would you like to do?")
        if user_input:
            query = user_input.lower()
            if "bill" in query:
                st.session_state.intent = "pay_bill"
            elif "ticket" in query:
                st.session_state.intent = "pay_ticket"
            elif "permit" in query:
                st.session_state.intent = "apply_permit"
            elif "issue" in query:
                st.session_state.intent = "report_issue"
            else:
                st.warning("I didn’t catch that. Try asking to pay a bill or report an issue.")
                st.stop()
            st.session_state.step = 1

    elif st.session_state.step == 1:
        intent = st.session_state.intent
        if intent == "pay_bill":
            address = st.text_input("📍 Your address:")
            if address:
                st.success(f"✅ Bill for {address}: $82.35")
                if st.button("💳 Pay Now"):
                    st.session_state.step = 2
        elif intent == "pay_ticket":
            ticket_id = st.text_input("🔢 Ticket or plate number:")
            if ticket_id:
                st.success(f"✅ Ticket {ticket_id} found. Fine: $45.00")
                if st.button("💳 Pay Now"):
                    st.session_state.step = 2
        elif intent == "apply_permit":
            ptype = st.selectbox("📄 Permit type:", ["Garage Sale", "Construction", "Event"])
            paddr = st.text_input("📍 Permit address:")
            if ptype and paddr:
                if st.button("Submit Application"):
                    st.success("Permit submitted.")
                    st.session_state.step = 2
        elif intent == "report_issue":
            itype = st.selectbox("🛠 Issue:", ["Pothole", "Streetlight", "Leak"])
            loc = st.text_input("📍 Location:")
            if itype and loc:
                if st.button("Submit Report"):
                    st.success("Thanks for reporting. Our team will check it soon.")
                    st.session_state.step = 2

    elif st.session_state.step == 2:
        st.success("✅ Done! Would you like to do something else?")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🏠 Main Menu"):
                st.session_state.clear()
        with col2:
            if st.button("🔁 Repeat This Task"):
                st.session_state.step = 1
        with col3:
            if st.button("❌ Exit"):
                st.success("Thanks for using LIA!")

# Admin View
else:
    st.markdown("""
    ### 🧑‍💼 Admin Console
    (Sample view only)
    """)
    st.info("Bill uploaded for 123 Olive St, $82.35")
    st.info("Garage Sale Permit requested at 210 Ash Lane")
    st.info("Pothole reported on 5th & Oak")
