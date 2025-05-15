# Streamlined Streamlit UI for LIA – Fast Demo Version for CEO/CTO
import streamlit as st
import streamlit.components.v1 as components

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

# Voice Welcome on Load (Simplified, Cloud-Friendly)
components.html("""
<script>
window.onload = function() {
  const speakWelcome = () => {
    const msg = new SpeechSynthesisUtterance("Hi there! I'm LIA, your assistant from the City of Kermit. How can I help you today?");
    const voices = speechSynthesis.getVoices();
    msg.voice = voices.find(v => v.name.includes('Female')) || voices[0];
    msg.lang = 'en-US';
    msg.pitch = 1.2;
    msg.rate = 1;
    speechSynthesis.speak(msg);
  }
  if (speechSynthesis.getVoices().length === 0) {
    speechSynthesis.onvoiceschanged = speakWelcome;
  } else {
    speakWelcome();
  }
};
</script>
""", height=0)

# Voice input (Streamlined, no extra submission logic)
components.html("""
<script>
  let recognition;
  function startListening() {
    if (!('webkitSpeechRecognition' in window)) {
      alert("Your browser doesn't support voice recognition. Please use Chrome.");
      return;
    }
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";
    recognition.start();
    recognition.onresult = function(event) {
      const transcript = event.results[0][0].transcript;
      document.getElementById("voice_input").value = transcript;
      document.getElementById("voice_input").dispatchEvent(new Event("input", { bubbles: true }));
    };
  }
</script>
<button onclick="startListening()">🎤 Speak to LIA</button>
""", height=0)

user_input = st.text_input("🎙️ Or type here what you'd like to do:", key="voice_input")

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

# Step 1: Utility bill flow (placeholder)
if st.session_state.step == 1:
    if st.session_state.intent == "Pay a utility bill":
        st.markdown("### 💧 Let's help you pay your utility bill")
        st.text_input("Please enter your service address:")
        st.button("🔍 Find My Bill")
        st.button("⬅️ Go Back", on_click=lambda: st.session_state.update(step=0))
    elif st.session_state.intent == "Pay a ticket":
        st.markdown("### 🚓 Enter your ticket number or plate:")
        st.text_input("Ticket Number or Plate")
        st.button("🔍 Look Up Ticket")
        st.button("⬅️ Go Back", on_click=lambda: st.session_state.update(step=0))
    elif st.session_state.intent == "Apply for a permit":
        st.markdown("### 📝 Select Permit Type")
        st.selectbox("Permit Type", ["Garage Sale", "Construction", "Event", "Other"])
        st.button("Start Application")
        st.button("⬅️ Go Back", on_click=lambda: st.session_state.update(step=0))
    elif st.session_state.intent == "Report a city issue":
        st.markdown("### 🛠️ Report an issue")
        st.selectbox("Issue Type", ["Pothole", "Streetlight Out", "Water Leak", "Other"])
        st.text_input("Issue Location")
        st.button("Submit Report")
        st.button("⬅️ Go Back", on_click=lambda: st.session_state.update(step=0))
    else:
        st.text_area("Please describe your issue")
        st.button("Send to City Clerk")
        st.button("⬅️ Go Back", on_click=lambda: st.session_state.update(step=0))

# Optional reset
st.sidebar.button("🔁 Restart", on_click=lambda: st.session_state.clear())
