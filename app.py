import os
import json
import base64
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime

# Page Setup
st.set_page_config(page_title="Noir -Eclipse AI", page_icon="⚡", layout="centered")

# --- INTERACTIVE EMBER CORE HTML/JS GENERATOR ---
HTML_EMBER_CORE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Noir -Eclipse // Interactive Energy Core</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; overflow: hidden; }
        body { background: #030712; color: #fff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        canvas { display: block; width: 100vw; height: 100vh; cursor: crosshair; }
        .ui-overlay {
            position: absolute; top: 20px; left: 20px; pointer-events: none;
            background: rgba(3, 7, 18, 0.6); padding: 15px 25px; border-radius: 12px;
            border: 1px solid rgba(0, 242, 254, 0.2); backdrop-filter: blur(10px);
        }
        .title { font-size: 1.2rem; font-weight: 700; letter-spacing: 2px; color: #00f2fe; text-shadow: 0 0 10px #00f2fe; }
        .subtitle { font-size: 0.8rem; color: #94a3b8; margin-top: 4px; }
    </style>
</head>
<body>
    <div class="ui-overlay">
        <div class="title">⚡ NOIR -ECLIPSE CORE</div>
        <div class="subtitle">Move cursor to distort magnetic field • Click to discharge shockwave</div>
    </div>
    <canvas id="coreCanvas"></canvas>

    <script>
        const canvas = document.getElementById('coreCanvas');
        const ctx = canvas.getContext('2d');

        let width = canvas.width = window.innerWidth;
        let height = canvas.height = window.innerHeight;

        window.addEventListener('resize', () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        });

        const mouse = { x: width / 2, y: height / 2, active: false };
        let shockwaves = [];

        window.addEventListener('mousemove', (e) => {
            mouse.x = e.clientX;
            mouse.y = e.clientY;
            mouse.active = true;
        });

        window.addEventListener('click', (e) => {
            shockwaves.push({
                x: e.clientX,
                y: e.clientY,
                radius: 10,
                maxRadius: 250,
                alpha: 1
            });
        });

        class Particle {
            constructor() {
                this.reset();
            }

            reset() {
                this.angle = Math.random() * Math.PI * 2;
                this.distance = 40 + Math.random() * 180;
                this.speed = (0.005 + Math.random() * 0.02) * (Math.random() < 0.5 ? 1 : -1);
                this.size = Math.random() * 3 + 1;
                this.color = Math.random() > 0.3 ? '#00f2fe' : '#ff4b4b';
                this.alpha = Math.random() * 0.8 + 0.2;
            }

            update(centerX, centerY) {
                this.angle += this.speed;
                
                let targetX = centerX + Math.cos(this.angle) * this.distance;
                let targetY = centerY + Math.sin(this.angle) * this.distance;

                if (mouse.active) {
                    const dx = mouse.x - targetX;
                    const dy = mouse.y - targetY;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 200) {
                        targetX += (dx / dist) * 30;
                        targetY += (dy / dist) * 30;
                    }
                }

                this.x = targetX;
                this.y = targetY;
            }

            draw() {
                ctx.save();
                ctx.globalAlpha = this.alpha;
                ctx.fillStyle = this.color;
                ctx.shadowBlur = 12;
                ctx.shadowColor = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }

        const particles = Array.from({ length: 180 }, () => new Particle());

        function animate() {
            ctx.fillStyle = 'rgba(3, 7, 18, 0.2)';
            ctx.fillRect(0, 0, width, height);

            const centerX = width / 2;
            const centerY = height / 2;

            // Draw Core Energy Pulse
            const time = Date.now() * 0.003;
            const corePulse = Math.sin(time) * 8 + 45;

            ctx.save();
            ctx.beginPath();
            ctx.arc(centerX, centerY, corePulse, 0, Math.PI * 2);
            const gradient = ctx.createRadialGradient(centerX, centerY, 5, centerX, centerY, corePulse + 30);
            gradient.addColorStop(0, '#ffffff');
            gradient.addColorStop(0.4, '#00f2fe');
            gradient.addColorStop(0.8, '#ff007f');
            gradient.addColorStop(1, 'transparent');
            ctx.fillStyle = gradient;
            ctx.shadowBlur = 40;
            ctx.shadowColor = '#00f2fe';
            ctx.fill();
            ctx.restore();

            // Update & Draw Particles
            particles.forEach(p => {
                p.update(centerX, centerY);
                p.draw();
            });

            // Shockwaves
            shockwaves.forEach((sw, index) => {
                sw.radius += 8;
                sw.alpha -= 0.02;

                ctx.save();
                ctx.beginPath();
                ctx.arc(sw.x, sw.y, sw.radius, 0, Math.PI * 2);
                ctx.strokeStyle = `rgba(0, 242, 254, ${sw.alpha})`;
                ctx.lineWidth = 3;
                ctx.shadowBlur = 15;
                ctx.shadowColor = '#00f2fe';
                ctx.stroke();
                ctx.restore();

                if (sw.alpha <= 0) shockwaves.splice(index, 1);
            });

            requestAnimationFrame(animate);
        }

        animate();
    </script>
</body>
</html>
"""

# Convert HTML string to Base64 Data URI
b64_core = base64.b64encode(HTML_EMBER_CORE.encode('utf-8')).decode('utf-8')
data_url_core = f"data:text/html;base64,{b64_core}"

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

# --- INTERACTIVE ENERGY CORE BRAIN (HEADER) ---
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
    .core-launch-btn {
        display: block; width: 100%; text-align: center; padding: 10px;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        color: #030712 !important; font-weight: 700; border-radius: 8px;
        text-decoration: none; box-shadow: 0 0 15px rgba(0,242,254,0.4);
        margin-bottom: 15px; transition: all 0.3s ease;
    }
    .core-launch-btn:hover {
        box-shadow: 0 0 25px rgba(0,242,254,0.8); transform: translateY(-2px);
    }
    </style>
    <div class="core-container"><div class="energy-core"></div></div>
""", unsafe_allow_html=True)

st.title("⚡ Noir -Eclipse")

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

# --- AUTOMATIC SESSION INITIALIZATION ---
if "chat_library" not in st.session_state:
    st.session_state.chat_library = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = f"New Chat ({datetime.now().strftime('%H:%M:%S')})"
    st.session_state.messages = []

# --- SIDEBAR: SETTINGS & AUTOMATED LIBRARY ---
with st.sidebar:
    # --- LAUNCH INTERACTIVE CORE BUTTON ---
    st.markdown(f'<a href="{data_url_core}" target="_blank" class="core-launch-btn">🔥 Launch Interactive Core (New Tab)</a>', unsafe_allow_html=True)
    
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

# System prompt binding
sys_prompt = get_system_prompt(target_lang)
if len(st.session_state.messages) == 0:
    st.session_state.messages = [{"role": "system", "content": sys_prompt}]
else:
    st.session_state.messages[0] = {"role": "system", "content": sys_prompt}

# Display Active Chat History
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

    # Auto-save after response
    st.session_state.chat_library[st.session_state.current_chat_id] = st.session_state.messages.copy()
