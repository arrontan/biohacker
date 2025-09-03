import streamlit as st
from datetime import datetime

st.set_page_config(page_title="BioHackers 🧬", page_icon="🧬", layout="wide")

# --- Initialize session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploads" not in st.session_state:
    st.session_state.uploads = []
if "pending_input" not in st.session_state:
    st.session_state.pending_input = ""

# --- Sidebar ---
st.sidebar.title("Conversation History")
for role, content, timestamp in st.session_state.messages:
    st.sidebar.markdown(f"**{role.capitalize()} ({timestamp})**: {content}")

st.title("🧬 BioHackers Chat Assistant")

# --- Chat display ---
for role, content, timestamp in st.session_state.messages:
    with st.chat_message(role, avatar="🧬" if role == "user" else "🤖"):
        st.markdown(content)

# --- Chat input row (input + upload inside + send button) ---
with st.container():
    col1, col2 = st.columns([0.9, 0.1])

    with col1:
        # Wrap uploader + input together
        uploaded_files = st.file_uploader(
            "Upload",
            type=["txt", "pdf", "docx", "csv"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="file_input"
        )

        st.session_state.pending_input = st.text_input(
            "💬 Type your message here...",
            value=st.session_state.pending_input,
            label_visibility="collapsed",
            key="chat_input_box"
        )

    with col2:
        send_clicked = st.button("✈️", key="send_button")

# --- Handle uploads ---
if uploaded_files:
    timestamp = datetime.now().strftime("%H:%M:%S")
    for f in uploaded_files:
        if f not in st.session_state.uploads:
            st.session_state.uploads.append(f)
            st.session_state.messages.append(
                ("user", f"📂 Uploaded: **{f.name}**", timestamp)
            )

# --- Handle sending messages ---
if send_clicked and st.session_state.pending_input.strip():
    user_input = st.session_state.pending_input.strip()
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Save user message
    st.session_state.messages.append(("user", user_input, timestamp))

    # Generate bot response (placeholder echo)
    bot_response = f"🤖 Echo: {user_input}"
    st.session_state.messages.append(("assistant", bot_response, timestamp))

    # Reset input field
    st.session_state.pending_input = ""
    st.experimental_rerun()

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
    .stChatMessage.user, .stChatMessage.assistant {
        color: #ffffff !important;
    }
    .stChatMessage.user {
        background-color: rgba(0, 200, 255, 0.15);
        border: 1px solid #00c8ff;
        border-radius: 12px;
        padding: 10px;
    }
    .stChatMessage.assistant {
        background-color: rgba(0, 255, 100, 0.15);
        border: 1px solid #00ff64;
        border-radius: 12px;
        padding: 10px;
    }

    /* Force all text in chat to white */
    .stChatMessage div, .stChatMessage p, .stChatMessage span, .stMarkdown {
        color: #ffffff !important;
    }

    /* --- Fix uploader --- */
    div[data-testid="stFileUploaderDropzone"] {
        display: none !important; /* hide drag zone */
    }

    div[data-testid="stFileUploader"] {
        position: absolute;
        left: 10px;
        top: 50%;
        transform: translateY(-50%);
        z-index: 5;
    }

    div[data-testid="stFileUploader"] > label {
        border: 2px solid #666;
        border-radius: 50%;
        width: 30px !important;
        height: 30px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        background: #222;
        padding: 0 !important;
        margin: 0 !important;
    }

    div[data-testid="stFileUploader"] label div {
        display: none !important;
    }

    div[data-testid="stFileUploader"] > label:after {
        content: "+";
        color: #ffffff;
        font-weight: bold;
        font-size: 18px;
    }

    /* Chat input box with left padding (for + button) */
    input[type="text"] {
        background: #111 !important;
        color: #ffffff !important;
        border: 1px solid #444 !important;
        border-radius: 20px !important;
        padding: 10px 15px 10px 45px !important; /* left padding for + */
        width: 100% !important;
    }

    /* Send button (✈️) */
    div[data-testid="stButton"] > button {
        width: 45px;
        height: 40px;
        border-radius: 50%;
        background: #00c8ff;
        color: #000;
        font-size: 18px;
        border: none;
        cursor: pointer;
    }
    div[data-testid="stButton"] > button:hover {
        background: #00a6d1;
        color: #fff;
    }

    /* Title color */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
