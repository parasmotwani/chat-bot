import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
from datetime import datetime
import time # For the typing indicator

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Personal Chatbot!",
    page_icon="🤖",
    layout="centered",
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set up Google Gemini-Pro AI model
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('models/gemini-2.0-flash-thinking-exp-01-21')

# Initialize multiple chat sessions storage
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}  # Stores chat histories separately

# Initialize list of chat IDs
if "chat_ids" not in st.session_state:
    st.session_state.chat_ids = ["Chat 1"]  # Default first chat
    st.session_state.active_chat = "Chat 1"  # Currently selected chat

# If active chat session is missing, create one
if st.session_state.active_chat not in st.session_state.chat_sessions:
    st.session_state.chat_sessions[st.session_state.active_chat] = {
        "chat_session": model.start_chat(history=[]),
        "chat_history": []
    }

# Custom CSS for WhatsApp-style chat bubbles
st.markdown("""
    <style>
        .user-message {
            text-align: right;
            background-color: #dcf8c6;
            color: black;
            padding: 10px;
            border-radius: 10px;
            margin: 5px;
            width: fit-content;
            max-width: 80%;
            float: right;
            clear: both;
        }
        .assistant-message {
            text-align: left;
            background-color: #ebebeb;
            color: black;
            padding: 10px;
            border-radius: 10px;
            margin: 5px;
            width: fit-content;
            max-width: 80%;
            float: left;
            clear: both;
        }
    </style>
""", unsafe_allow_html=True)

# App title
st.title("🤖 Personal Chatbot")

# Chat session selector
col1, col2 = st.columns([4, 1])  # Adjust width ratio as needed

with col1:
    st.markdown("#### 💬 Select Chat") 
    selected_chat = st.selectbox("", st.session_state.chat_ids, index=st.session_state.chat_ids.index(st.session_state.active_chat), label_visibility="collapsed")

with col2:
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True) 
    if st.button("➕ New Chat"):
        new_chat_id = f"Chat {len(st.session_state.chat_ids) + 1}"
        st.session_state.chat_ids.append(new_chat_id)
        st.session_state.chat_sessions[new_chat_id] = {
            "chat_session": model.start_chat(history=[]),
            "chat_history": []
        }
        st.session_state.active_chat = new_chat_id
        st.rerun()



# Update active chat when selection changes
if selected_chat != st.session_state.active_chat:
    st.session_state.active_chat = selected_chat
    st.rerun()

# Get active chat session & history
chat_data = st.session_state.chat_sessions[st.session_state.active_chat]

# Display all chat history inside the main chat interface
for role, text, timestamp in chat_data["chat_history"]:
    if role == "User":
        st.markdown(f'<div class="user-message"><strong>You:</strong> {text} <br><small>{timestamp}</small></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-message"><strong>Bot:</strong> {text} <br><small>{timestamp}</small></div>', unsafe_allow_html=True)

# Chat input field
user_prompt = st.chat_input("Ask Gemini-Pro...")

if user_prompt:
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Display user message on the right (WhatsApp style)
    st.markdown(f'<div class="user-message"><strong>You:</strong> {user_prompt} <br><small>{timestamp}</small></div>', unsafe_allow_html=True)

    # Store user message
    chat_data["chat_history"].append(("User", user_prompt, timestamp))

    # Show typing indicator
    with st.spinner("Gemini-Pro is typing..."):
        time.sleep(1.5)  # Simulate typing delay

    # Get AI response
    gemini_response = chat_data["chat_session"].send_message(user_prompt)
    ai_response_text = gemini_response.text

    # Display AI response on the left
    st.markdown(f'<div class="assistant-message"><strong>Bot:</strong> {ai_response_text} <br><small>{timestamp}</small></div>', unsafe_allow_html=True)

    # Store AI response in history
    chat_data["chat_history"].append(("Assistant", ai_response_text, timestamp))

# Function to generate chat history text for download
def generate_chat_text(chat_id):
    chat_text = f"Chat History - {chat_id}\n\n"
    for entry in st.session_state.chat_sessions[chat_id]["chat_history"]:
        role, text, timestamp = entry
        chat_text += f"[{timestamp}] {role}: {text}\n\n"
    return chat_text

# Allow users to download chat history for the selected chat
chat_text = generate_chat_text(st.session_state.active_chat)
st.download_button(
    label="📥 Download Chat History",
    data=chat_text,
    file_name=f"{st.session_state.active_chat}_history.txt",
    mime="text/plain"
)

# Button to clear current chat history
if st.button("🗑️ Clear Current Chat"):
    st.session_state.chat_sessions[st.session_state.active_chat]["chat_history"] = []
    st.session_state.chat_sessions[st.session_state.active_chat]["chat_session"] = model.start_chat(history=[])
    st.rerun()
