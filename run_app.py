import streamlit as st
from app.vector_database.result import result_query
from db_utils import init_db, save_message, get_chat_history, load_conversation_messages
from datetime import datetime
import uuid

init_db()

st.set_page_config(page_title="Chatbot Hỗ Trợ Y Tế", layout="wide")

st.markdown("""
    <style>
        /* Hide main menu */
        #MainMenu {visibility: hidden;}

        /* Sidebar styling */
        .sidebar-chat {
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            cursor: pointer;
            background-color: #2E2E2E;
            color: white;
        }
        .sidebar-chat:hover {
            background-color: #1E1E1E;
        }
        .selected-chat {
            background-color: #1E1E1E;
        }

        /* Message styling */
        .user-message, .bot-message {
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .user-message { background-color: #2E2E2E; }
        .bot-message { background-color: #1E1E1E; }
        .timestamp { font-size: 0.8em; color: #888; }

        /* Input styling */
        .stTextInput>div>div>input {
            background-color: #2E2E2E;
            color: white;
            border: 1px solid #4A4A4A;
            border-radius: 5px;
        }
        .stButton>button {
            background-color: #4A4A4A;
            color: white;
            border: none;
            border-radius: 5px;
        }
        .stButton>button:hover {
            background-color: #666666;
        }
    </style>
""", unsafe_allow_html=True)

if 'current_conversation' not in st.session_state:
    st.session_state.current_conversation = None

with st.sidebar:
    if st.button("New Chat"):
        new_conv_id = str(uuid.uuid4())
        st.session_state.current_conversation = new_conv_id
        save_message("System", "Conversation started", new_conv_id)

    st.markdown("### Lịch sử trò chuyện")
    conversations = get_chat_history() 
    
    for conv_id, created_at, title in conversations:
        display_title = title if title else f"Cuộc trò chuyện {conv_id[:8]}"
        if st.button(display_title, key=f"conv_{conv_id}"):
            st.session_state.current_conversation = conv_id

if st.session_state.current_conversation is None:
    conversations = get_chat_history()
    if conversations:
        st.session_state.current_conversation = conversations[0][0]  
    else:
        new_conv_id = str(uuid.uuid4())
        st.session_state.current_conversation = new_conv_id
        save_message("System", "Conversation started", new_conv_id)

user_input = st.text_input("Nhập câu hỏi của bạn:", key=f"input_{st.session_state.current_conversation}")

if st.button("Gửi", key=f"send_{st.session_state.current_conversation}"):
    if user_input:
        save_message("Bạn", user_input, st.session_state.current_conversation)
        response = result_query(user_input)
        save_message("Chatbot", response, st.session_state.current_conversation)

messages = load_conversation_messages(st.session_state.current_conversation)
for message in messages:
    if message['sender'] == "System":  
        continue
    
    st.markdown(f"""
        <div class="{message['sender'].lower()}-message">
            <strong>{message['sender']}:</strong> {message['message']}<br>
            <span class="timestamp">{message['timestamp']}</span>
        </div>
    """, unsafe_allow_html=True)