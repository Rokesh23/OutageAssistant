import streamlit as st
from rag import retrieve
from llm import ask_llm

st.set_page_config(
    page_title="Outage RCA Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS matching Starry Header Banner + Light Body UI
custom_ui_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc !important; /* Clean light background for body */
        color: #0f172a;
        overflow: hidden !important; /* Fits everything without page scrolling */
    }

    /* Hide Streamlit default headers, footers, and chrome elements */
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; display: none !important; }
    div[data-testid="stToolbar"] { visibility: hidden; }
    section[data-testid="stSidebar"] { display: none; }
    button[data-testid="baseButton-header"] { display: none; }
    div[data-testid="stStatusWidget"] { visibility: hidden; }

    /* Starry Dark Blue Header Banner */
    .hero-header-banner {
        background: 
            radial-gradient(1px 1px at 20px 30px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 40px 70px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 80px 10px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 150px 80px, #cbd5e1, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 200px 20px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 300px 50px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 420px 90px, #cbd5e1, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 550px 30px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 650px 70px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 780px 15px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 900px 85px, #cbd5e1, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 1020px 40px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 1150px 65px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 1280px 25px, #cbd5e1, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 1400px 75px, #ffffff, rgba(0,0,0,0)),
            linear-gradient(135deg, #050a14 0%, #0c1427 45%, #182238 100%);
        color: #ffffff;
        padding: 24px 40px 20px 40px;
        margin-top: -60px;
        margin-left: -5rem;
        margin-right: -5rem;
        margin-bottom: 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
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
        color: #ffffff !important;
    }

    .hero-main-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #60a5fa 0%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 10px;
        margin-bottom: 4px;
    }

    .hero-main-subtitle {
        color: #cbd5e1;
        font-size: 0.92rem;
        font-weight: 400;
    }

    /* Metric Cards (Light Section) */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 10px 14px;
        display: flex;
        align-items: center;
        gap: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .metric-icon {
        width: 38px;
        height: 38px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }
    .metric-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.1;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #64748b;
        font-weight: 500;
    }
    .metric-subtext {
        font-size: 0.68rem;
        color: #10b981;
    }

    /* Action Buttons */
    .stButton>button {
        width: 100%;
        background-color: #ffffff;
        color: #0f172a;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 8px 12px;
        font-weight: 600;
        font-size: 0.82rem;
        text-align: left;
        transition: all 0.2s ease;
        margin-bottom: -10px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .stButton>button:hover {
        background-color: #f1f5f9;
        border-color: #cbd5e1;
        color: #0284c7;
    }

    .section-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 8px;
    }

    /* Chat Area Scrollable Box */
    div[data-testid="stChatMessageContainer"] {
        max-height: 260px !important;
        overflow-y: auto !important;
        padding-right: 5px;
    }

    div[data-testid="stChatMessage"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 10px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
        font-size: 0.88rem;
    }

    /* Footer */
    .footer {
        background-color: #050a14;
        color: #64748b;
        padding: 6px 40px;
        margin-left: -5rem;
        margin-right: -5rem;
        position: fixed;
        bottom: 0;
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.75rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
"""
st.markdown(custom_ui_style, unsafe_allow_html=True)

# Starry Header Banner (Centered Title + Top Right Home Link)
st.markdown("""
<div class="hero-header-banner">
    <div class="header-top-nav">
        <a href="?" target="_self" class="nav-link active">Home</a>
    </div>
    <div class="hero-main-title">Outage RCA Assistant</div>
    <div class="hero-main-subtitle">Investigate incidents. Identify root causes. Resolve faster.</div>
</div>
""", unsafe_allow_html=True)

# Metrics Overview Cards (In Light Background)
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon" style="background:#eff6ff; color:#2563eb;">📋</div>
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
        <div class="metric-icon" style="background:#f0fdf4; color:#16a34a;">🧠</div>
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
        <div class="metric-icon" style="background:#fff7ed; color:#ea580c;">🧩</div>
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
        <div class="metric-icon" style="background:#faf5ff; color:#9333ea;">📖</div>
        <div>
            <div class="metric-label">Resolution Playbooks</div>
            <div class="metric-value">14</div>
            <div class="metric-subtext">Step-by-step guides</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Main Dashboard Grid
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
    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:8px; font-size:0.78rem;">
        <table style="width:100%; border-collapse:collapse;">
            <tr style="border-bottom:1px solid #f1f5f9; color:#64748b; font-weight:600;">
                <td style="padding:4px 6px;">Incident ID</td>
                <td style="padding:4px 6px;">Project/System</td>
                <td style="padding:4px 6px;">Status</td>
                <td style="padding:4px 6px;">RCA Confidence</td>
            </tr>
            <tr style="border-bottom:1px solid #f8fafc;">
                <td style="padding:4px 6px; font-weight:600; color:#2563eb;">INC0178998</td>
                <td style="padding:4px 6px;">EDMS_RL PROD</td>
                <td style="padding:4px 6px; color:#16a34a; font-weight:600;">● Resolved</td>
                <td style="padding:4px 6px; font-weight:600;">98%</td>
            </tr>
            <tr style="border-bottom:1px solid #f8fafc;">
                <td style="padding:4px 6px; font-weight:600; color:#2563eb;">INC0176274</td>
                <td style="padding:4px 6px;">EDMS_RL QA</td>
                <td style="padding:4px 6px; color:#16a34a; font-weight:600;">● Resolved</td>
                <td style="padding:4px 6px; font-weight:600;">95%</td>
            </tr>
            <tr>
                <td style="padding:4px 6px; font-weight:600; color:#2563eb;">INC0191705</td>
                <td style="padding:4px 6px;">ASK2 PROD</td>
                <td style="padding:4px 6px; color:#16a34a; font-weight:600;">● Resolved</td>
                <td style="padding:4px 6px; font-weight:600;">92%</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# Chat Assistant Box
st.markdown('<div class="section-title" style="margin-top:10px;">💬 Ask Assistant</div>', unsafe_allow_html=True)

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
