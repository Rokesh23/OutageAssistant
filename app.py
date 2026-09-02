import re
import streamlit as st

from config import *
from llm import ask_llm_stream
from rag import retrieve, metadata

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Outage RCA Assistant", page_icon="🤖", layout="wide"
)

# ==========================================================
# EXTRACT INCIDENT NUMBER
# ==========================================================

def extract_incident_number(question):
    match = re.search(r"(INC\d+|QA-INC-\d+)", question, re.IGNORECASE)
    if match:
        return match.group(0).upper()
    return "Not Specified"


# ==========================================================
# SESSION STATE
# ==========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================================
# SIDEBAR (DYNAMIC STATS)
# ==========================================================

# Calculate actual statistics dynamically from metadata
total_docs = len(set(item.get("source", "") for item in metadata)) if metadata else 0
unique_incidents = len(set(item.get("incident") for item in metadata if item.get("incident") and item.get("incident") != "GENERAL")) if metadata else 0
total_chunks = len(metadata) if metadata else 0

with st.sidebar:
    st.title("🤖 Outage Assistant")
    st.caption("AI Powered RCA Knowledge Assistant")

    st.divider()

    st.subheader("📊 Knowledge Base")
    st.success(f"📄 Documents : {total_docs}")
    st.success(f"📑 Sections : {total_chunks}")
    st.success(f"🚨 Incidents : {unique_incidents}")

    st.divider()

    st.subheader("🟢 Status")
    st.success("FAISS Connected")
    st.success("Ollama Running")

    st.divider()

    st.subheader("🔒 Offline AI")
    st.info("""
This AI searches your RCA documents locally.

✅ No internet required

✅ No RCA data leaves your computer

✅ Powered by Ollama + FAISS
""")

    st.divider()

    st.subheader("💡 Example Questions")
    st.markdown("""
- What caused INC0176274?
- Show total incidents
- Resolution for INC0191705
- List SSL related incidents
- Which incident involved Elasticsearch?
""")

# ==========================================================
# TITLE
# ==========================================================

st.title("🤖 Outage RCA Assistant")
st.caption(
    "Ask questions about outages, root causes, resolutions and lessons learned."
)

# ==========================================================
# DISPLAY CHAT HISTORY
# ==========================================================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================================================
# CHAT INPUT & RESPONSE GENERATION
# ==========================================================

question = st.chat_input("Ask a question about your RCA documents...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        context, results, confidence = retrieve(question)

        # ==================================================
        # NO MATCH FOUND
        # ==================================================
        if not context or context.strip() == "":
            incident = extract_incident_number(question)
            answer = f"""
## ❌ No Matching RCA Found

**Incident Number / Subject:**  
{incident if incident != 'Not Specified' else 'Not Found'}

Sorry, I could not find any RCA document related to your query in the indexed records.

### Possible Reasons
• The incident or keyword does not exist in the uploaded documents.  
• The RCA document has not been uploaded or indexed yet.

### Suggestions
✅ Run `python ingest.py` to index new documents.  
✅ Verify the Incident Number or technical key terms.
"""
            st.markdown(answer)

        # ==================================================
        # MATCH FOUND - STREAM RESPONSE
        # ==================================================
        else:
            answer = st.write_stream(ask_llm_stream(question, context))

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

# ==========================================================
# CUSTOM DARK THEME CSS
# ==========================================================

st.markdown(
    """
<style>

/* ==========================================
   GLOBAL APP & BACKGROUND
========================================== */

.stApp {
    background-color: #000000 !important;
    color: #FFFFFF !important;
}

/* Force text, captions, and headings to white */
.stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp span, .stApp label, [data-testid="stCaptionContainer"] {
    color: #FFFFFF !important;
}

h1 {
    color: #FFFFFF !important;
    font-weight: 800;
    font-size: 48px;
}

/* ==========================================
   MAIN CONTAINER
========================================== */

.block-container {
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* ==========================================
   SIDEBAR
========================================== */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #0F4C81 0%,
        #1976D2 60%,
        #42A5F5 100%
    );
    color: white;
    border-right: 3px solid rgba(255,255,255,.15);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,.25);
}

[data-testid="stSidebar"] .stAlert {
    border-radius: 14px;
    background: rgba(255,255,255,.12);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,.18);
}

/* ==========================================
   CHAT MESSAGES
========================================== */

[data-testid="stChatMessage"] {
    background-color: #121212 !important;
    border: 1px solid #2D2D2D !important;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 18px;
    color: #FFFFFF !important;
}

[data-testid="stChatMessage"] * {
    color: #FFFFFF !important;
}

/* ==========================================
   CHAT INPUT
========================================== */

[data-testid="stChatInput"] {
    background-color: #1E1E1E !important;
    border-radius: 18px;
    border: 1px solid #333333 !important;
    padding: 8px;
}

div[data-baseweb="input"] {
    background-color: #1E1E1E !important;
}

input {
    font-size: 17px !important;
    color: #FFFFFF !important;
}

/* ==========================================
   REMOVE STREAMLIT HEADER & FOOTER
========================================== */

header {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

[data-testid="stToolbar"] {
    background: transparent;
}

</style>
""",
    unsafe_allow_html=True,
)