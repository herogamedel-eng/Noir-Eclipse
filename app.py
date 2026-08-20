import os
import json
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime

# Page Setup
st.set_page_config(page_title="Noir -Eclipse - Cyber Guardian AI", page_icon="⚡", layout="wide")

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
        security_keywords = [
            "virus", "malware", "phishing", "hack", "security", "exploit", 
            "cyber", "code", "python", "script", "analyze", "threat", 
            "vulnerability", "firewall", "encrypt", "trojan", "ransomware"
        ]
        lowered = prompt_text.lower()
        if any(keyword in lowered for keyword in security_keywords) or len(prompt_text.split()) > 35:
            return "llama-3.3-70b-versatile", "🛡️ High-Intelligence Sentinel Model (70B)"
        return "llama-3.1-8b-instant", "⚡ Ultra-Fast Assistant Model (8B)"
    elif choice == "Llama 3.3 70B (High Intelligence)":
        return "llama-3.3-70b-versatile", "🛡️ Groq Llama 3.3 (70B)"
    return "llama-3.1-8b-instant", "⚡ Groq Llama 3.1 (8B)"

# --- INTERACTIVE ENERGY CORE BRAIN (HTML/CSS) ---
st.markdown("""
    <style>
    .core-container { display: flex; justify-content: center; align-items: center; margin: 5px 0; }
    .energy-core {
        width: 80px; height: 80px; border-radius: 50%;
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

# --- SIDEBAR: SETTINGS & CONTROLS ---
with st.sidebar:
    st.header("⚙️ Noir -Eclipse Controls")
    
    model_choice = st.selectbox(
        "Choose Groq Model",
        ["⚡ Dynamic Auto-Router", "Llama 3.3 70B (High Intelligence)", "Llama 3.1 8B (Fast Response)"]
    )
    sec_mode = st.toggle("Cybersecurity & Anti-Virus Sentinel", value=True)
    target_lang = st.selectbox("Target Language", ["None (Standard AI)", "Spanish", "French", "German", "Chinese", "Hindi", "Japanese"])
    
    st.subheader("🔓 Launch Permissions")
    allow_google = st.checkbox("Allow opening Google / Web Searches", value=True)
    allow_youtube = st.checkbox("Allow opening YouTube", value=False)
    custom_url = st.text_input("Custom Shortcut URL", placeholder="https://example.com")

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
if "chat_library" not in st.session_state:
    st.session_state.chat_library = {}

st.session_state.messages[0] = {"role": "system", "content": get_system_prompt()}

# --- MAIN INTERFACE: WORKSPACE & CENTRAL LIBRARY TABS ---
chat_tab, library_tab = st.tabs(["💬 Assistant Console", "📚 Central Library"])

# --- TAB 1: ASSISTANT CONSOLE ---
with chat_tab:
    # Display Active Chat History
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # Voice & Text Inputs
    audio_file = st.audio_input("🎙️ Voice Command")
    prompt = None

    if audio_file:
        transcription = client.audio.transcriptions.create(
            file=(audio_file.name, audio_file.getvalue()),
            model="whisper-large-v3"
        )
        prompt = transcription.text

    text_prompt = st.chat_input("Ask Noir -Eclipse or type a security query...")
    if text_prompt:
        prompt = text_prompt

    if prompt:
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

        if allow_google and "search" in prompt.lower():
            st.link_button("🌐 Open Google Search", "https://www.google.com")
        if allow_youtube and "youtube" in prompt.lower():
            st.link_button("▶️ Open YouTube", "https://www.youtube.com")
        if custom_url and "open shortcut" in prompt.lower():
            st.link_button("🔗 Open Custom Allowed Site", custom_url)

# --- TAB 2: CENTRAL LIBRARY ---
with library_tab:
    st.header("📚 Noir -Eclipse Central Library")
    lib_col1, lib_col2 = st.columns([1, 1])

    with lib_col1:
        st.subheader("💾 Chat Archives")
        
        # Save Current Session
        if st.button("💾 Save Current Session to Library", use_container_width=True):
            if len(st.session_state.messages) > 1:
                first_msg = next((m["content"] for m in st.session_state.messages if m["role"] == "user"), "Session")
                title = f"{first_msg[:20]}... ({datetime.now().strftime('%H:%M - %b %d')})"
                st.session_state.chat_library[title] = st.session_state.messages.copy()
                st.success(f"Saved: '{title}'")
            else:
                st.warning("No conversation to save yet.")

        # Load / Delete Saved Sessions
        if st.session_state.chat_library:
            selected_archive = st.selectbox("Saved Archives", list(st.session_state.chat_library.keys()))
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("📖 Load Session", use_container_width=True):
                    st.session_state.messages = st.session_state.chat_library[selected_archive].copy()
                    st.success("Session loaded! Switch to Assistant Console tab.")
            with btn_col2:
                if st.button("🗑️ Delete Archive", use_container_width=True):
                    del st.session_state.chat_library[selected_archive]
                    st.rerun()

        # Export JSON
        if len(st.session_state.messages) > 1:
            chat_json = json.dumps(st.session_state.messages, indent=2)
            st.download_button(
                label="📥 Export Session as JSON File",
                data=chat_json,
                file_name=f"noir_eclipse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

    with lib_col2:
        st.subheader("🛡️ Security Intelligence & Threat Vault")
        
        with st.expander("🚨 Trojan & Malware First-Response Checklist"):
            st.markdown("""
            1. **Isolate Device**: Disconnect Wi-Fi and Ethernet immediately.
            2. **Safe Mode**: Boot Windows in Safe Mode with Networking disabled.
            3. **Process Audit**: Open Task Manager (`Ctrl+Shift+Esc`) and terminate unrecognized processes using high CPU/RAM.
            4. **Offline Scan**: Execute a full scan using Windows Defender Offline or a trusted scanner.
            """)

        with st.expander("🎣 Phishing & Malicious URL Indicators"):
            st.markdown("""
            * **Domain Spoofing**: Check for subtle typos (e.g., `micros0ft.com` or `paypaI.com`).
            * **Unsolicited Attachments**: Avoid opening `.iso`, `.vbs`, `.exe`, or macro-enabled `.docm` files.
            * **Urgency Signals**: Be wary of demands for immediate password resets or payment verification.
            """)

    st.divider()
    st.subheader("⚡ Quick Security Commands")
    
    cmd_col1, cmd_col2, cmd_col3 = st.columns(3)
    with cmd_col1:
        if st.button("🔍 Scan for Ransomware Risks", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Explain how to protect my system against ransomware attacks and identify common vulnerability points."})
            st.info("Query queued. Switch to Assistant Console tab to view response.")
    with cmd_col2:
        if st.button("🛡️ Password Safety Audit", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "What are the essential criteria for high-entropy secure passwords and two-factor authentication?"})
            st.info("Query queued. Switch to Assistant Console tab to view response.")
    with cmd_col3:
        if st.button("🌐 Check Browser Security", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Provide a step-by-step checklist to harden my web browser against malicious tracking and drive-by downloads."})
            st.info("Query queued. Switch to Assistant Console tab to view response.")
