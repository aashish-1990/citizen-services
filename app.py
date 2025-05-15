# Enhanced Streamlit UI for LIA – Gov2Biz-style Multi-Service Chatbot with Avatars, Help, Voice Input, and TTS
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="LIA – City Assistant", layout="centered")
st.image("https://cdn-icons-png.flaticon.com/512/4712/4712107.png", width=80)
st.title("🤖 Meet LIA – Your City of Kermit Assistant")

if "step" not in st.session_state:
    st.session_state.step = 0
if "intent" not in st.session_state:
    st.session_state.intent = None

# TTS welcome voice (female)
st.markdown("""
<audio autoplay>
  <source src="https://github.com/audiojs/audiojs/raw/master/audio/hello-welcome-kermit.mp3" type="audio/mpeg">
  Your browser does not support the audio element.
</audio>
""", unsafe_allow_html=True)

# Custom welcome voice text using JS TTS
components.html("""
<script>
window.onload = function() {
  const msg = new SpeechSynthesisUtterance("Hi there! I'm LIA, your assistant from the City of Kermit. How can I help you today?");
  msg.voice = speechSynthesis.getVoices().find(voice => voice.name.includes('Google') && voice.name.includes('Female')) || speechSynthesis.getVoices()[0];
  msg.lang = 'en-US';
  msg.pitch = 1.2;
  msg.rate = 1;
  speechSynthesis.speak(msg);
};
</script>
""", height=0)

st.markdown("""<style>
.chat-bubble {
  background-color: #f1f1f1;
  padding: 15px;
  border-radius: 15px;
  margin: 10px 0;
  font-size: 16px;
}
</style>""", unsafe_allow_html=True)

# Voice recorder script
st.markdown("""
<script>
  let recognition;
  function startListening() {
    if (!('webkitSpeechRecognition' in window)) {
      alert("Your browser doesn't support voice recognition. Try using Chrome.");
      return;
    }
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";
    recognition.start();
    recognition.onresult = function(event) {
      const transcript = event.results[0][0].transcript;
      document.getElementById("voice_result").value = transcript;
      document.getElementById("submit_voice").click();
    };
  }
</script>
<button onclick="startListening()">🎤 Speak to LIA</button>
<br><input type="text" id="voice_result" style="display:none"/>
<button id="submit_voice" style="display:none" onclick="document.forms[0].submit();">Submit</button>
""", unsafe_allow_html=True)

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

# Optional reset
st.sidebar.button("🔁 Restart", on_click=lambda: st.session_state.clear())
