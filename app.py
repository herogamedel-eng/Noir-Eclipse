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

# --- MAIN NAVIGATION TABS ---
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
# TAB 2: JARVIS HUD & EMBER CORE
# ==========================================
with tab_ember:
    st.caption("PERSONAL VISUAL INTERFACE")
    st.title("Ember Arc Reactor Core")
    st.markdown("A live holographic visualizer featuring orbital particle shells, HUD telemetry, and dynamic containment controls.")

    # Core Aspects / Controls
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        core_scale = st.slider("CORE SCALE", 0.5, 2.0, 1.1, 0.1)
    with c2:
        ring_density = st.slider("ORBITAL RINGS", 2, 12, 6, 1)
    with c3:
        particle_count = st.slider("PARTICLE FLUX", 100, 500, 250, 50)
    with c4:
        theme_choice = st.selectbox("HUD THEME", ["Ember Gold", "Cyan HUD", "Plasma Purple", "Red Alert"])

    theme_presets = {
        "Ember Gold": {"primary": "#ff7700", "secondary": "#ffcc00", "bg_glow": "rgba(255, 119, 0, 0.15)"},
        "Cyan HUD": {"primary": "#00f2fe", "secondary": "#4facfe", "bg_glow": "rgba(0, 242, 254, 0.15)"},
        "Plasma Purple": {"primary": "#c084fc", "secondary": "#f472b6", "bg_glow": "rgba(192, 132, 252, 0.15)"},
        "Red Alert": {"primary": "#f87171", "secondary": "#fb923c", "bg_glow": "rgba(248, 113, 113, 0.15)"}
    }
    active_theme = theme_presets[theme_choice]

    jarvis_canvas_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; overflow: hidden; }}
            body {{
                background: #04060a;
                font-family: 'Courier New', monospace;
                color: #e2e8f0;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 600px;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 12px;
                position: relative;
                user-select: none;
            }}
            #canvas-container {{ position: relative; width: 100%; height: 100%; cursor: crosshair; }}
            canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; }}
            
            /* HUD Overlays */
            .hud-header {{
                position: absolute; top: 20px; left: 25px;
                font-size: 11px; letter-spacing: 2px; color: {active_theme["primary"]};
                font-weight: bold; text-shadow: 0 0 8px {active_theme["primary"]};
            }}
            .hud-top-right {{
                position: absolute; top: 20px; right: 25px;
                font-size: 10px; letter-spacing: 2px; color: rgba(255, 255, 255, 0.5);
                text-align: right;
            }}
            .hud-bottom-left {{
                position: absolute; bottom: 25px; left: 25px;
            }}
            .hud-bottom-left .label {{ font-size: 9px; color: rgba(255, 255, 255, 0.4); letter-spacing: 2px; }}
            .hud-bottom-left .value {{ font-size: 32px; font-weight: 900; color: #ffffff; letter-spacing: 1px; }}
            .hud-bottom-left .status {{ font-size: 11px; color: {active_theme["secondary"]}; letter-spacing: 1.5px; font-weight: bold; }}
            
            .hud-bottom-right {{
                position: absolute; bottom: 25px; right: 25px; text-align: right;
                font-size: 10px; color: rgba(255, 255, 255, 0.4); letter-spacing: 1px;
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
                    this.size = Math.random() * 2 + 0.8;
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
                    ctx.globalAlpha = Math.max(0.1, (z + this.radius) / (2 * this.radius));
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
                ctx.globalAlpha = 0.15;
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
                ctx.globalAlpha = 0.4;
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
                    ctx.globalAlpha = 0.5 + (i * 0.05);
                    ctx.lineWidth = 1.8;
                    ctx.shadowBlur = 10;
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
                ctx.shadowBlur = 35;
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
    st.subheader("⚙️ JARVIS System Diagnostics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Core Temperature", "89.18 °C", "-0.4°C")
    m2.metric("Magnetic Shield", "4.8 Tesla", "100% Nominal")
    m3.metric("Neural Sync", "99.98%", "+0.02%")
    m4.metric("Reactor Output", "1.21 GW", "Stable")
