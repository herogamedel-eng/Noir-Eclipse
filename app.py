import os
import json
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime

# Page Setup
st.set_page_config(page_title="Noir -Eclipse OS", page_icon="⚡", layout="wide")

# Inject Custom High-Tech Blue & Cyan Cyber Styling (No Pink/Purple)
st.markdown("""
<style>
    /* Main Background Gradient - Deep Oceanic Charcoal */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #031326 0%, #050e1a 50%, #02070d 100%);
        color: #e2e8f0;
    }
    
    /* Vibrant Cyan & Electric Blue Gradient Header */
    .glow-title {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00f2fe, #0072ff, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(0, 242, 254, 0.3);
        margin-bottom: 0.1rem;
    }

    .glow-subtitle {
        color: #00f2fe;
        font-size: 1rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(0, 242, 254, 0.5);
    }

    /* Sidebar Glassmorphism & Glowing Cyan Borders */
    [data-testid="stSidebar"] {
        background: rgba(8, 20, 36, 0.85) !important;
        border-right: 1px solid rgba(0, 242, 254, 0.3) !important;
        box-shadow: 5px 0 25px rgba(0, 242, 254, 0.15) !important;
    }

    /* Custom Electric Cyan & Blue Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0072ff, #00f2fe) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 6px 20px rgba(0, 242, 254, 0.6) !important;
        background: linear-gradient(135deg, #00f2fe, #3b82f6) !important;
    }

    /* Tab Navigation Header Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px 10px 0px 0px;
        color: #a0aec0;
        font-weight: 700;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 0px 24px;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 114, 255, 0.25), rgba(0, 242, 254, 0.25)) !important;
        color: #ffffff !important;
        border-bottom: 3px solid #00f2fe !important;
        border-top: 1px solid rgba(0, 242, 254, 0.5) !important;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.4);
    }

    /* Cyan Metrics Card Containers */
    [data-testid="stMetric"] {
        background: rgba(10, 25, 45, 0.7);
        border: 1px solid rgba(0, 242, 254, 0.3);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 242, 254, 0.15);
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stMetricLabel"] {
        color: #00f2fe !important;
        font-weight: 700 !important;
        letter-spacing: 1px;
    }

    [data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-weight: 900 !important;
        text-shadow: 0 0 12px rgba(56, 189, 248, 0.6);
    }

    /* Glowing Select Boxes & Text Inputs */
    .stTextInput > div > div > input, .stSelectbox > div > div {
        background: rgba(10, 20, 35, 0.8) !important;
        color: #ffffff !important;
        border: 1px solid rgba(0, 242, 254, 0.4) !important;
        border-radius: 8px !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #00f2fe !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.6) !important;
    }

    /* Chat Messages Glass Panel */
    [data-testid="stChatMessage"] {
        background: rgba(10, 22, 40, 0.6) !important;
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

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
    st.markdown('<div class="glow-title" style="font-size: 2rem;">⚡ NOIR</div>', unsafe_allow_html=True)
    st.markdown('<div class="glow-subtitle">GENESIS AI OS</div>', unsafe_allow_html=True)
    
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
            label="Export JSON",
            data=chat_json,
            file_name=f"noir_eclipse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

# --- MAIN NAVIGATION TABS ---
tab_console, tab_ember = st.tabs(["💬 AI Console", "🔥 Ember Core"])

# ==========================================
# TAB 1: AI CONSOLE
# ==========================================
with tab_console:
    st.markdown('<div class="glow-title">💬 Assistant Console</div>', unsafe_allow_html=True)
    st.markdown('<div class="glow-subtitle">VOICE & TEXT INTERACTION ENGINE</div>', unsafe_allow_html=True)
    
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
# TAB 2: JARVIS HUD & EMBER CORE
# ==========================================
with tab_ember:
    st.markdown('<div class="glow-title">🔥 Ember Arc Reactor</div>', unsafe_allow_html=True)
    st.markdown('<div class="glow-subtitle">HOLOGRAPHIC JARVIS INTERFACE & TELEMETRY</div>', unsafe_allow_html=True)

    # Core Aspect Controls
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        core_scale = st.slider("CORE SCALE", 0.5, 2.0, 1.1, 0.1)
    with c2:
        ring_density = st.slider("ORBITAL RINGS", 2, 12, 6, 1)
    with c3:
        particle_count = st.slider("PARTICLE FLUX", 100, 500, 250, 50)
    with c4:
        theme_choice = st.selectbox("HUD THEME", ["Cyan Cyberpunk", "Emerald Matrix", "Neon Gold", "Red Alert"])

    theme_presets = {
        "Cyan Cyberpunk": {"primary": "#00f2fe", "secondary": "#4facfe", "hud": "#00f2fe"},
        "Emerald Matrix": {"primary": "#10b981", "secondary": "#34d399", "hud": "#059669"},
        "Neon Gold": {"primary": "#ffaa00", "secondary": "#ffd700", "hud": "#ffaa00"},
        "Red Alert": {"primary": "#f87171", "secondary": "#fb923c", "hud": "#ef4444"}
    }
    active_theme = theme_presets[theme_choice]

    jarvis_canvas_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; overflow: hidden; }}
            body {{
                background: #030812;
                font-family: 'Courier New', monospace;
                color: #e2e8f0;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 600px;
                border: 1px solid {active_theme["primary"]}55;
                border-radius: 16px;
                position: relative;
                box-shadow: 0 0 35px {active_theme["primary"]}22;
                user-select: none;
            }}
            #canvas-container {{ position: relative; width: 100%; height: 100%; cursor: crosshair; }}
            canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; }}
            
            /* HUD Overlays */
            .hud-header {{
                position: absolute; top: 20px; left: 25px;
                font-size: 12px; letter-spacing: 2px; color: {active_theme["hud"]};
                font-weight: bold; text-shadow: 0 0 10px {active_theme["hud"]};
            }}
            .hud-top-right {{
                position: absolute; top: 20px; right: 25px;
                font-size: 10px; letter-spacing: 2px; color: {active_theme["secondary"]};
                text-align: right; text-shadow: 0 0 8px {active_theme["secondary"]};
            }}
            .hud-bottom-left {{
                position: absolute; bottom: 25px; left: 25px;
            }}
            .hud-bottom-left .label {{ font-size: 9px; color: rgba(255, 255, 255, 0.5); letter-spacing: 2px; }}
            .hud-bottom-left .value {{ font-size: 32px; font-weight: 900; color: #ffffff; letter-spacing: 1px; text-shadow: 0 0 15px {active_theme["primary"]}; }}
            .hud-bottom-left .status {{ font-size: 11px; color: {active_theme["hud"]}; letter-spacing: 1.5px; font-weight: bold; }}
            
            .hud-bottom-right {{
                position: absolute; bottom: 25px; right: 25px; text-align: right;
                font-size: 10px; color: rgba(255, 255, 255, 0.5); letter-spacing: 1px;
            }}
        </style>
    </head>
    <body>
        <div id="canvas-container">
            <canvas id="jarvisCanvas"></canvas>

            <!-- HUD TELEMETRY OVERLAYS -->
            <div class="hud-header">ANALYSING DATA // REACTOR CORE</div>
            <div class="hud-top-right">
                SYSTEM CHECK: OK<br>
                SPECTRUM: ACTIVE<br>
                CONTAINMENT: 100%
            </div>
            <div class="hud-bottom-left">
                <div class="label">CORE INTEGRITY</div>
                <div class="value">89.18°C</div>
                <div class="status">CONTAINMENT STABLE // ONLINE</div>
            </div>
            <div class="hud-bottom-right">
                CORE SCALE: {core_scale}x<br>
                ORBITAL DENSITY: {ring_density} L<br>
                PARTICLE FLUX: {particle_count} P
            </div>
        </div>

        <script>
            const canvas = document.getElementById('jarvisCanvas');
            const ctx = canvas.getContext('2d');

            let width, height;
            function resize() {{
                width = canvas.width = canvas.offsetWidth;
                height = canvas.height = canvas.offsetHeight;
            }}
            resize();
            window.addEventListener('resize', resize);

            const scale = {core_scale};
            const rings = {ring_density};
            const numParticles = {particle_count};
            const primaryColor = "{active_theme["primary"]}";
            const secondaryColor = "{active_theme["secondary"]}";

            let rotationY = 0;
            let mouseX = 0, mouseY = 0;

            window.addEventListener('mousemove', (e) => {{
                const rect = canvas.getBoundingClientRect();
                mouseX = (e.clientX - rect.left - width / 2) * 0.0005;
                mouseY = (e.clientY - rect.top - height / 2) * 0.0005;
            }});

            // Particle Swarm Class
            class Particle {{
                constructor() {{
                    this.reset();
                }}
                reset() {{
                    this.theta = Math.random() * Math.PI * 2;
                    this.phi = Math.acos((Math.random() * 2) - 1);
                    this.radius = (100 + Math.random() * 140) * scale;
                    this.speed = (0.003 + Math.random() * 0.01) * (Math.random() < 0.5 ? 1 : -1);
                    this.size = Math.random() * 2.2 + 0.8;
                }}
                update() {{
                    this.theta += this.speed;
                }}
                draw(centerX, centerY) {{
                    const x = this.radius * Math.sin(this.phi) * Math.cos(this.theta + rotationY);
                    const y = this.radius * Math.cos(this.phi);
                    const z = this.radius * Math.sin(this.phi) * Math.sin(this.theta + rotationY);

                    const perspective = 400 / (400 + z);
                    const px = centerX + x * perspective;
                    const py = centerY + y * perspective;

                    ctx.save();
                    ctx.beginPath();
                    ctx.arc(px, py, this.size * perspective, 0, Math.PI * 2);
                    ctx.fillStyle = z > 0 ? primaryColor : secondaryColor;
                    ctx.globalAlpha = Math.max(0.15, (z + this.radius) / (2 * this.radius));
                    ctx.shadowBlur = 8;
                    ctx.shadowColor = primaryColor;
                    ctx.fill();
                    ctx.restore();
                }}
            }}

            const particles = Array.from({{ length: numParticles }}, () => new Particle());

            function draw() {{
                ctx.clearRect(0, 0, width, height);
                const centerX = width / 2;
                const centerY = height / 2;

                rotationY += 0.008 + mouseX;

                // --- 1. HUD TARGET GRID & RETICLES ---
                ctx.save();
                ctx.strokeStyle = primaryColor;
                ctx.globalAlpha = 0.2;
                ctx.lineWidth = 1;

                // Concentric HUD Circles
                for (let r = 80; r <= 280; r += 60) {{
                    ctx.beginPath();
                    ctx.arc(centerX, centerY, r * scale, 0, Math.PI * 2);
                    ctx.stroke();
                }}

                // Radial Tick Lines
                for (let a = 0; a < Math.PI * 2; a += Math.PI / 12) {{
                    ctx.beginPath();
                    ctx.moveTo(centerX + Math.cos(a) * 70 * scale, centerY + Math.sin(a) * 70 * scale);
                    ctx.lineTo(centerX + Math.cos(a) * 280 * scale, centerY + Math.sin(a) * 280 * scale);
                    ctx.stroke();
                }}
                ctx.restore();

                // --- 2. RADIATING LIGHT RAYS / BURST SPIKES ---
                ctx.save();
                ctx.strokeStyle = secondaryColor;
                ctx.lineWidth = 1.5;
                ctx.globalAlpha = 0.45;
                const rayCount = 16;
                for (let i = 0; i < rayCount; i++) {{
                    const rayAngle = (i * Math.PI * 2 / rayCount) + rotationY * 0.5;
                    const innerR = 30 * scale;
                    const outerR = (180 + Math.sin(rotationY * 3 + i) * 40) * scale;
                    ctx.beginPath();
                    ctx.moveTo(centerX + Math.cos(rayAngle) * innerR, centerY + Math.sin(rayAngle) * innerR);
                    ctx.lineTo(centerX + Math.cos(rayAngle) * outerR, centerY + Math.sin(rayAngle) * outerR);
                    ctx.stroke();
                }}
                ctx.restore();

                // --- 3. 3D ROTATING ORBITAL RINGS ---
                for (let i = 0; i < rings; i++) {{
                    ctx.save();
                    ctx.translate(centerX, centerY);
                    
                    const tiltX = (i * Math.PI / rings) + mouseY;
                    const tiltY = rotationY * (i % 2 === 0 ? 1 : -1);
                    
                    ctx.rotate(tiltX);
                    ctx.rotate(tiltY);

                    ctx.beginPath();
                    const rx = (110 + i * 18) * scale;
                    const ry = (40 + i * 12) * scale;
                    ctx.ellipse(0, 0, rx, ry, 0, 0, Math.PI * 2);
                    
                    ctx.strokeStyle = i % 2 === 0 ? primaryColor : secondaryColor;
                    ctx.globalAlpha = 0.6 + (i * 0.04);
                    ctx.lineWidth = 2.0;
                    ctx.shadowBlur = 12;
                    ctx.shadowColor = primaryColor;
                    ctx.stroke();
                    ctx.restore();
                }}

                // --- 4. PARTICLE SWARM SHELL ---
                particles.forEach(p => {{
                    p.update();
                    p.draw(centerX, centerY);
                }});

                // --- 5. GLOWING ARC REACTOR CORE ---
                ctx.save();
                const coreRadius = 40 * scale;

                // Outer Atmosphere Glow
                ctx.beginPath();
                ctx.arc(centerX, centerY, coreRadius + 30, 0, Math.PI * 2);
                const glowGradient = ctx.createRadialGradient(centerX, centerY, 5, centerX, centerY, coreRadius + 40);
                glowGradient.addColorStop(0, '#ffffff');
                glowGradient.addColorStop(0.3, secondaryColor);
                glowGradient.addColorStop(0.7, primaryColor);
                glowGradient.addColorStop(1, 'transparent');
                ctx.fillStyle = glowGradient;
                ctx.globalAlpha = 0.85;
                ctx.fill();

                // Solid Core Center
                ctx.beginPath();
                ctx.arc(centerX, centerY, coreRadius, 0, Math.PI * 2);
                ctx.fillStyle = "#ffffff";
                ctx.shadowBlur = 40;
                ctx.shadowColor = primaryColor;
                ctx.fill();
                ctx.restore();

                requestAnimationFrame(draw);
            }}

            draw();
        </script>
    </body>
    </html>
    """

    components.html(jarvis_canvas_html, height=620)

    # Telemetry metrics
    st.markdown("### ⚙️ JARVIS System Diagnostics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Core Temperature", "89.18 °C", "-0.4°C")
    m2.metric("Magnetic Shield", "4.8 Tesla", "100% Nominal")
    m3.metric("Neural Sync", "99.98%", "+0.02%")
    m4.metric("Reactor Output", "1.21 GW", "Stable")
