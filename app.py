import streamlit as st
from rag import retrieve
from llm import ask_llm

st.set_page_config(
    page_title="Outage RCA Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to mimic the exact Dashboard UI layout and styling
custom_ui_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #f4f6f9 !important;
        color: #1e293b;
    }

    /* Hide default Streamlit headers, menus, and footers */
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; display: none !important; }
    div[data-testid="stToolbar"] { visibility: hidden; }
    section[data-testid="stSidebar"] { display: none; }
    button[data-testid="baseButton-header"] { display: none; }
    div[data-testid="stStatusWidget"] { visibility: hidden; }

    /* Top Navigation Bar */
    .navbar {
        background-color: #0b132b;
        color: #ffffff;
        padding: 12px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #1c2541;
        margin-top: -60px;
        margin-left: -5rem;
        margin-right: -5rem;
    }
    .navbar-title {
        font-weight: 700;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #0b132b 0%, #1c2541 60%, #3a506b 100%);
        color: white;
        padding: 40px 60px 50px 60px;
        margin-left: -5rem;
        margin-right: -5rem;
        border-bottom: 1px solid #3a506b;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .hero-subtitle {
        color: #cbd5e1;
        font-size: 1.1rem;
        margin-bottom: 4px;
        font-weight: 500;
    }
    .hero-caption {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 25px;
    }

    /* Metric Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 20px;
        display: flex;
        align-items: center;
        gap: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .metric-icon {
        width: 48px;
        height: 48px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 500;
    }
    .metric-subtext {
        font-size: 0.75rem;
        color: #10b981;
        margin-top: 2px;
    }

    /* Cards Container */
    .section-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 20px;
    }
    .section-title {
        font-size: 1rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 16px;
    }

    /* Action Tile Buttons */
    .stButton>button {
        width: 100%;
        background-color: #f8fafc;
        color: #1e293b;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 16px;
        font-weight: 600;
        text-align: left;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #eff6ff;
        border-color: #3b82f6;
        color: #2563eb;
    }

    /* Footer */
    .footer {
        background-color: #0b132b;
        color: #64748b;
        padding: 16px 40px;
        margin-left: -5rem;
        margin-right: -5rem;
        margin-top: 40px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.85rem;
    }

    /* Table Adjustments */
    div[data-testid="stChatMessage"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }
    </style>
"""
st.markdown(custom_ui_style, unsafe_allow_html=True)

# Top Navigation Bar
st.markdown("""
<div class="navbar">
    <div class="navbar-title">🎯 Outage RCA Assistant</div>
    <div style="font-size: 0.88rem; color: #94a3b8;">Home &nbsp;|&nbsp; Incidents &nbsp;|&nbsp; RCA Insights &nbsp;|&nbsp; Knowledge Base</div>
</div>
""", unsafe_allow_html=True)

# Hero Section Header
st.markdown("""
<div class="hero-section">
    <div class="hero-title">Outage RCA Assistant</div>
    <div class="hero-subtitle">Investigate incidents. Identify root causes. Resolve faster.</div>
    <div class="hero-caption">Ask questions about outages, root causes, resolutions, error codes, and lessons learned.</div>
</div>
""", unsafe_allow_html=True)

st.write("")

# Metrics Overview Banner
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
            <div class="metric-subtext">Step-by-step fixes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

# Main Dashboard Content Grid
col_left, col_right = st.columns([1, 1.3])

# Set initial query trigger state
if "query_trigger" not in st.session_state:
    st.session_state.query_trigger = None

with col_left:
    st.markdown('<div class="section-title">What can I help you with?</div>', unsafe_allow_html=True)
    
    b1, b2 = st.columns(2)
    with b1:
        if st.button("🎯 Find Root Cause\nAsk questions to identify causes"):
            st.session_state.query_trigger = "What are the primary root causes across all incidents?"
        if st.button("⏱️ Check Previous Incidents\nSearch historical outage records"):
            st.session_state.query_trigger = "show me all the incidents"

    with b2:
        if st.button("💻 Analyze Error Code\nGet details for error codes"):
            st.session_state.query_trigger = "List all incidents with 504 gateway timeout or 502 bad gateway errors"
        if st.button("🛠️ Recommend Resolution\nGet recommended resolution steps"):
            st.session_state.query_trigger = "What are the fixes and resolutions applied for EDMS_RL incidents?"

with col_right:
    st.markdown('<div class="section-title">Recent Incident Insights</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:12px; font-size:0.85rem;">
        <table style="width:100%; border-collapse:collapse;">
            <tr style="border-bottom:1px solid #f1f5f9; color:#64748b; font-weight:600;">
                <td style="padding:8px;">Incident ID</td>
                <td style="padding:8px;">Project/System</td>
                <td style="padding:8px;">Status</td>
                <td style="padding:8px;">RCA Confidence</td>
            </tr>
            <tr style="border-bottom:1px solid #f8fafc;">
                <td style="padding:8px; font-weight:600; color:#2563eb;">INC0178998</td>
                <td style="padding:8px;">EDMS_RL PROD</td>
                <td style="padding:8px; color:#16a34a; font-weight:600;">● Resolved</td>
                <td style="padding:8px; font-weight:600;">98%</td>
            </tr>
            <tr style="border-bottom:1px solid #f8fafc;">
                <td style="padding:8px; font-weight:600; color:#2563eb;">INC0176274</td>
                <td style="padding:8px;">EDMS_RL QA</td>
                <td style="padding:8px; color:#16a34a; font-weight:600;">● Resolved</td>
                <td style="padding:8px; font-weight:600;">95%</td>
            </tr>
            <tr>
                <td style="padding:8px; font-weight:600; color:#2563eb;">INC0191705</td>
                <td style="padding:8px;">ASK2 PROD</td>
                <td style="padding:8px; color:#16a34a; font-weight:600;">● Resolved</td>
                <td style="padding:8px; font-weight:600;">92%</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.markdown("---")

# Chat Assistant Section
st.subheader("💬 Ask Assistant")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input from Chat Bar or Quick Action Buttons
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

# Footer Bar
st.markdown("""
<div class="footer">
    <div>🛡️ Secure • Trusted • Always On | Your operations, our priority.</div>
    <div>© 2026 Outage RCA Assistant. All rights reserved. | Version 1.0.0</div>
</div>
""", unsafe_allow_html=True)
