import streamlit as st
from rag import retrieve
from llm import ask_llm

st.set_page_config(
    page_title="Outage RCA Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Dark Theme CSS with fixed layout & zero page overflow
custom_ui_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Viewport & Dark Background */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #0b1329 !important;
        color: #f1f5f9 !important;
        overflow-x: hidden !important;
    }

    /* Remove main block container extra top padding to prevent overflow */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
        max-width: 100% !important;
    }

    /* Hide Streamlit default UI elements */
    header[data-testid="stHeader"] { visibility: hidden; height: 0px !important; display: none !important; }
    #MainMenu { visibility: hidden; display: none !important; }
    footer { visibility: hidden; display: none !important; }
    div[data-testid="stToolbar"] { visibility: hidden; display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }

    /* Clean Hero Header Banner without negative margin breaks */
    .hero-header-banner {
        background: 
            radial-gradient(1px 1px at 20px 30px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 80px 10px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 300px 50px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 900px 85px, #cbd5e1, rgba(0,0,0,0)),
            linear-gradient(135deg, #030712 0%, #0b1329 50%, #1e293b 100%);
        color: #ffffff;
        padding: 20px 20px 25px 20px;
        margin-top: -20px;
        margin-bottom: 20px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        text-align: center;
        position: relative;
    }

    .header-top-nav {
        position: absolute;
        top: 15px;
        right: 25px;
        display: flex;
        align-items: center;
    }

    .nav-link {
        color: #94a3b8 !important;
        text-decoration: none !important;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .nav-link.active {
        color: #ffffff !important;
    }

    .hero-main-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 5px;
        margin-bottom: 4px;
    }

    .hero-main-subtitle {
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 400;
    }

    /* Metric Cards Styling */
    .metric-card {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 10px;
        padding: 12px 16px;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }
    .metric-value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #f8fafc !important;
        line-height: 1.1;
    }
    .metric-label {
        font-size: 0.76rem;
        color: #94a3b8 !important;
        font-weight: 500;
    }

    /* Action Buttons Styling */
    .stButton>button {
        width: 100%;
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 8px;
        padding: 10px 14px;
        font-weight: 600;
        font-size: 0.82rem;
        text-align: left;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #334155 !important;
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
    }

    .section-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: #f8fafc !important;
        margin-bottom: 10px;
    }

    /* Incident Table Styling */
    .incident-table-container {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px;
        padding: 10px;
        font-size: 0.78rem;
        color: #f8fafc !important;
    }

    /* Chat Messages Styling */
    div[data-testid="stChatMessage"] {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #f8fafc !important;
    }

    /* Native Bottom Chat Input Box Dark Theme */
    div[data-testid="stChatInput"] > div {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stChatInput"] textarea {
        color: #f8fafc !important;
    }
    </style>
"""
st.markdown(custom_ui_style, unsafe_allow_html=True)

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "preset_prompt" not in st.session_state:
    st.session_state.preset_prompt = None

# Header Banner
st.markdown("""
<div class="hero-header-banner">
    <div class="header-top-nav">
        <a href="?" target="_self" class="nav-link active">Home</a>
    </div>
    <div class="hero-main-title">Outage RCA Assistant</div>
    <div class="hero-main-subtitle">Investigate incidents • Identify root causes • Resolve faster</div>
</div>
""", unsafe_allow_html=True)

# Metric Cards Overview
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon" style="background:#1e3a8a; color:#60a5fa;">📋</div>
        <div>
            <div class="metric-label">Incidents Analyzed</div>
            <div class="metric-value">14</div>
            <div class="metric-subtext" style="font-size:0.68rem; color:#34d399;">↑ 100% indexed in system</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon" style="background:#064e3b; color:#34d399;">🧠</div>
        <div>
            <div class="metric-label">RCA Knowledge</div>
            <div class="metric-value">16</div>
            <div class="metric-subtext" style="font-size:0.68rem; color:#34d399;">Articles & known causes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon" style="background:#7c2d12; color:#fb923c;">🧩</div>
        <div>
            <div class="metric-label">Common Error Codes</div>
            <div class="metric-value">81</div>
            <div class="metric-subtext" style="font-size:0.68rem; color:#34d399;">Mapped & documented</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon" style="background:#581c87; color:#c084fc;">📖</div>
        <div>
            <div class="metric-label">Resolution Playbooks</div>
            <div class="metric-value">14</div>
            <div class="metric-subtext" style="font-size:0.68rem; color:#34d399;">Step-by-step guides</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Action Buttons and Recent Incident Insights Grid
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.markdown('<div class="section-title">What can I help you with?</div>', unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("🔍 Find Root Cause"):
            st.session_state.preset_prompt = "What are the primary root causes across all incidents?"
            st.rerun()
        if st.button("⏱️ Check Incidents"):
            st.session_state.preset_prompt = "show me all the incidents"
            st.rerun()

    with b2:
        if st.button("💻 Analyze Error Code"):
            st.session_state.preset_prompt = "List all incidents with gateway timeout or bad gateway errors"
            st.rerun()
        if st.button("🛠️ Recommend Fix"):
            st.session_state.preset_prompt = "What are the fixes and resolutions applied for EDMS_RL incidents?"
            st.rerun()

with col_right:
    st.markdown('<div class="section-title">Recent Incident Insights</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="incident-table-container">
        <table style="width:100%; border-collapse:collapse;">
            <tr style="border-bottom:1px solid #334155; color:#94a3b8; font-weight:600;">
                <td style="padding:6px;">Incident ID</td>
                <td style="padding:6px;">Project/System</td>
                <td style="padding:6px;">Status</td>
                <td style="padding:6px;">RCA Confidence</td>
            </tr>
            <tr style="border-bottom:1px solid #0f172a;">
                <td style="padding:6px; font-weight:600; color:#38bdf8;">INC0178998</td>
                <td style="padding:6px;">EDMS_RL PROD</td>
                <td style="padding:6px; color:#34d399; font-weight:600;">● Resolved</td>
                <td style="padding:6px; font-weight:600;">98%</td>
            </tr>
            <tr style="border-bottom:1px solid #0f172a;">
                <td style="padding:6px; font-weight:600; color:#38bdf8;">INC0176274</td>
                <td style="padding:6px;">EDMS_RL QA</td>
                <td style="padding:6px; color:#34d399; font-weight:600;">● Resolved</td>
                <td style="padding:6px; font-weight:600;">95%</td>
            </tr>
            <tr>
                <td style="padding:6px; font-weight:600; color:#38bdf8;">INC0191705</td>
                <td style="padding:6px;">ASK2 PROD</td>
                <td style="padding:6px; color:#34d399; font-weight:600;">● Resolved</td>
                <td style="padding:6px; font-weight:600;">92%</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Render message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Bottom Fixed Input Box
user_input = st.chat_input("Ask about an incident, error code, RCA, or resolution...")

if st.session_state.preset_prompt:
    user_input = st.session_state.preset_prompt
    st.session_state.preset_prompt = None

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing RCA Documents..."):
            context_str, matched_results, confidence = retrieve(user_input)
            full_response = ask_llm(user_input, context_str)
            st.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
