# Custom Dark Theme CSS with dark bottom bar container
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

    /* Block Container Padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 6rem !important;
        max-width: 100% !important;
    }

    /* Hide Streamlit default UI elements */
    header[data-testid="stHeader"] { visibility: hidden; height: 0px !important; display: none !important; }
    #MainMenu { visibility: hidden; display: none !important; }
    footer { visibility: hidden; display: none !important; }
    div[data-testid="stToolbar"] { visibility: hidden; display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }

    /* Header Banner */
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

    /* Metric Cards */
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

    /* Buttons */
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

    /* Incident Table */
    .incident-table-container {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px;
        padding: 10px;
        font-size: 0.78rem;
        color: #f8fafc !important;
    }

    /* Chat Messages */
    div[data-testid="stChatMessage"] {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #f8fafc !important;
    }

    /* FIX: Dark Background for the entire Bottom Input Dock Container */
    div[data-testid="stBottom"], 
    div[data-testid="stChatInputContainer"], 
    .stChatInput {
        background-color: #0b1329 !important;
        border-top: 1px solid #1e293b !important;
    }

    /* Fixed Dark Chat Input Textarea Box */
    div[data-testid="stChatInput"] > div {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stChatInput"] textarea {
        color: #f8fafc !important;
        background-color: transparent !important;
    }
    </style>
"""
