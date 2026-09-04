import streamlit as st
from rag import retrieve
from llm import ask_llm

st.set_page_config(
    page_title="Outage RCA Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Background, Modern Styling, and Hidden Chrome Elements
custom_ui_style = """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%) !important;
        background-attachment: fixed !important;
        color: #f8fafc;
    }

    /* Hide Top Header, Toolbar, Footer, and Sidebar */
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; display: none !important; }
    div[data-testid="stToolbar"] { visibility: hidden; }
    section[data-testid="stSidebar"] { display: none; }
    button[data-testid="baseButton-header"] { display: none; }
    div[data-testid="stStatusWidget"] { visibility: hidden; }
    .viewerBadge_container__1QS3n { display: none !important; }

    /* Custom Header Styling */
    .title-text {
        font-size: 2.25rem;
        font-weight: 700;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .caption-text {
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Chat Messages Glassmorphism Cards */
    div[data-testid="stChatMessage"] {
        background: rgba(30, 41, 59, 0.65) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 1rem 1.25rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
    }

    /* Markdown Table Styling Inside Chat */
    div[data-testid="stChatMessage"] table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
        border-radius: 8px;
        overflow: hidden;
    }

    div[data-testid="stChatMessage"] th {
        background-color: #312e81 !important;
        color: #e0e7ff !important;
        padding: 10px 14px;
        text-align: left;
    }

    div[data-testid="stChatMessage"] td {
        background-color: rgba(15, 23, 42, 0.5) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding: 10px 14px;
        color: #cbd5e1;
    }

    /* Chat Input Bar Styling */
    div[data-testid="stChatInput"] {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(99, 102, 241, 0.4) !important;
        border-radius: 12px !important;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.2) !important;
    }

    div[data-testid="stChatInput"] textarea {
        color: #f8fafc !important;
    }

    </style>
"""
st.markdown(custom_ui_style, unsafe_allow_html=True)

# Main Interface Header
st.markdown('<div class="title-text">🤖 Outage RCA Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="caption-text">Ask questions about outages, root causes, resolutions, and lessons learned.</div>', unsafe_allow_html=True)

# Chat history initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask a question about incidents, RCAs, or error codes..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing RCA Documents..."):
            context_str, matched_results, confidence = retrieve(prompt)
            full_response = ask_llm(prompt, context_str)
            st.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
