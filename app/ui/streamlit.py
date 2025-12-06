import streamlit as st
import os
import sys
import asyncio
import tempfile

# ✅ Add project root to Python import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from loguru import logger
from app.core.worflow import get_workflow

# Page Config
st.set_page_config(page_title="Medical Assistant", layout="centered")
st.title("🧠 Medical Assistant (Multi-Modal)")
st.write("Upload a PDF, an Image, or ask a medical question.")

# Initialize Session State
# History structure: list of tuples (Sender, Message, Audio_Path)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

workflow = get_workflow()

# --- Async Helper Functions ---

async def ask_text_question(question, session_id, user_id, language):
    response = await workflow.run_conversation(
        user_input=question,
        session_id=session_id,
        user_id=user_id,
        language=language,
        image_url=None,
        pdf_url=None,
        audio_url=None
    )
    # Return both text and the specific audio path from the response
    return response.get("assistant_response", ""), response.get("audio_path", None)

async def analyze_pdf(pdf_path, session_id, user_id, language):
    response = await workflow.run_conversation(
        user_input="Please analyze this PDF summary", 
        session_id=session_id,
        user_id=user_id,
        language=language,
        image_url=None,
        pdf_url=pdf_path,
        audio_url=None
    )
    return response.get("assistant_response", ""), response.get("audio_path", None)

async def analyze_image(img_path, session_id, user_id, language):
    response = await workflow.run_conversation(
        user_input="Please analyze this medical image",
        session_id=session_id,
        user_id=user_id,
        language=language,
        image_url=img_path,
        pdf_url=None,
        audio_url=None
    )
    return response.get("assistant_response", ""), response.get("audio_path", None)

# --- Sidebar / Configuration ---
with st.sidebar:
    st.header("Settings")
    language = st.selectbox("🌐 Language", ["en", "kn", "hi"]) # Fixed 'hn' to 'hi' (Hindi standard code)
    session_id = "streamlit_session"
    user_id = "streamlit_user"
    
    # Optional: Button to clear history
    if st.button("Clear History"):
        st.session_state.chat_history = []
        st.rerun()

# --- Input Area ---
col1, col2 = st.columns(2)

with col1:
    uploaded_pdf = st.file_uploader("📄 Upload PDF", type=["pdf"], key="pdf_uploader")

with col2:
    uploaded_image = st.file_uploader("🖼️ Upload Image", type=["png", "jpg", "jpeg"], key="img_uploader")

user_input = st.text_input("💬 Ask a question", key="text_input")

# --- Processing Logic ---

# 1. Text Input
if user_input:
    with st.spinner("Thinking & Generating Audio..."):
        # Unpack text AND audio
        text_resp, audio_path = asyncio.run(ask_text_question(user_input, session_id, user_id, language))
        
        # Store: (Sender, Text, AudioPath)
        st.session_state.chat_history.append(("You", user_input, None))
        st.session_state.chat_history.append(("AI", text_resp, audio_path))

# 2. PDF Input
if uploaded_pdf:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(uploaded_pdf.read())
        temp_path = temp_pdf.name

    with st.spinner("Analyzing PDF & Generating Audio..."):
        text_resp, audio_path = asyncio.run(analyze_pdf(temp_path, session_id, user_id, language))
        
        st.session_state.chat_history.append(("PDF", f"Uploaded: {uploaded_pdf.name}", None))
        st.session_state.chat_history.append(("AI", text_resp, audio_path))

# 3. Image Input
if uploaded_image:
    st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
        temp_img.write(uploaded_image.read())
        temp_img_path = temp_img.name

    with st.spinner("Analyzing Image & Generating Audio..."):
        text_resp, audio_path = asyncio.run(analyze_image(temp_img_path, session_id, user_id, language))
        
        st.session_state.chat_history.append(("Image", "Uploaded Medical Image", None))
        st.session_state.chat_history.append(("AI", text_resp, audio_path))

# --- Display History ---
st.divider()
st.markdown("### 🗂 Chat History")

# Loop through history (now with 3 items per entry)
for sender, message, audio_file in st.session_state.chat_history:
    
    if sender == "AI":
        st.markdown(f"**🤖 Assistant:** {message}")
        
        # ✅ Check if audio path exists and play it
        if audio_file and os.path.exists(audio_file):
            try:
                st.audio(audio_file, format="audio/mp3")
            except Exception as e:
                st.error(f"Could not play audio: {e}")
                
    elif sender == "PDF":
        st.info(f"**📄 PDF:** {message}")
    elif sender == "Image":
        st.warning(f"**🖼️ Image:** {message}")
    else:
        st.markdown(f"**🧑‍💻 You:** {message}")