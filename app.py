import streamlit as st
from rag import retrieve
from llm import ask_llm

st.set_page_config(
    page_title="Outage RCA Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark Enterprise UI Palette
custom_ui_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Application Container - Slate Dark Background */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Inter', sans-serif;
        background-color: #0b0f17 !important;
        color: #f1f5f9 !important;
        overflow: hidden !important;
    }

    /* Hide Streamlit default UI overlays */
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; display: none !important; }
    div[data-testid="stToolbar"] { visibility: hidden; }
    section[data-testid="stSidebar"] { display: none; }
    button[data-testid="baseButton-header"] { display: none; }
    div[data-testid="stStatusWidget"] { visibility: hidden; }

    /* Header Banner with Subtle Space Effect */
    .hero-header-banner {
        background: 
            radial-gradient(1px 1px at 20px 30px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 80px 10px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 300px 50px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 900px 85px, #cbd5e1, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 1280px 25px, #cbd5e1, rgba(0,0,0,0)),
            linear-gradient(180deg, #070a10 0%, #0b0f17 100%);
        color: #ffffff;
        padding: 22px 40px 18px 40px;
        margin-top: -60px;
        margin-left: -5rem;
        margin-right: -5rem;
        margin-bottom: 20px;
        border-bottom: 1px solid #1e293b;
        text-align: center;
        position: relative;
    }

    .header-top-nav {
        position: absolute;
        top: 18px;
        right: 40px;
        display: flex;
        align-items: center;
    }

    .nav-link {
        color: #94a3b8 !important;
        text-decoration: none !important;
        font-size: 0.85rem;
        font-weight: 500;
        transition: color 0.2s ease;
    }
    .nav-link:hover, .nav-link.active {
        color: #38bdf8 !important;
    }

    .hero-main-title {
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #60a5fa 0%, #38bdf8 100%);
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

    /* Metric Cards - Dark Glass Style */
    .metric-card {
        background: #111827;
        border: 1px solid #1f293d;
        border-radius: 10px;
        padding: 12px 16px;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }
    .metric-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.15rem;
    }
    .metric-value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.1;
    }
    .metric-label {
        font-size: 0.76rem;
        color: #94a3b8;
        font-weight: 500;
    }
    .metric-subtext {
        font-size: 0.68rem;
        color: #34d399;
    }

    /* Action Tile Buttons */
    .stButton>button {
        width: 100%;
        background-color: #111827;
        color: #f1f5f9;
        border: 1px solid #1f293d;
        border-radius: 8px;
        padding: 9px 14px;
        font-weight: 600;
        font-size: 0.82rem;
        text-align: left;
        transition: all 0.2s ease;
        margin-bottom: -10px;
    }
    .stButton>button:hover {
        background-color: #1e293b;
        border-color: #38bdf8;
        color: #38bdf8;
    }

    .section-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 10px;
    }

    /* Chat Area Settings */
    div[data-testid="stChatMessageContainer"] {
        max-height: 260px !important;
        overflow-y: auto !important;
        padding-right: 5px;
    }

    div[data-testid="stChatMessage"] {
        background: #111827 !important;
        border: 1px solid #1f293d !important;
        border-radius: 8px !important;
        padding: 10px !important;
        color: #f8fafc !important;
        font-size: 0.88rem;
    }

    /* Bottom Input Box Styling */
    div[data-testid="stChatInput"] input {
        background-color: #111827 !important;
        color: #f8fafc !important;
        border: 1px solid #1f293d !important;
        border-radius: 8px !important;
    }

    /* Footer */
    .footer {
        background-color: #070a10;
        color: #64748b;
        padding: 8px 40px;
        margin-left: -5rem;
        margin-right: -5rem;
        position: fixed;
        bottom: 0;
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.75rem;
        border-top: 1px solid #1e293b;
    }
    </style>
"""
st.markdown(custom_ui_style, unsafe_allow_html=True)

# Dark Hero Banner
st.markdown("""
<div class="hero-header-banner">
    <div class="header-top-nav">
        <a href="?" target="_self" class="nav-link active">Home</a>
    </div>
    <div class="hero-main-title">Outage RCA Assistant</div>
    <div class="hero-main-subtitle">Investigate incidents • Identify root causes • Resolve faster</div>
</div>
""", unsafe_allow_html=True)

# Metrics Cards (Dark Theme)
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon" style="background:#1e3a8a; color:#60a5fa;">📋</div>
        <div>
            <div class="metric-label">Incidents Analyzed</div>
            <div class="metric-value">14</div>
            <div class="metric-subtext">↑ 100% indexed in system</div>
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
            <div class="metric-subtext">Articles & known causes</div>
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
            <div class="metric-subtext">Mapped & documented</div>
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
            <div class="metric-subtext">Step-by-step guides</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Layout Grid
col_left, col_right = st.columns([1, 1.2])

if "query_trigger" not in st.session_state:
    st.session_state.query_trigger = None

with col_left:
    st.markdown('<div class="section-title">What can I help you with?</div>', unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("🔍 Find Root Cause"):
            st.session_state.query_trigger = "What are the primary root causes across all incidents?"
        if st.button("⏱️ Check Incidents"):
            st.session_state.query_trigger = "show me all the incidents"

    with b2:
        if st.button("💻 Analyze Error Code"):
            st.session_state.query_trigger = "List all incidents with gateway timeout or bad gateway errors"
        if st.button("🛠️ Recommend Fix"):
            st.session_state.query_trigger = "What are the fixes and resolutions applied for EDMS_RL incidents?"

with col_right:
    st.markdown('<div class="section-title">Recent Incident Insights</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#111827; border:1px solid #1f293d; border-radius:8px; padding:10px; font-size:0.78rem; color:#f8fafc;">
        <table style="width:100%; border-collapse:collapse;">
            <tr style="border-bottom:1px solid #1f293d; color:#94a3b8; font-weight:600;">
                <td style="padding:6px;">Incident ID</td>
                <td style="padding:6px;">Project/System</td>
                <td style="padding:6px;">Status</td>
                <td style="padding:6px;">RCA Confidence</td>
            </tr>
            <tr style="border-bottom:1px solid #161e2e;">
                <td style="padding:6px; font-weight:600; color:#38bdf8;">INC0178998</td>
                <td style="padding:6px;">EDMS_RL PROD</td>
                <td style="padding:6px; color:#34d399; font-weight:600;">● Resolved</td>
                <td style="padding:6px; font-weight:600;">98%</td>
            </tr>
            <tr style="border-bottom:1px solid #161e2e;">
                <td style="padding:6px; font-weight:600; color:#38bdf8;">INC0176274</td>
                <td style="padding:6px;">EDMS_RL QA</td>
                <td style="padding:6px; color:#34d399; font-weight:600;">● Resolved</td>
                <td style="padding:6px; font-weight:600;">95%</td>
            </tr>
            <tr>
                <td style="padding:6px; font-weight:600; color:#38bdf8;">INC0191705</td>
                <td style="padding:6px;">ASK2 PROD</td>
                <td style="padding:6px; color:#34d399; font-weight:600;">● Resolved</td>
                <td style="padding:4px 6px;">92%</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# Chat Area
st.markdown('<div class="section-title" style="margin-top:12px;">💬 Ask Assistant</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_prompt = st.chat_input("Ask about an incident, error code, RCA, or resolution...")

if st.session_state.query_trigger:
    user_prompt = st.session_state.query_trigger
    st.session_state.query_trigger = None

if user_prompt:
    st.chat_message("user").markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing RCA Documents..."):
            context_str, matched_results, confidence = retrieve(user_prompt)
            full_response = ask_llm(user_prompt, context_str)
            st.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Footer Section
st.markdown("""
<div class="footer">
    <div>🛡️ Secure • Trusted • Always On</div>
    <div>© 2026 Outage RCA Assistant | v1.0.0</div>
</div>
""", unsafe_allow_html=True)
