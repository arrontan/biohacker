import os
import uuid
import streamlit as st
from biohacker_agent import biohacker_agent
from software_assistant import software_assistant
import asyncio
import threading
import queue
import time

st.set_page_config(page_title=" Biohacker ", page_icon="🧬", layout="wide")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_uploader" not in st.session_state:
    st.session_state.show_uploader = False
if "uploaded_files_info" not in st.session_state:
    st.session_state.uploaded_files_info = []

# ensure uploads dir exists
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
# Limit how many bytes we send to the agent to avoid memory/LLM input overflow
MAX_SEND_BYTES = 200_000  # ~200 KB, adjustable

# Persistent intro instructions (stays at top)
intro_md = """
**Tell me more about your research!**

I can help you:

1. Review the literature, try:
    - Best tools for simulating molecular dynamics?
    - How can I compare between different homologs of a protein?
    - What visualisation is best used for showing gene expression data?

2. Guide you through software installation, setup, and execution, try:
    - Molecular dynamics: GROMACS tutorial
    - Sequence analysis: ClustalW tutorial
    - Data visualisation: Volcano plot tutorial in R

3. Ask me questions about basic biology
4. Help you with file management, workflow automation and scripting
    - Upload a document for analysis or cleaning 
    - Clear folders used in this runtime
"""

st.markdown(intro_md)

# Render chat messages after the intro
for role, content in st.session_state.messages:
     with st.chat_message(role):
          st.markdown(content)


# Sidebar upload button 

st.sidebar.title("🧬 Biohacker")
st.sidebar.markdown("<br>", unsafe_allow_html=True)

if st.sidebar.button("📂 Upload Documents"):
    st.session_state.show_uploader = not st.session_state.show_uploader

if st.session_state.show_uploader:
    uploaded_files = st.sidebar.file_uploader(
        "Choose files",
        type=["txt", "pdf", "docx", "csv"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        # save uploaded files to uploads dir and keep metadata in session
        for uf in uploaded_files:
            # create a unique filename to avoid collisions
            fname = uf.name
            unique_name = f"{uuid.uuid4().hex}_{fname}"
            saved_path = os.path.join(UPLOAD_DIR, unique_name)
            # write to disk
            with open(saved_path, "wb") as out_f:
                out_f.write(uf.getbuffer())

            # create a preview for small text-like files
            preview_text = None
            try:
                # attempt to decode small files as utf-8
                if uf.type.startswith("text") or fname.endswith(('.txt', '.csv')):
                    raw = uf.getvalue()
                    if isinstance(raw, bytes):
                        decoded = raw.decode("utf-8", errors="replace")
                    else:
                        decoded = str(raw)
                    preview_text = decoded[:1000]
            except Exception:
                preview_text = None

            st.session_state.uploaded_files_info.append(
                {"name": fname, "path": saved_path, "type": uf.type, "preview": preview_text}
            )

        st.sidebar.success(f"{len(uploaded_files)} file(s) uploaded and saved to uploads/")

st.sidebar.write("_Your files will appear here_")

file_names = [f["name"] for f in st.session_state.uploaded_files_info]
selected = None
if file_names:
    selected = st.sidebar.selectbox("Select a file", options=file_names)
    # show preview and a button to send to agent
    info = next((f for f in st.session_state.uploaded_files_info if f["name"] == selected), None)
    if info:
        st.sidebar.write(f"Path: {info['path']}")
        if info.get("preview"):
            st.sidebar.markdown("**Preview:**")
            st.sidebar.code(info["preview"])
        else:
            st.sidebar.write("No text preview available for this file type.")

        if st.sidebar.button("Send selected file to agent"):
            # Read small text files up to MAX_SEND_BYTES and include metadata; otherwise include path reference
            to_send = None
            truncated = False
            total_size = None
            try:
                if info['name'].endswith(('.txt', '.csv')):
                    total_size = os.path.getsize(info['path'])
                    with open(info['path'], 'r', encoding='utf-8', errors='replace') as r:
                        snippet = r.read(MAX_SEND_BYTES)
                        to_send = snippet
                        if total_size is not None and total_size > MAX_SEND_BYTES:
                            truncated = True
                else:
                    to_send = f"FILE_PATH:{info['path']}"
            except Exception:
                to_send = f"FILE_PATH:{info['path']}"

            # Build a simple shuttle for the agent
            shuttle = {
                "prompt": f"User uploaded file: {info['name']}",
                "file_name": info['name'],
                "file_content_or_path": to_send,
                "file_truncated": truncated,
                "file_total_size": total_size,
                "followup": None,
            }

            # Call the agent (it may accept a JSON string or object; use str() if needed)
            with st.spinner("Thinking..."):
                try:
                    reply = biohacker_agent(shuttle)
                except Exception:
                    reply = biohacker_agent(str(shuttle))
            st.session_state.messages.append(("assistant", reply))
            with st.chat_message("assistant"):
                st.markdown(reply)

user_input = st.chat_input("Type your message here...")

# --- Process Input ---
if user_input:
    st.session_state.messages.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # Route the input through the general assistant tool while showing a spinner
    with st.spinner("Thinking..."):
        try:
            reply = biohacker_agent(user_input)            
        except Exception as e:
            reply = f"[ERROR] {e}"

    st.session_state.messages.append(("assistant", str(reply)))
    with st.chat_message("assistant"):
        st.markdown(str(reply))

