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

# Inject Custom Cyan & Glass HUD Styling
st.markdown("""
<style>
    /* Main Background - Deep Glass OLED Obsidian */
    .stApp {
        background: radial-gradient(circle at 50% 20%, #030b14 0%, #01050a 60%, #000205 100%);
        color: #e2e8f0;
    }
    
    /* Vibrant Electric Cyan Title Header */
    .glow-title {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00f2fe, #0099ff, #00e5ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(0, 242, 254, 0.4);
        margin-bottom: 0.1rem;
    }

    .glow-subtitle {
        color: #00f2fe;
        font-size: 0.95rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(0, 242, 254, 0.5);
    }

    /* Sidebar Glassmorphism & Glowing Cyan Borders */
    [data-testid="stSidebar"] {
        background: rgba(4, 12, 22, 0.9) !important;
        border-right: 1px solid rgba(0, 242, 254, 0.25) !important;
        box-shadow: 5px 0 25px rgba(0, 242, 254, 0.1) !important;
    }

    /* Custom Cyan HUD Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0055ff, #00f2fe) !important;
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
        background: linear-gradient(135deg, #00f2fe, #0088ff) !important;
    }

    /* Tab Navigation Header Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 10px 10px 0px 0px;
        color: #94a3b8;
        font-weight: 700;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 0px 24px;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 150, 255, 0.2), rgba(0, 242, 254, 0.25)) !important;
        color: #ffffff !important;
        border-bottom: 3px solid #00f2fe !important;
        border-top: 1px solid rgba(0, 242, 254, 0.4) !important;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.3);
    }

    /* Cyan Metrics Containers */
    [data-testid="stMetric"] {
        background: rgba(5, 18, 32, 0.75);
        border: 1px solid rgba(0, 242, 254, 0.25);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 242, 254, 0.1);
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
        text-shadow: 0 0 12px rgba(56, 189, 248, 0.5);
    }

    /* Input Styling */
    .stTextInput > div > div > input, .stSelectbox > div > div {
        background: rgba(4, 15, 28, 0.8) !important;
        color: #ffffff !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        border-radius: 8px !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #00f2fe !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.5) !important;
    }

    /* Chat Panel */
    [data-testid="stChatMessage"] {
        background: rgba(6, 18, 32, 0.6) !important;
        border: 1px solid rgba(0, 242, 254, 0.15);
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- API KEY & CLIENT LOAD ---
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

# --- SESSION INITIALIZATION ---
if "chat_library" not in st.session_state:
    st.session_state.chat_library = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = f"New Chat ({datetime.now().strftime('%H:%M:%S')})"
    st.session_state.messages = []

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

# --- SIDEBAR NAVIGATION ---
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

    st.header("📚 Library")
    if st.button("➕ Start New Chat", use_container_width=True):
        if len(st.session_state.messages) > 1:
            st.session_state.chat_library[st.session_state.current_chat_id] = st.session_state.messages.copy()
        
        st.session_state.current_chat_id = f"New Chat ({datetime.now().strftime('%H:%M:%S')})"
        st.session_state.messages = []
        st.rerun()

    if st.session_state.chat_library:
        st.subheader("🗂️ Saved Sessions")
        selected_archive = st.selectbox("Select Session", list(st.session_state.chat_library.keys()))
        
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

# --- MAIN TABS ---
tab_console, tab_ember = st.tabs(["💬 AI Console", "🔥 JARVIS HUD Core"])

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
# TAB 2: TRANSPARENT GLASS JARVIS HUD
# ==========================================
with tab_ember:
    st.markdown('<div class="glow-title">⚡ J.A.R.V.I.S. HUD Core</div>', unsafe_allow_html=True)
    st.markdown('<div class="glow-subtitle">REAL-TIME HOLOGRAPHIC TRANSPARENT DISPLAY UI</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        core_scale = st.slider("RING RADIUS", 0.7, 1.5, 1.0, 0.05)
    with c2:
        rot_speed = st.slider("ROTATION SPEED", 0.5, 3.0, 1.2, 0.1)
    with c3:
        hud_theme = st.selectbox("HUD SPECTRUM", ["Cyan Arc", "Electric Blue", "Matrix Green", "Amber Glow"])

    color_maps = {
        "Cyan Arc": {"primary": "#00f2fe", "secondary": "#0099ff", "glow": "rgba(0, 242, 254, 0.8)"},
        "Electric Blue": {"primary": "#3b82f6", "secondary": "#60a5fa", "glow": "rgba(59, 130, 246, 0.8)"},
        "Matrix Green": {"primary": "#10b981", "secondary": "#34d399", "glow": "rgba(16, 185, 129, 0.8)"},
        "Amber Glow": {"primary": "#ffaa00", "secondary": "#ffd700", "glow": "rgba(255, 170, 0, 0.8)"}
    }
    active_colors = color_maps[hud_theme]

    transparent_hud_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; overflow: hidden; }}
            body {{
                background: #02060c;
                font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
                color: #e2e8f0;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 620px;
                border: 1px solid rgba(0, 242, 254, 0.25);
                border-radius: 16px;
                position: relative;
                box-shadow: inset 0 0 50px rgba(0, 0, 0, 0.8), 0 0 30px rgba(0, 242, 254, 0.15);
                user-select: none;
            }}
            #hud-container {{ position: relative; width: 100%; height: 100%; }}
            canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; }}
            
            /* Left side telemetry widgets like image */
            .left-widget-panel {{
                position: absolute;
                top: 40px;
                left: 35px;
                display: flex;
                flex-direction: column;
                gap: 18px;
                z-index: 10;
                width: 220px;
            }}
            .widget-box {{
                background: rgba(4, 15, 28, 0.5);
                border-left: 2px solid {active_colors["primary"]};
                padding: 10px 14px;
                border-radius: 0 8px 8px 0;
                backdrop-filter: blur(8px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            }}
            .widget-title {{
                font-size: 10px;
                letter-spacing: 1.5px;
                color: {active_colors["primary"]};
                font-weight: 700;
                text-transform: uppercase;
                margin-bottom: 4px;
            }}
            .widget-body {{
                font-size: 12px;
                color: #ffffff;
                font-weight: 600;
            }}
            .widget-sub {{
                font-size: 9px;
                color: #64748b;
            }}

            /* Bottom active status indicator matching image */
            .center-status-badge {{
                position: absolute;
                bottom: 50px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 4px;
                z-index: 10;
            }}
            .status-tag {{
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 12px;
                font-weight: 800;
                letter-spacing: 3px;
                color: {active_colors["primary"]};
                text-shadow: 0 0 10px {active_colors["primary"]};
            }}
            .status-dot {{
                width: 8px;
                height: 8px;
                background-color: {active_colors["primary"]};
                border-radius: 50%;
                box-shadow: 0 0 10px {active_colors["primary"]};
                animation: pulse 1.5s infinite;
            }}
            .status-subtext {{
                font-size: 9px;
                letter-spacing: 1px;
                color: rgba(255, 255, 255, 0.4);
            }}

            @keyframes pulse {{
                0% {{ opacity: 0.3; transform: scale(0.8); }}
                50% {{ opacity: 1; transform: scale(1.2); }}
                100% {{ opacity: 0.3; transform: scale(0.8); }}
            }}
        </style>
    </head>
    <body>
        <div id="hud-container">
            <canvas id="hudCanvas"></canvas>

            <!-- LEFT TELEMETRY WIDGETS (Matching photo visual elements) -->
            <div class="left-widget-panel">
                <div class="widget-box">
                    <div class="widget-title">AUDIO SYSTEM</div>
                    <div class="widget-body">Too Many Nights</div>
                    <div class="widget-sub">feat. Don Toliver...</div>
                </div>

                <div class="widget-box">
                    <div class="widget-title">SYSTEM METRICS</div>
                    <div class="widget-body">CPU: 24% | RAM: 58%</div>
                    <div class="widget-sub">CORE TEMP: 48°C</div>
                </div>

                <div class="widget-box">
                    <div class="widget-title">LINK STATUS</div>
                    <div class="widget-body">QUANTUM ENCRYPTION</div>
                    <div class="widget-sub">PING: 2ms // SECURE</div>
                </div>
            </div>

            <!-- CENTER STATUS DISPLAY -->
            <div class="center-status-badge">
                <div class="status-tag">
                    <div class="status-dot"></div>
                    ACTIVE
                </div>
                <div class="status-subtext">J.A.R.V.I.S. is online. Click status to disconnect.</div>
            </div>
        </div>

        <script>
            const canvas = document.getElementById('hudCanvas');
            const ctx = canvas.getContext('2d');

            let width, height;
            function resize() {{
                width = canvas.width = canvas.offsetWidth;
                height = canvas.height = canvas.offsetHeight;
            }}
            resize();
            window.addEventListener('resize', resize);

            const primary = "{active_colors["primary"]}";
            const secondary = "{active_colors["secondary"]}";
            const baseScale = {core_scale};
            const speed = {rot_speed};

            let angle = 0;
            let waveOffset = 0;

            function drawJARVISRing(cx, cy, radius) {{
                ctx.save();
                ctx.translate(cx, cy);

                // --- 1. OUTERMOST THIN GLOW RING ---
                ctx.beginPath();
                ctx.arc(0, 0, radius * 1.35, 0, Math.PI * 2);
                ctx.strokeStyle = primary;
                ctx.globalAlpha = 0.3;
                ctx.lineWidth = 1.5;
                ctx.stroke();

                // --- 2. SEGMENTED DASHED RING ---
                ctx.save();
                ctx.rotate(angle * 0.4);
                ctx.beginPath();
                ctx.arc(0, 0, radius * 1.22, 0, Math.PI * 2);
                ctx.strokeStyle = primary;
                ctx.globalAlpha = 0.8;
                ctx.lineWidth = 4;
                ctx.setLineDash([12, 18, 4, 18]);
                ctx.shadowBlur = 12;
                ctx.shadowColor = primary;
                ctx.stroke();
                ctx.restore();

                // --- 3. INNER RADIAL TICK MARKS (Identical to J.A.R.V.I.S image) ---
                ctx.save();
                ctx.rotate(-angle * 0.6);
                const ticks = 60;
                for (let i = 0; i < ticks; i++) {{
                    const a = (i * Math.PI * 2) / ticks;
                    const innerR = radius * 0.92;
                    const outerR = (i % 5 === 0) ? radius * 1.08 : radius * 1.02;
                    
                    ctx.beginPath();
                    ctx.moveTo(Math.cos(a) * innerR, Math.sin(a) * innerR);
                    ctx.lineTo(Math.cos(a) * outerR, Math.sin(a) * outerR);
                    ctx.strokeStyle = (i % 5 === 0) ? primary : secondary;
                    ctx.lineWidth = (i % 5 === 0) ? 2.5 : 1;
                    ctx.globalAlpha = (i % 5 === 0) ? 0.9 : 0.4;
                    ctx.stroke();
                }}
                ctx.restore();

                // --- 4. SOLID INNER DOUBLE RINGS ---
                ctx.beginPath();
                ctx.arc(0, 0, radius * 0.88, 0, Math.PI * 2);
                ctx.strokeStyle = primary;
                ctx.lineWidth = 3;
                ctx.globalAlpha = 0.95;
                ctx.shadowBlur = 15;
                ctx.shadowColor = primary;
                ctx.stroke();

                ctx.beginPath();
                ctx.arc(0, 0, radius * 0.82, 0, Math.PI * 2);
                ctx.strokeStyle = secondary;
                ctx.lineWidth = 1;
                ctx.globalAlpha = 0.5;
                ctx.stroke();

                // --- 5. CENTER "J.A.R.V.I.S." TEXT ---
                ctx.font = `900 ${{Math.round(26 * baseScale)}}px 'Segoe UI', sans-serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillStyle = '#ffffff';
                ctx.shadowBlur = 15;
                ctx.shadowColor = primary;
                ctx.fillText('J.A.R.V.I.S.', 0, 0);

                ctx.restore();
            }}

            // Draw Bottom Left Oscilloscope Waveform from image
            function drawWaveform() {{
                ctx.save();
                ctx.beginPath();
                const startX = 35;
                const startY = height - 70;
                const waveWidth = 180;

                ctx.moveTo(startX, startY);
                for (let x = 0; x < waveWidth; x += 4) {{
                    const y = startY + Math.sin((x * 0.1) + waveOffset) * 12 * Math.cos((x * 0.05) + waveOffset);
                    ctx.lineTo(startX + x, y);
                }}

                ctx.strokeStyle = primary;
                ctx.lineWidth = 2;
                ctx.shadowBlur = 10;
                ctx.shadowColor = primary;
                ctx.globalAlpha = 0.8;
                ctx.stroke();
                ctx.restore();
            }}

            function render() {{
                ctx.clearRect(0, 0, width, height);

                angle += 0.01 * speed;
                waveOffset += 0.08;

                const centerX = width / 2;
                const centerY = height / 2 - 20;
                const radius = 110 * baseScale;

                // Center Hologram Core Ring
                drawJARVISRing(centerX, centerY, radius);

                // Waveform graph at bottom left
                drawWaveform();

                requestAnimationFrame(render);
            }}

            render();
        </script>
    </body>
    </html>
    """

    components.html(transparent_hud_html, height=640)

    # Telemetry metrics
    st.markdown("### ⚙️ JARVIS System Diagnostics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Core Temperature", "48.00 °C", "-0.2°C")
    m2.metric("Neural Link", "99.98%", "+0.01%")
    m3.metric("Quantum Sync", "4.8 GHz", "Nominal")
    m4.metric("Reactor Output", "1.21 GW", "Stable")
