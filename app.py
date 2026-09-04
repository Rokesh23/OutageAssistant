import streamlit as st
from rag import retrieve
from llm import ask_llm

st.set_page_config(
    page_title="Outage RCA Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to hide top header, toolbar (Share, Edit, GitHub), menu, footer, and Streamlit Cloud buttons
hide_streamlit_style = """
    <style>
    /* Hide the top header bar and toolbar options (Share, Star, Edit, GitHub, Menu) */
    header[data-testid="stHeader"] {
        visibility: hidden;
        height: 0%;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stToolbar"] {visibility: hidden;}

    /* Hide sidebar collapse button */
    section[data-testid="stSidebar"] {
        display: none;
    }
    button[data-testid="baseButton-header"] {
        display: none;
    }

    /* Hide bottom-right Streamlit Cloud management button */
    div[data-testid="stStatusWidget"] {
        visibility: hidden;
    }
    .viewerBadge_container__1QS3n {
        display: none !important;
    }
    button[title="View app in Streamlit Cloud"] {
        display: none !important;
    }
    footer {display: none !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Main Interface Header
st.title("🤖 Outage RCA Assistant")
st.caption("Ask questions about outages, root causes, resolutions and lessons learned.")

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
