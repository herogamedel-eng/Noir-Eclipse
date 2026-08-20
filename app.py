import os
import json
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime

# Page Setup
st.set_page_config(page_title="Noir -Eclipse AI", page_icon="⚡", layout="centered")

# --- SAFE API KEY LOADING ---
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key and "GROQ_API_KEY" in st.secrets:
    groq_api_key = st.secrets["GROQ_API_KEY"]

if not groq_api_key:
    st.error("🔑 Groq API Key missing! Add `GROQ_API_KEY` to your `.env` file or Streamlit Cloud Secrets.")
    st.stop()

client = Groq(api_key=groq_api_key)

# --- GROQ MODEL ROUTER FUNCTION ---
def resolve_groq_model(choice: str, prompt_text: str) -> tuple[str, str]:
    if choice == "⚡ Dynamic Auto-Router":
        if len(prompt_text.split()) > 35 or "code" in prompt_text.lower() or "analyze" in prompt_text.lower():
            return "llama-3.3-70b-versatile", "🛡️ High-Intelligence Model (70B)"
        return "llama-3.1-8b-instant", "⚡ Ultra-Fast Assistant Model (8B)"
    elif choice == "Llama 3.3 70B (High Intelligence)":
        return "llama-3.3-70b-versatile", "🛡️ Groq Llama 3.3 (70B)"
    return "llama-3.1-8b-instant", "⚡ Groq Llama 3.1 (8B)"

# --- INTERACTIVE ENERGY CORE BRAIN (HTML/CSS) ---
st.markdown("""
    <style>
    .core-container { display: flex; justify-content: center; align-items: center; margin: 5px 0; }
    .energy-core {
        width: 85px; height: 85px; border-radius: 50%;
        background: radial-gradient(circle, #00f2fe 0%, #4facfe 50%, #000 100%);
        box-shadow: 0 0 20px #00f2fe, 0 0 40px #4facfe;
        animation: pulse 2s infinite ease-in-out;
    }
    @keyframes pulse {
        0% { transform: scale(0.92); box-shadow: 0 0 15px #00f2fe; }
        50% { transform: scale(1.08); box-shadow: 0 0 30px #00f2fe, 0 0 50px #4facfe; }
        100% { transform: scale(0.92); box-shadow: 0 0 15px #00f2fe; }
    }
    </style>
    <div class="core-container"><div class="energy-core"></div></div>
""", unsafe_allow_html=True)

st.title("⚡ Noir -Eclipse")

# Helper function for system prompt
def get_system_prompt(target_lang: str) -> str:
    instructions = (
        "You are Noir -Eclipse, an advanced Personal AI Assistant. "
        "Assist with general tasks, answering questions accurately and concisely."
    )
    if target_lang != "None (Standard AI)":
        instructions += f" Translate your final response into {target_lang}."
    return instructions

# --- AUTOMATIC SESSION INITIALIZATION ---
if "chat_library" not in st.session_state:
    st.session_state.chat_library = {}

# Start a fresh chat session whenever the site opens or reloads
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = f"New Chat ({datetime.now().strftime('%H:%M:%S')})"
    st.session_state.messages = []

# --- SIDEBAR: SETTINGS & AUTOMATED LIBRARY ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    model_choice = st.selectbox(
        "Choose Groq Model",
        ["⚡ Dynamic Auto-Router", "Llama 3.3 70B (High Intelligence)", "Llama 3.1 8B (Fast Response)"]
    )
    target_lang = st.selectbox(
        "Target Language", 
        ["None (Standard AI)", "Spanish", "French", "German", "Chinese", "Hindi", "Japanese"]
    )

    st.divider()

    # --- SIDEBAR LIBRARY ---
    st.header("📚 Library")

    # Button to force a new chat manually
    if st.button("➕ Start New Chat", use_container_width=True):
        # Save active conversation if it contains user messages
        if len(st.session_state.messages) > 1:
            st.session_state.chat_library[st.session_state.current_chat_id] = st.session_state.messages.copy()
        
        # Reset to new session
        st.session_state.current_chat_id = f"New Chat ({datetime.now().strftime('%H:%M:%S')})"
        st.session_state.messages = []
        st.rerun()

    # Saved Archives List
    if st.session_state.chat_library:
        st.subheader("🗂️ Auto-Saved Chats")
        selected_archive = st.selectbox("Select Previous Session", list(st.session_state.chat_library.keys()))
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("📖 Load", use_container_width=True):
                st.session_state.messages = st.session_state.chat_library[selected_archive].copy()
                st.session_state.current_chat_id = selected_archive
                st.rerun()
        with btn_col2:
            if st.button("🗑️ Delete", use_container_width=True):
                del st.session_state.chat_library[selected_archive]
                st.rerun()

    # Export active session
    if len(st.session_state.messages) > 1:
        st.subheader("📥 Export")
        chat_json = json.dumps(st.session_state.messages, indent=2)
        st.download_button(
            label="Export as JSON",
            data=chat_json,
            file_name=f"noir_eclipse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

# Initialize or update system prompt in active session
sys_prompt = get_system_prompt(target_lang)
if len(st.session_state.messages) == 0:
    st.session_state.messages = [{"role": "system", "content": sys_prompt}]
else:
    st.session_state.messages[0] = {"role": "system", "content": sys_prompt}

# Display Active Chat Messages
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Voice & Text Inputs
st.write("---")
audio_file = st.audio_input("🎙️ Voice Command")
prompt = None

if audio_file:
    transcription = client.audio.transcriptions.create(
        file=(audio_file.name, audio_file.getvalue()),
        model="whisper-large-v3"
    )
    prompt = transcription.text

text_prompt = st.chat_input("Ask Noir -Eclipse anything...")
if text_prompt:
    prompt = text_prompt

# Process User Query
if prompt:
    # Rename session title dynamically based on the first user message
    if len(st.session_state.messages) == 1:
        st.session_state.current_chat_id = f"{prompt[:18]}... ({datetime.now().strftime('%H:%M')})"

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    model_id, model_description = resolve_groq_model(model_choice, prompt)
    cleaned_messages = [{"role": m["role"], "content": str(m["content"])} for m in st.session_state.messages]

    with st.chat_message("assistant"):
        st.caption(f"Engine: `{model_id}` | {model_description}")
        response = client.chat.completions.create(
            model=model_id,
            messages=cleaned_messages,
            temperature=0.6,
        )
        ai_reply = response.choices[0].message.content
        st.write(ai_reply)
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})

    # --- AUTO-SAVE AFTER EVERY RESPONSE ---
    st.session_state.chat_library[st.session_state.current_chat_id] = st.session_state.messages.copy()
