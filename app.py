import os
import json
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI
from datetime import datetime

# Page Setup
st.set_page_config(page_title="Noir -Eclipse - Cyber Guardian AI", page_icon="⚡", layout="centered")

# --- SAFE API KEY LOADING ---
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Load Groq API Key
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key and "GROQ_API_KEY" in st.secrets:
    groq_api_key = st.secrets["GROQ_API_KEY"]

if not groq_api_key:
    st.error("🔑 Groq API Key missing! Add `GROQ_API_KEY` to your `.env` file or Streamlit Secrets.")
    st.stop()

groq_client = Groq(api_key=groq_api_key)

# Load Optional OpenAI API Key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key and "OPENAI_API_KEY" in st.secrets:
    openai_api_key = st.secrets["OPENAI_API_KEY"]

openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None

# --- MODEL SELECTION ROUTER ---
def resolve_model_execution(choice: str, prompt_text: str) -> tuple[str, str, str]:
    """
    Returns: (provider_name, model_id, model_description)
    """
    if choice == "⚡ Dynamic Auto-Router (Groq)":
        security_keywords = [
            "virus", "malware", "phishing", "hack", "security", "exploit", 
            "cyber", "code", "python", "script", "analyze", "threat", 
            "vulnerability", "firewall", "encrypt", "trojan", "ransomware"
        ]
        lowered = prompt_text.lower()
        if any(keyword in lowered for keyword in security_keywords) or len(prompt_text.split()) > 35:
            return "groq", "llama-3.3-70b-versatile", "🛡️ High-Intelligence Groq Sentinel (70B)"
        return "groq", "llama-3.1-8b-instant", "⚡ Fast Groq Assistant (8B)"
    
    elif choice == "Groq: Llama 3.3 70B":
        return "groq", "llama-3.3-70b-versatile", "🛡️ Groq Llama 3.3 (70B)"
    elif choice == "Groq: Llama 3.1 8B":
        return "groq", "llama-3.1-8b-instant", "⚡ Groq Llama 3.1 (8B)"
    elif choice == "OpenAI: GPT-4o Mini":
        return "openai", "gpt-4o-mini", "🧠 OpenAI GPT-4o Mini"
    elif choice == "OpenAI: GPT-4o":
        return "openai", "gpt-4o", "🔥 OpenAI GPT-4o (High Reasoning)"
    
    return "groq", "llama-3.1-8b-instant", "⚡ Default Groq Model"

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

# --- SIDEBAR: SETTINGS & MODEL SELECTION ---
with st.sidebar:
    st.header("⚙️ Noir -Eclipse Settings")
    
    # Model Provider Selector
    st.subheader("🤖 Model Selection")
    model_choice = st.selectbox(
        "Choose Engine",
        [
            "⚡ Dynamic Auto-Router (Groq)",
            "Groq: Llama 3.3 70B",
            "Groq: Llama 3.1 8B",
            "OpenAI: GPT-4o Mini",
            "OpenAI: GPT-4o"
        ]
    )

    # Cybersecurity Sentinel Toggle
    sec_mode = st.toggle("Cybersecurity & Anti-Virus Sentinel", value=True)
    
    # Translation Tool
    st.subheader("🌐 Translation Mode")
    target_lang = st.selectbox("Target Language", ["None (Standard AI)", "Spanish", "French", "German", "Chinese", "Hindi", "Japanese"])
    
    # Permission Manager for Web Launching
    st.subheader("🔓 Launch Permissions")
    allow_google = st.checkbox("Allow opening Google / Web Searches", value=True)
    allow_youtube = st.checkbox("Allow opening YouTube", value=False)
    custom_url = st.text_input("Custom Shortcut URL", placeholder="https://example.com")

    st.divider()

    # --- CHAT HISTORY LIBRARY ---
    st.header("📚 Chat Library")

    if "chat_library" not in st.session_state:
        st.session_state.chat_library = {}

    def get_system_prompt():
        instructions = (
            "You are Noir -Eclipse, an advanced Cyber Guardian & Personal AI Assistant. "
            "Your core priorities are: "
            "1. Warn users about cybersecurity threats, phishing attempts, suspicious URLs, malware indicators, and device virus risks. "
            "2. Assist with general tasks concisely and accurately. "
        )
        if sec_mode:
            instructions += "Actively analyze user queries for security risks, virus threats, and offer preventive security advice. "
        if target_lang != "None (Standard AI)":
            instructions += f"Translate your final response into {target_lang}. "
        return instructions

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]

    # New Chat Button
    if st.button("➕ Start New Chat", use_container_width=True):
        if len(st.session_state.messages) > 1:
            first_user_msg = next((m["content"] for m in st.session_state.messages if m["role"] == "user"), "Chat")
            chat_title = f"{first_user_msg[:18]}... ({datetime.now().strftime('%H:%M')})"
            st.session_state.chat_library[chat_title] = st.session_state.messages.copy()
        
        st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]
        st.rerun()

    # Saved Chat History Selector
    if st.session_state.chat_library:
        selected_chat = st.selectbox("Select History", list(st.session_state.chat_library.keys()))
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📖 Load", use_container_width=True):
                st.session_state.messages = st.session_state.chat_library[selected_chat].copy()
                st.rerun()
        with col2:
            if st.button("🗑️ Delete", use_container_width=True):
                del st.session_state.chat_library[selected_chat]
                st.rerun()

    # Export Chat Session
    if len(st.session_state.messages) > 1:
        chat_json = json.dumps(st.session_state.messages, indent=2)
        st.download_button(
            label="📥 Export Current Chat",
            data=chat_json,
            file_name=f"noir_eclipse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

# Sync System Prompt
st.session_state.messages[0] = {"role": "system", "content": get_system_prompt()}

# Display Active Chat History
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# --- VOICE INPUT SECTION ---
st.write("---")
audio_file = st.audio_input("🎙️ Speak to Noir -Eclipse")
prompt = None

if audio_file:
    transcription = groq_client.audio.transcriptions.create(
        file=(audio_file.name, audio_file.getvalue()),
        model="whisper-large-v3"
    )
    prompt = transcription.text

# Text Input Fallback
text_prompt = st.chat_input("Ask Noir -Eclipse or type a security query...")
if text_prompt:
    prompt = text_prompt

# --- PROCESSING USER INPUT WITH MULTI-MODEL ROUTING ---
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Determine Provider and Model ID
    provider, model_id, model_description = resolve_model_execution(model_choice, prompt)

    # Sanitize message payload
    cleaned_messages = [
        {"role": m["role"], "content": str(m["content"])} 
        for m in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        st.caption(f"Engine: `{model_id}` | {model_description}")
        
        # Route to OpenAI API
        if provider == "openai":
            if not openai_client:
                st.error("🔑 OpenAI API key missing! Add `OPENAI_API_KEY` to your `.env` file or Streamlit Cloud Secrets.")
                st.stop()
            
            response = openai_client.chat.completions.create(
                model=model_id,
                messages=cleaned_messages,
                temperature=0.6,
            )
        # Route to Groq API
        else:
            response = groq_client.chat.completions.create(
                model=model_id,
                messages=cleaned_messages,
                temperature=0.6,
            )

        ai_reply = response.choices[0].message.content
        st.write(ai_reply)
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})

    # Trigger Authorized Launchers
    if allow_google and "search" in prompt.lower():
        st.link_button("🌐 Open Google Search", "https://www.google.com")
    if allow_youtube and "youtube" in prompt.lower():
        st.link_button("▶️ Open YouTube", "https://www.youtube.com")
    if custom_url and "open shortcut" in prompt.lower():
        st.link_button("🔗 Open Custom Allowed Site", custom_url)
