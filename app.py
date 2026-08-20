import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Page Setup
st.set_page_config(page_title="Noir -Eclipse - Cyber Guardian AI", page_icon="⚡", layout="centered")

# --- SAFE API KEY LOADING ---
# Load local .env if present
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Check both .env environment variables and Streamlit Cloud Secrets
api_key = os.getenv("GROQ_API_KEY")
if not api_key and "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]

# Halt gracefully if key is missing instead of crashing with a traceback error
if not api_key:
    st.error("🔑 Groq API Key missing! Please add `GROQ_API_KEY=gsk_your_key` to your `.env` file or Streamlit Cloud Secrets.")
    st.stop()

# Initialize Groq client with resolved API key
client = Groq(api_key=api_key)

# --- INTERACTIVE ENERGY CORE BRAIN (HTML/CSS) ---
st.markdown("""
    <style>
    .core-container { display: flex; justify-content: center; align-items: center; margin: 10px 0; }
    .energy-core {
        width: 95px; height: 95px; border-radius: 50%;
        background: radial-gradient(circle, #00f2fe 0%, #4facfe 50%, #000 100%);
        box-shadow: 0 0 25px #00f2fe, 0 0 50px #4facfe;
        animation: pulse 2s infinite ease-in-out;
    }
    @keyframes pulse {
        0% { transform: scale(0.92); box-shadow: 0 0 15px #00f2fe; }
        50% { transform: scale(1.08); box-shadow: 0 0 35px #00f2fe, 0 0 65px #4facfe; }
        100% { transform: scale(0.92); box-shadow: 0 0 15px #00f2fe; }
    }
    </style>
    <div class="core-container"><div class="energy-core"></div></div>
""", unsafe_allow_html=True)

st.title("⚡ Noir -Eclipse")

# --- SIDEBAR: PERMISSIONS & TRANSLATOR CONTROL ---
with st.sidebar:
    st.header("⚙️ Noir -Eclipse Permissions")
    
    # Cybersecurity Sentinel Toggle
    sec_mode = st.toggle("Cybersecurity & Anti-Virus Sentinel", value=True)
    
    # Translation Tool
    st.subheader("🌐 Translation Mode")
    target_lang = st.selectbox("Target Language", ["None (Standard AI)", "Spanish", "French", "German", "Chinese", "Hindi", "Japanese"])
    
    # Permission Manager for Web/App Launching
    st.subheader("🔓 Launch Permissions")
    allow_google = st.checkbox("Allow opening Google / Web Searches", value=True)
    allow_youtube = st.checkbox("Allow opening YouTube", value=False)
    custom_url = st.text_input("Custom Shortcut URL", placeholder="https://example.com")

# --- SYSTEM PROMPT GENERATOR ---
system_instructions = (
    "You are Noir -Eclipse, an advanced Cyber Guardian & Personal AI Assistant. "
    "Your core priorities are: "
    "1. Warn users about cybersecurity threats, phishing attempts, suspicious URLs, malware indicators, and device virus risks. "
    "2. Assist with general tasks concisely and accurately. "
)
if sec_mode:
    system_instructions += "Actively analyze user queries for security risks, virus threats, and offer preventive security advice. "
if target_lang != "None (Standard AI)":
    system_instructions += f"Translate your final response into {target_lang}. "

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_instructions}]

# Display Chat History
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# --- VOICE INPUT SECTION ---
st.write("---")
audio_file = st.audio_input("🎙️ Speak to Noir -Eclipse")
prompt = None

if audio_file:
    # Transcribe audio using Groq Whisper model
    transcription = client.audio.transcriptions.create(
        file=(audio_file.name, audio_file.read()),
        model="whisper-large-v3"
    )
    prompt = transcription.text

# Text Input Fallback
text_prompt = st.chat_input("Ask Noir -Eclipse or type a security query...")
if text_prompt:
    prompt = text_prompt

# --- PROCESSING USER INPUT ---
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Process AI Response
    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=st.session_state.messages,
            temperature=0.6,
        )
        ai_reply = response.choices[0].message.content
        st.write(ai_reply)
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})

    # Trigger Authorized Web Launchers
    if allow_google and "search" in prompt.lower():
        st.link_button("🌐 Open Google Search", "https://www.google.com")
    if allow_youtube and "youtube" in prompt.lower():
        st.link_button("▶️ Open YouTube", "https://www.youtube.com")
    if custom_url and "open shortcut" in prompt.lower():
        st.link_button("🔗 Open Custom Allowed Site", custom_url)
