import os
import json
import calendar
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime

# Page Setup
st.set_page_config(page_title="Noir -Eclipse OS", page_icon="⚡", layout="wide")

# Inject Custom High-Tech Cyan Glassmorphism Styling
st.markdown("""
<style>
    /* Main Background - Deep Glass OLED Obsidian */
    .stApp {
        background: radial-gradient(circle at 50% 20%, #031326 0%, #050e1a 60%, #02070d 100%);
        color: #e2e8f0;
    }
    
    /* Vibrant Electric Cyan Title Header */
    .glow-title {
        font-size: 2.6rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00f2fe, #0099ff, #00e5ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(0, 242, 254, 0.4);
        margin-bottom: 0.1rem;
    }

    .glow-subtitle {
        color: #00f2fe;
        font-size: 0.9rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 1.2rem;
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

    /* Card Panels & Containers */
    .widget-panel {
        background: rgba(5, 18, 32, 0.75);
        border: 1px solid rgba(0, 242, 254, 0.25);
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 20px rgba(0, 242, 254, 0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 15px;
    }

    /* Metrics Styling */
    [data-testid="stMetric"] {
        background: rgba(5, 18, 32, 0.75);
        border: 1px solid rgba(0, 242, 254, 0.25);
        padding: 12px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.1);
    }
    [data-testid="stMetricLabel"] { color: #00f2fe !important; font-weight: 700 !important; }
    [data-testid="stMetricValue"] { color: #38bdf8 !important; font-weight: 900 !important; }

    /* Inputs */
    .stTextInput > div > div > input, .stSelectbox > div > div, .stTextArea > div > div > textarea {
        background: rgba(4, 15, 28, 0.8) !important;
        color: #ffffff !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        border-radius: 8px !important;
    }

    [data-testid="stChatMessage"] {
        background: rgba(6, 18, 32, 0.6) !important;
        border: 1px solid rgba(0, 242, 254, 0.15);
        border-radius: 12px;
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

# --- GROQ MODEL ROUTER ---
def resolve_groq_model(choice: str, prompt_text: str) -> tuple[str, str]:
    if choice == "⚡ Dynamic Auto-Router":
        if len(prompt_text.split()) > 35 or "code" in prompt_text.lower() or "analyze" in prompt_text.lower():
            return "llama-3.3-70b-versatile", "🛡️ High-Intelligence Model (70B)"
        return "llama-3.1-8b-instant", "⚡ Ultra-Fast Assistant Model (8B)"
    elif choice == "Llama 3.3 70B (High Intelligence)":
        return "llama-3.3-70b-versatile", "🛡️ Groq Llama 3.3 (70B)"
    return "llama-3.1-8b-instant", "⚡ Groq Llama 3.1 (8B)"

# --- SESSION STATES ---
if "chat_library" not in st.session_state:
    st.session_state.chat_library = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = f"New Chat ({datetime.now().strftime('%H:%M:%S')})"
    st.session_state.messages = []

if "calc_expr" not in st.session_state:
    st.session_state.calc_expr = ""

if "todo_list" not in st.session_state:
    st.session_state.todo_list = ["System Diagnostic Check", "Review Neural Link Parameters"]

def get_system_prompt(target_lang: str) -> str:
    instructions = "You are Noir -Eclipse, an advanced Personal AI Assistant. Respond accurately and concisely."
    if target_lang != "English":
        instructions += f" Translate your final response into {target_lang}."
    return instructions

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<div class="glow-title" style="font-size: 1.8rem;">⚡ NOIR</div>', unsafe_allow_html=True)
    st.markdown('<div class="glow-subtitle">GENESIS AI OS</div>', unsafe_allow_html=True)
    
    st.header("⚙️ Settings")
    model_choice = st.selectbox("Groq Model", ["⚡ Dynamic Auto-Router", "Llama 3.3 70B (High Intelligence)", "Llama 3.1 8B (Fast Response)"])
    target_lang = st.selectbox("Language", ["English", "Spanish", "French", "German", "Chinese", "Hindi", "Japanese"], index=0)

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
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("📖 Load", use_container_width=True):
                st.session_state.messages = st.session_state.chat_library[selected_archive].copy()
                st.session_state.current_chat_id = selected_archive
                st.rerun()
        with btn_c2:
            if st.button("🗑️ Delete", use_container_width=True):
                del st.session_state.chat_library[selected_archive]
                st.rerun()

# --- MAIN TABS ---
tab_console, tab_ember, tab_widgets = st.tabs(["💬 AI Console", "🔥 JARVIS Core", "📊 Utility Dashboard"])

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
            response = client.chat.completions.create(model=model_id, messages=cleaned_messages, temperature=0.6)
            ai_reply = response.choices[0].message.content
            st.write(ai_reply)
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})

        st.session_state.chat_library[st.session_state.current_chat_id] = st.session_state.messages.copy()

# ==========================================
# TAB 2: JARVIS HUD
# ==========================================
with tab_ember:
    st.markdown('<div class="glow-title">⚡ J.A.R.V.I.S. HUD Core</div>', unsafe_allow_html=True)
    st.markdown('<div class="glow-subtitle">REAL-TIME HOLOGRAPHIC TRANSPARENT DISPLAY UI</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        core_scale = st.slider("RING RADIUS", 0.7, 1.5, 1.0, 0.05)
    with c2:
        rot_speed = st.slider("ROTATION SPEED", 0.5, 3.0, 1.2, 0.1)

    transparent_hud_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; overflow: hidden; }}
            body {{
                background: #02060c;
                font-family: 'Segoe UI', system-ui, sans-serif;
                color: #e2e8f0;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 520px;
                border: 1px solid rgba(0, 242, 254, 0.25);
                border-radius: 16px;
                position: relative;
                box-shadow: inset 0 0 50px rgba(0, 0, 0, 0.8), 0 0 30px rgba(0, 242, 254, 0.15);
            }}
            canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; }}
            .status-badge {{
                position: absolute; bottom: 35px; left: 50%; transform: translateX(-50%);
                display: flex; flex-direction: column; align-items: center; gap: 4px; z-index: 10;
            }}
            .status-tag {{ font-size: 12px; font-weight: 800; letter-spacing: 3px; color: #00f2fe; text-shadow: 0 0 10px #00f2fe; }}
        </style>
    </head>
    <body>
        <canvas id="hudCanvas"></canvas>
        <div class="status-badge">
            <div class="status-tag">⚡ CORE ACTIVE</div>
            <div style="font-size: 9px; color: rgba(255, 255, 255, 0.4);">J.A.R.V.I.S. ONLINE // SYSTEM NOMINAL</div>
        </div>
        <script>
            const canvas = document.getElementById('hudCanvas');
            const ctx = canvas.getContext('2d');
            let width, height;
            function resize() {{ width = canvas.width = canvas.offsetWidth; height = canvas.height = canvas.offsetHeight; }}
            resize();
            window.addEventListener('resize', resize);

            let angle = 0;
            function render() {{
                ctx.clearRect(0, 0, width, height);
                angle += 0.01 * {rot_speed};
                const cx = width / 2, cy = height / 2 - 10, r = 100 * {core_scale};

                ctx.save();
                ctx.translate(cx, cy);

                // Segmented Outer Ring
                ctx.save();
                ctx.rotate(angle);
                ctx.beginPath();
                ctx.arc(0, 0, r * 1.25, 0, Math.PI * 2);
                ctx.strokeStyle = '#00f2fe';
                ctx.lineWidth = 3;
                ctx.setLineDash([12, 16, 4, 16]);
                ctx.stroke();
                ctx.restore();

                // Inner Ticks
                ctx.save();
                ctx.rotate(-angle * 0.5);
                for (let i = 0; i < 48; i++) {{
                    const a = (i * Math.PI * 2) / 48;
                    ctx.beginPath();
                    ctx.moveTo(Math.cos(a) * r * 0.9, Math.sin(a) * r * 0.9);
                    ctx.lineTo(Math.cos(a) * r * 1.05, Math.sin(a) * r * 1.05);
                    ctx.strokeStyle = i % 4 === 0 ? '#00f2fe' : '#0072ff';
                    ctx.lineWidth = i % 4 === 0 ? 2 : 1;
                    ctx.stroke();
                }}
                ctx.restore();

                // Solid Core Ring
                ctx.beginPath();
                ctx.arc(0, 0, r * 0.85, 0, Math.PI * 2);
                ctx.strokeStyle = '#00f2fe';
                ctx.lineWidth = 2.5;
                ctx.shadowBlur = 15;
                ctx.shadowColor = '#00f2fe';
                ctx.stroke();

                // Center Text
                ctx.font = '900 22px sans-serif';
                ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
                ctx.fillStyle = '#ffffff';
                ctx.fillText('J.A.R.V.I.S.', 0, 0);

                ctx.restore();
                requestAnimationFrame(render);
            }}
            render();
        </script>
    </body>
    </html>
    """
    components.html(transparent_hud_html, height=540)

# ==========================================
# TAB 3: UTILITY WIDGETS DASHBOARD
# ==========================================
with tab_widgets:
    st.markdown('<div class="glow-title">📊 OS Workspace & Widgets</div>', unsafe_allow_html=True)
    st.markdown('<div class="glow-subtitle">TACTICAL DASHBOARD & UTILITY SUITE</div>', unsafe_allow_html=True)

    # TOP BANNER: LIVE CLOCK & DATE WIDGET
    clock_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                background: rgba(5, 18, 32, 0.8);
                border: 1px solid rgba(0, 242, 254, 0.3);
                border-radius: 12px;
                padding: 15px 25px;
                color: #ffffff;
                font-family: 'Segoe UI', system-ui, sans-serif;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 4px 20px rgba(0, 242, 254, 0.15);
            }
            .time-text {
                font-size: 38px;
                font-weight: 900;
                color: #00f2fe;
                letter-spacing: 2px;
                text-shadow: 0 0 15px rgba(0, 242, 254, 0.6);
            }
            .date-text {
                font-size: 16px;
                font-weight: 700;
                color: #94a3b8;
                letter-spacing: 1.5px;
                text-align: right;
            }
            .sys-tag {
                font-size: 10px;
                letter-spacing: 2px;
                color: #00f2fe;
                text-transform: uppercase;
            }
        </style>
    </head>
    <body>
        <div>
            <div class="sys-tag">LOCAL SYSTEM TIME</div>
            <div id="clock" class="time-text">00:00:00 AM</div>
        </div>
        <div>
            <div class="sys-tag" style="text-align: right;">DATE // CALENDAR</div>
            <div id="date" class="date-text">Loading...</div>
        </div>
        <script>
            function updateClock() {
                const now = new Date();
                document.getElementById('clock').innerText = now.toLocaleTimeString();
                document.getElementById('date').innerText = now.toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
            }
            setInterval(updateClock, 1000);
            updateClock();
        </script>
    </body>
    </html>
    """
    components.html(clock_html, height=100)

    col_left, col_right = st.columns([1, 1])

    # LEFT COLUMN: CALCULATOR & TASK MANAGER
    with col_left:
        st.markdown('<div class="widget-panel">', unsafe_allow_html=True)
        st.subheader("🧮 Tactical Calculator")
        
        # Display Calculator Screen
        st.text_input("Expression", value=st.session_state.calc_expr, key="calc_display", disabled=True)

        # Calculator Buttons Grid
        b_col1, b_col2, b_col3, b_col4 = st.columns(4)
        with b_col1:
            if st.button("7", use_container_width=True): st.session_state.calc_expr += "7"; st.rerun()
            if st.button("4", use_container_width=True): st.session_state.calc_expr += "4"; st.rerun()
            if st.button("1", use_container_width=True): st.session_state.calc_expr += "1"; st.rerun()
            if st.button("C", use_container_width=True): st.session_state.calc_expr = ""; st.rerun()

        with b_col2:
            if st.button("8", use_container_width=True): st.session_state.calc_expr += "8"; st.rerun()
            if st.button("5", use_container_width=True): st.session_state.calc_expr += "5"; st.rerun()
            if st.button("2", use_container_width=True): st.session_state.calc_expr += "2"; st.rerun()
            if st.button("0", use_container_width=True): st.session_state.calc_expr += "0"; st.rerun()

        with b_col3:
            if st.button("9", use_container_width=True): st.session_state.calc_expr += "9"; st.rerun()
            if st.button("6", use_container_width=True): st.session_state.calc_expr += "6"; st.rerun()
            if st.button("3", use_container_width=True): st.session_state.calc_expr += "3"; st.rerun()
            if st.button(".", use_container_width=True): st.session_state.calc_expr += "."; st.rerun()

        with b_col4:
            if st.button("÷", use_container_width=True): st.session_state.calc_expr += "/"; st.rerun()
            if st.button("×", use_container_width=True): st.session_state.calc_expr += "*"; st.rerun()
            if st.button("-", use_container_width=True): st.session_state.calc_expr += "-"; st.rerun()
            if st.button("+", use_container_width=True): st.session_state.calc_expr += "+"; st.rerun()

        if st.button("=", use_container_width=True):
            try:
                st.session_state.calc_expr = str(eval(st.session_state.calc_expr))
            except Exception:
                st.session_state.calc_expr = "Error"
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

        # TASK MANAGER WIDGET
        st.markdown('<div class="widget-panel">', unsafe_allow_html=True)
        st.subheader("📋 System Task Tracker")
        
        new_task = st.text_input("Add Mission / Task", placeholder="Enter new task...")
        if st.button("➕ Add Task", use_container_width=True) and new_task:
            st.session_state.todo_list.append(new_task)
            st.rerun()

        st.write("---")
        for idx, task in enumerate(st.session_state.todo_list):
            t_col1, t_col2 = st.columns([4, 1])
            t_col1.write(f"• {task}")
            if t_col2.button("✖", key=f"del_{idx}"):
                st.session_state.todo_list.pop(idx)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # RIGHT COLUMN: INTERACTIVE CALENDAR & QUICK SCRATCHPAD
    with col_right:
        st.markdown('<div class="widget-panel">', unsafe_allow_html=True)
        st.subheader("📅 Interactive Calendar")
        
        selected_date = st.date_input("Select Date", datetime.now())
        
        # Monthly Calendar Grid View
        year = selected_date.year
        month = selected_date.month
        cal = calendar.month(year, month)
        
        st.code(cal, language="text")
        st.markdown('</div>', unsafe_allow_html=True)

        # QUICK NOTES SCRATCHPAD
        st.markdown('<div class="widget-panel">', unsafe_allow_html=True)
        st.subheader("📝 Encrypted Scratchpad")
        st.text_area("Quick AI Notes", height=160, placeholder="Type temporary ideas, calculations, or system prompts here...")
        st.markdown('</div>', unsafe_allow_html=True)
