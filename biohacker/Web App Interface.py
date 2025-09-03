import streamlit as st
from biohacker.no_expertise import general_assistant


st.set_page_config(page_title="Smarter Agents. Wilder Biology.", page_icon="💬", layout="wide")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_uploader" not in st.session_state:
    st.session_state.show_uploader = False

# --- Chat Messages ---
st.title("💬 Smarter Agents. Wilder Biology.")
for role, content in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(content)

# --- Upload Button + Conditional Uploader ---
if st.button("📂 Upload Documents"):
    st.session_state.show_uploader = not st.session_state.show_uploader

if st.session_state.show_uploader:
    uploaded_files = st.file_uploader(
        "Choose files",
        type=["txt", "pdf", "docx", "csv","py"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) uploaded!")

# --- Chat Input at Bottom ---
user_input = st.chat_input("Type your message here...")

# --- Process Input ---
if user_input:
    st.session_state.messages.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # Route the input through the general assistant tool
    reply = general_assistant(user_input)

    # Save the assistant reply
    st.session_state.messages.append(("assistant", reply))
    with st.chat_message("assistant"):
        st.markdown(reply)

