import streamlit as st
from rag import retrieve
from llm import ask_llm

st.set_page_config(
    page_title="Outage RCA Assistant",
    page_icon="🤖",
    layout="wide"
)

# Sidebar UI
with st.sidebar:
    st.title("🤖 Outage Assistant")
    st.subheader("AI Powered RCA Knowledge Assistant")
    
    st.markdown("---")
    st.markdown("### 📊 Knowledge Base")
    st.markdown("📄 **Documents**: 16")
    st.markdown("📑 **Sections**: 81")
    st.markdown("🚨 **Incidents**: 14")
    
    st.markdown("---")
    st.markdown("### 🟢 Status")
    st.success("FAISS Connected")
    st.success("Groq API Ready")

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
