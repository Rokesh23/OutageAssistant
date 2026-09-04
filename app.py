import streamlit as st
from rag import retrieve
from llm import ask_llm

st.set_page_config(
    page_title="Outage RCA Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS matching Hero Search Input + Light Body Grid
custom_ui_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc !important;
        color: #0f172a;
    }

    /* Hide default Streamlit headers, footers, toolbars */
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; display: none !important; }
    #MainMenu { visibility: hidden; display: none !important; }
    footer { visibility: hidden; display: none !important; }
    div[data-testid="stToolbar"] { visibility: hidden; display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    button[data-testid="baseButton-header"] { display: none !important; }
    div[data-testid="stStatusWidget"] { visibility: hidden; display: none !important; }

    /* Hide Bottom Floating Host Badges */
    div[data-testid="stAppToolbar"], 
    .stAppToolbar, 
    .viewerBadge_container__1QSob,
    [data-testid="manage-app-button"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Starry Header Banner */
    .hero-header-banner {
        background: 
            radial-gradient(1px 1px at 20px 30px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 80px 10px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 300px 50px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 900px 85px, #cbd5e1, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 1280px 25px, #cbd5e1, rgba(0,0,0,0)),
            linear-gradient(135deg, #050a14 0%, #0c1427 45%, #182238 100%);
        color: #ffffff;
        padding: 30px 40px 35px 40px;
        margin-top: -60px;
        margin-left: -5rem;
        margin-right: -5rem;
        margin-bottom: 24px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        position: relative;
    }

    .header-top-nav {
        position: absolute;
        top: 20px;
        right: 40px;
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
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #60a5fa 0%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 10px;
        margin-bottom: 6px;
    }

    .hero-main-subtitle {
        color: #cbd5e1;
        font-size: 0.95rem;
        font-weight: 400;
        margin-bottom: 20px;
    }

    /* Style the Search Input Box inside Header */
    div[data-testid="stTextInput"] {
        max-width: 680px;
        margin: 0 auto;
    }

    div[data-testid="stTextInput"] input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
        padding: 12px 18px !important;
        font-size: 0.92rem !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }

    /* Metric Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 16px;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
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
        color: #0f172a;
        line-height: 1.1;
    }
    .metric-label {
        font-size: 0.76rem;
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
        padding: 10px 14px;
        font-weight: 600;
        font-size: 0.82rem;
        text-align: left;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .stButton>button:hover {
        background-color: #f1f5f9;
        border-color: #cbd5e1;
        color: #0284c7;
    }

    .section-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 10px;
    }

    /* Chat Response Container */
    div[data-testid="stChatMessage"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 12px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
        font-size: 0.88rem;
        margin-bottom: 12px;
    }

    /* Footer */
    .footer {
        background-color: #050a14;
        color: #64748b;
        padding: 8px 40px;
        margin-left: -5rem;
        margin-right: -5rem;
        margin-top: 40px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.75rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
"""
st.markdown(custom_ui_style, unsafe_allow_html=True)

# State Management
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# Header Banner with Search Input Box inside
st.markdown("""
<div class="hero-header-banner">
    <div class="header-top-nav">
        <a href="?" target="_self" class="nav-link active">Home</a>
    </div>
    <div class="hero-main-title">Outage RCA Assistant</div>
    <div class="hero-main-subtitle">Investigate incidents • Identify root causes • Resolve faster</div>
</div>
""", unsafe_allow_html=True)

# Input Box placed inside the header visually
user_input = st.text_input(
    "", 
    value=st.session_state.search_query,
    placeholder="🔍 Ask about an incident, error code, RCA, or resolution...",
    label_visibility="collapsed",
    key="header_search_box"
)

st.write("")

# Metrics Overview Cards (Placed below second bar / below header)
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

# Action Tiles and Incidents Table Grid
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.markdown('<div class="section-title">What can I help you with?</div>', unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("🔍 Find Root Cause"):
            st.session_state.search_query = "What are the primary root causes across all incidents?"
            st.rerun()
        if st.button("⏱️ Check Incidents"):
            st.session_state.search_query = "show me all the incidents"
            st.rerun()

    with b2:
        if st.button("💻 Analyze Error Code"):
            st.session_state.search_query = "List all incidents with gateway timeout or bad gateway errors"
            st.rerun()
        if st.button("🛠️ Recommend Fix"):
            st.session_state.search_query = "What are the fixes and resolutions applied for EDMS_RL incidents?"
            st.rerun()

with col_right:
    st.markdown('<div class="section-title">Recent Incident Insights</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:10px; font-size:0.78rem;">
        <table style="width:100%; border-collapse:collapse;">
            <tr style="border-bottom:1px solid #f1f5f9; color:#64748b; font-weight:600;">
                <td style="padding:6px;">Incident ID</td>
                <td style="padding:6px;">Project/System</td>
                <td style="padding:6px;">Status</td>
                <td style="padding:6px;">RCA Confidence</td>
            </tr>
            <tr style="border-bottom:1px solid #f8fafc;">
                <td style="padding:6px; font-weight:600; color:#2563eb;">INC0178998</td>
                <td style="padding:6px;">EDMS_RL PROD</td>
                <td style="padding:6px; color:#16a34a; font-weight:600;">● Resolved</td>
                <td style="padding:6px; font-weight:600;">98%</td>
            </tr>
            <tr style="border-bottom:1px solid #f8fafc;">
                <td style="padding:6px; font-weight:600; color:#2563eb;">INC0176274</td>
                <td style="padding:6px;">EDMS_RL QA</td>
                <td style="padding:6px; color:#16a34a; font-weight:600;">● Resolved</td>
                <td style="padding:6px; font-weight:600;">95%</td>
            </tr>
            <tr>
                <td style="padding:6px; font-weight:600; color:#2563eb;">INC0191705</td>
                <td style="padding:6px;">ASK2 PROD</td>
                <td style="padding:6px; color:#16a34a; font-weight:600;">● Resolved</td>
                <td style="padding:6px; font-weight:600;">92%</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# Process Search Query and Render Answer
if user_input:
    st.write("")
    st.markdown('<div class="section-title">Analysis Result</div>', unsafe_allow_html=True)
    with st.spinner("Analyzing RCA Documents..."):
        context_str, matched_results, confidence = retrieve(user_input)
        full_response = ask_llm(user_input, context_str)
        with st.chat_message("assistant"):
            st.markdown(full_response)

# Footer
st.markdown("""
<div class="footer">
    <div>🛡️ Secure • Trusted • Always On</div>
    <div>© 2026 Outage RCA Assistant | v1.0.0</div>
</div>
""", unsafe_allow_html=True)
