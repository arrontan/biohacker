import streamlit as st
from datetime import datetime

st.set_page_config(page_title="BioHackers 🧬", page_icon="🧬", layout="wide")

# --- Initialize session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploads" not in st.session_state:
    st.session_state.uploads = []

# --- Sidebar ---
st.sidebar.title("Conversation History")
for role, content, timestamp in st.session_state.messages:
    st.sidebar.markdown(f"**{role.capitalize()} ({timestamp})**: {content}")

st.title("🧬 BioHackers Chat Assistant")

# --- Chat display ---
for role, content, timestamp in st.session_state.messages:
    with st.chat_message(role, avatar="🧬" if role == "user" else "🤖"):
        st.markdown(content)

# --- Chat input with plus icon ---
with st.container():
    col1, col2 = st.columns([0.15, 0.85])

    with col1:
        uploaded_files = st.file_uploader(
            "📂", type=["txt", "pdf", "docx", "csv"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="file_input"
        )

    with col2:
        user_input = st.chat_input("💬 Type your message here...")

# --- Handle uploads ---
if uploaded_files:
    timestamp = datetime.now().strftime("%H:%M:%S")
    for f in uploaded_files:
        if f not in st.session_state.uploads:
            st.session_state.uploads.append(f)
            st.session_state.messages.append(("user", f"📂 Uploaded: **{f.name}**", timestamp))

# --- Handle text ---
if user_input:
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append(("user", user_input, timestamp))
    bot_response = f"🤖 Echo: {user_input}"
    st.session_state.messages.append(("assistant", bot_response, timestamp))

# --- Custom styling ---
st.markdown(
    """
    <style>
    /* Full black background */
    .stApp {
        background-color: #000000 !important;
    }

    /* Sidebar background (dark gray) */
    section[data-testid="stSidebar"] {
        background-color: #111111 !important;
        color: #ffffff !important;
    }

    /* Chat bubbles */
    .stChatMessage.user {
        background-color: rgba(0, 200, 255, 0.15); /* neon cyan tint */
        border: 1px solid #00c8ff;
        border-radius: 12px;
        padding: 10px;
        color: #e0e0e0;
    }
    .stChatMessage.assistant {
        background-color: rgba(0, 255, 100, 0.15); /* neon green tint */
        border: 1px solid #00ff64;
        border-radius: 12px;
        padding: 10px;
        color: #e0e0e0;
    }

    /* File uploader styled as + button */
    div[data-testid="stFileUploader"] > label {
        border: 2px solid #666;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 24px;
        background: #222;
    }
    div[data-testid="stFileUploader"] > label:after {
        content: "+";
        color: #ffffff;
        font-weight: bold;
    }
    div[data-testid="stFileUploader"] span {
        display: none;
    }

    /* Title color */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

