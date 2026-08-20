import os
import json
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime

# Page Setup
st.set_page_config(page_title="Noir -Eclipse AI", page_icon="⚡", layout="wide")

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

# --- AUTOMATIC SESSION INITIALIZATION ---
if "chat_library" not in st.session_state:
    st.session_state.chat_library = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = f"New Chat ({datetime.now().strftime('%H:%M:%S')})"
    st.session_state.messages = []

# --- SYSTEM PROMPT HELPER ---
def get_system_prompt(target_lang: str) -> str:
    instructions = (
        "You are Noir -Eclipse, an advanced Personal AI Assistant. "
        "Assist with general tasks, answering questions accurately and concisely."
    )
    if target_lang != "English":
        instructions += f" Translate your final response into {target_lang}."
    else:
        instructions += " Always respond in English."
    return instructions

# --- SIDEBAR: SETTINGS & LIBRARY ---
with st.sidebar:
    st.title("⚡ Noir -Eclipse OS")
    st.caption("GENESIS - PERSONAL AI OS")
    
    st.header("⚙️ Settings")
    model_choice = st.selectbox(
        "Choose Groq Model",
        ["⚡ Dynamic Auto-Router", "Llama 3.3 70B (High Intelligence)", "Llama 3.1 8B (Fast Response)"]
    )
    
    target_lang = st.selectbox(
        "Target Language", 
        ["English", "Spanish", "French", "German", "Chinese", "Hindi", "Japanese"],
        index=0
    )

    st.divider()

    # --- SIDEBAR LIBRARY ---
    st.header("📚 Library")

    if st.button("➕ Start New Chat", use_container_width=True):
        if len(st.session_state.messages) > 1:
            st.session_state.chat_library[st.session_state.current_chat_id] = st.session_state.messages.copy()
        
        st.session_state.current_chat_id = f"New Chat ({datetime.now().strftime('%H:%M:%S')})"
        st.session_state.messages = []
        st.rerun()

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

# --- MAIN NAVIGATION TABS IN WEBSITE ---
tab_console, tab_ember = st.tabs(["💬 AI Console", "🔥 Ember Core"])

# ==========================================
# TAB 1: AI CONSOLE
# ==========================================
with tab_console:
    st.title("💬 Assistant Console")
    
    sys_prompt = get_system_prompt(target_lang)
    if len(st.session_state.messages) == 0:
        st.session_state.messages = [{"role": "system", "content": sys_prompt}]
    else:
        st.session_state.messages[0] = {"role": "system", "content": sys_prompt}

    # Display Chat History
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

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

    if prompt:
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

        st.session_state.chat_library[st.session_state.current_chat_id] = st.session_state.messages.copy()

# ==========================================
# TAB 2: EMBER CORE (VISUAL CONTAINMENT INTERFACE)
# ==========================================
with tab_ember:
    st.caption("PERSONAL VISUAL INTERFACE")
    st.title("Ember Core")
    st.markdown("A live, editable containment visualizer. Its field expands while you speak and settles back into containment when the room is quiet.")

    # Control Parameters (Aspects)
    col_aspect1, col_aspect2, col_aspect3, col_aspect4 = st.columns(4)
    
    with col_aspect1:
        core_scale = st.slider("CORE SCALE", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
    with col_aspect2:
        ring_density = st.slider("RING DENSITY", min_value=1, max_value=6, value=3, step=1)
    with col_aspect3:
        energy_profile = st.selectbox("ENERGY PROFILE", ["Amber Flame", "Plasma Core", "Quantum Void", "Overdrive"])
    with col_aspect4:
        core_status = st.selectbox("CONTAINMENT MODE", ["ONLINE", "STANDBY", "CONTAINMENT LOCK", "OVERLOAD"])

    # Color mapping for Energy Profile
    color_map = {
        "Amber Flame": {"primary": "#ff5500", "secondary": "#ffaa00", "glow": "rgba(255, 85, 0, 0.8)"},
        "Plasma Core": {"primary": "#00f2fe", "secondary": "#4facfe", "glow": "rgba(0, 242, 254, 0.8)"},
        "Quantum Void": {"primary": "#a855f7", "secondary": "#ec4899", "glow": "rgba(168, 85, 247, 0.8)"},
        "Overdrive": {"primary": "#ef4444", "secondary": "#f97316", "glow": "rgba(239, 68, 68, 0.9)"}
    }
    theme = color_map[energy_profile]

    # Dynamic HTML/Canvas Ember Visualizer
    ember_canvas_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; background: transparent; overflow: hidden; }}
            body {{
                background: #090a0f;
                font-family: 'Courier New', Courier, monospace;
                color: #e2e8f0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 500px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                position: relative;
            }}
            #container {{ position: relative; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; }}
            canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; }}
            
            .hud-top-right {{
                position: absolute; top: 15px; right: 20px;
                font-size: 11px; letter-spacing: 2px; color: rgba(255, 255, 255, 0.4);
                text-transform: uppercase;
            }}
            .hud-bottom-left {{
                position: absolute; bottom: 20px; left: 25px;
            }}
            .hud-bottom-left .title {{ font-size: 10px; color: rgba(255,255,255,0.4); letter-spacing: 2px; }}
            .hud-bottom-left .value {{ font-size: 28px; font-weight: bold; color: #ffffff; margin: 2px 0; }}
            .hud-bottom-left .sub {{ font-size: 11px; color: {theme["primary"]}; letter-spacing: 1px; font-weight: 600; }}
        </style>
    </head>
    <body>
        <div id="container">
            <canvas id="emberCanvas"></canvas>
            <div class="hud-top-right">E M B E R • C O N T A I N M E N T • I N T E R F A C E</div>
            <div class="hud-bottom-left">
                <div class="title">CORE INTEGRITY</div>
                <div class="value">100%</div>
                <div class="sub">{core_status} - CONTAINMENT STABLE</div>
            </div>
        </div>

        <script>
            const canvas = document.getElementById('emberCanvas');
            const ctx = canvas.getContext('2d');

            let width, height;
            function resize() {{
                width = canvas.width = canvas.offsetWidth;
                height = canvas.height = canvas.offsetHeight;
            }}
            resize();
            window.addEventListener('resize', resize);

            const scale = {core_scale};
            const ringsCount = {ring_density};
            const primaryColor = "{theme["primary"]}";
            const secondaryColor = "{theme["secondary"]}";
            const statusText = "{core_status}";

            let angleOffset = 0;

            function draw() {{
                ctx.clearRect(0, 0, width, height);
                const centerX = width / 2;
                const centerY = height / 2;
                
                angleOffset += 0.015;

                // --- 1. Draw Outer Orbital Containment Rings ---
                for (let i = 0; i < ringsCount; i++) {{
                    ctx.save();
                    ctx.translate(centerX, centerY);
                    
                    const ringAngle = angleOffset * (i % 2 === 0 ? 1 : -1) + (i * Math.PI / ringsCount);
                    ctx.rotate(ringAngle);
                    
                    ctx.beginPath();
                    const rx = (120 + i * 25) * scale;
                    const ry = (35 + i * 12) * scale;
                    ctx.ellipse(0, 0, rx, ry, i * 0.4, 0, Math.PI * 2);
                    ctx.strokeStyle = i === 0 ? primaryColor : secondaryColor;
                    ctx.globalAlpha = 0.4 + (i * 0.1);
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                    ctx.restore();
                }}

                // --- 2. Draw Ember Core Glow ---
                const coreRadius = 45 * scale;
                ctx.save();
                ctx.beginPath();
                ctx.arc(centerX, centerY, coreRadius + 20, 0, Math.PI * 2);
                const outerGlow = ctx.createRadialGradient(centerX, centerY, 5, centerX, centerY, coreRadius + 35);
                outerGlow.addColorStop(0, primaryColor);
                outerGlow.addColorStop(0.6, secondaryColor);
                outerGlow.addColorStop(1, 'transparent');
                ctx.fillStyle = outerGlow;
                ctx.globalAlpha = 0.8;
                ctx.fill();

                // Core Sphere
                ctx.beginPath();
                ctx.arc(centerX, centerY, coreRadius, 0, Math.PI * 2);
                const innerCore = ctx.createRadialGradient(centerX - 10, centerY - 10, 2, centerX, centerY, coreRadius);
                innerCore.addColorStop(0, '#ffffff');
                innerCore.addColorStop(0.3, secondaryColor);
                innerCore.addColorStop(1, primaryColor);
                ctx.fillStyle = innerCore;
                ctx.globalAlpha = 1.0;
                ctx.shadowBlur = 30;
                ctx.shadowColor = primaryColor;
                ctx.fill();
                ctx.restore();

                // --- 3. Center Status Text ---
                ctx.save();
                ctx.font = "900 11px Arial, sans-serif";
                ctx.fillStyle = "#ffffff";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.letterSpacing = "2px";
                ctx.fillText(statusText, centerX, centerY);
                ctx.restore();

                requestAnimationFrame(draw);
            }}

            draw();
        </script>
    </body>
    </html>
    """

    # Embed HTML Visualizer directly inside Streamlit Tab
    components.html(ember_canvas_html, height=520)

    # Telemetry and Quick Actions
    st.subheader("⚙️ Aspect Control Metrics")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Thermal Energy Output", "485 K", "+2.4%")
    m_col2.metric("Magnetic Field Flux", "1.24 Tesla", "Nominal")
    m_col3.metric("Containment Stability", "99.8%", "Stable")
    m_col4.metric("Voice Sensitivity", "Active", "Listening")
