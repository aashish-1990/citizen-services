# Enhanced Streamlit UI for LIA – Gov2Biz-style Multi-Service Chatbot with Avatars, Help, Real-Time Voice Input (WebRTC), and TTS
import streamlit as st
import streamlit.components.v1 as components
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import av
import numpy as np
import queue
import threading
import whisper

st.set_page_config(page_title="LIA – City Assistant", layout="centered")
st.image("https://cdn-icons-png.flaticon.com/512/4712/4712107.png", width=80)
st.title("🤖 Meet LIA – Your City of Kermit Assistant")

if "step" not in st.session_state:
    st.session_state.step = 0
if "intent" not in st.session_state:
    st.session_state.intent = None

st.markdown("""
<audio autoplay>
  <source src="https://github.com/audiojs/audiojs/raw/master/audio/hello-welcome-kermit.mp3" type="audio/mpeg">
  Your browser does not support the audio element.
</audio>
""", unsafe_allow_html=True)

components.html("""
<script>
window.onload = function() {
  const msg = new SpeechSynthesisUtterance("Hi there! I'm LIA, your assistant from the City of Kermit. How can I help you today?");
  const voices = window.speechSynthesis.getVoices();
  if (!voices.length) {
    setTimeout(() => speechSynthesis.speak(msg), 500);
  } else {
    msg.voice = voices.find(v => v.name.includes('Female')) || voices[0];
    msg.lang = 'en-US';
    msg.pitch = 1.2;
    msg.rate = 1;
    speechSynthesis.speak(msg);
  }
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

# Whisper transcription handler
result_queue = queue.Queue()
model = whisper.load_model("base")

class AudioProcessor:
    def __init__(self):
        self.buffer = queue.Queue()

    def recv(self, frame):
        audio = frame.to_ndarray()
        audio = audio.mean(axis=1).astype(np.int16)  # Mono
        self.buffer.put(audio)
        return av.AudioFrame.from_ndarray(audio, layout="mono")

    def transcribe_background(self):
        while True:
            audio_chunk = []
            while not self.buffer.empty():
                audio_chunk.extend(self.buffer.get())
            if audio_chunk:
                try:
                    audio_np = np.array(audio_chunk, dtype=np.float32) / 32768.0
                    result = model.transcribe(audio_np, language='en')
                    result_queue.put(result['text'])
                except Exception as e:
                    result_queue.put(f"[ERROR] {e}")
            else:
                result_queue.put("")

ap = AudioProcessor()
th = threading.Thread(target=ap.transcribe_background, daemon=True)
th.start()

st.markdown("### 🎤 Speak to LIA")
webrtc_streamer(key="mic", mode=WebRtcMode.SENDONLY, client_settings=ClientSettings(media_stream_constraints={"audio": True, "video": False}), audio_processor_factory=lambda: ap)

if not result_queue.empty():
    transcript = result_queue.get()
    if transcript:
        st.success(f"You said: {transcript}")
        if "bill" in transcript.lower():
            st.session_state.intent = "Pay a utility bill"
            st.session_state.step = 1
        elif "ticket" in transcript.lower():
            st.session_state.intent = "Pay a ticket"
            st.session_state.step = 1
        elif "permit" in transcript.lower():
            st.session_state.intent = "Apply for a permit"
            st.session_state.step = 1
        elif "report" in transcript.lower() or "issue" in transcript.lower():
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

# Optional reset
st.sidebar.button("🔁 Restart", on_click=lambda: st.session_state.clear())
