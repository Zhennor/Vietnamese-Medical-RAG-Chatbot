import streamlit as st
from app.vector_database.result import result_query
from db_utils import init_db, save_message, get_chat_history
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

if 'conversations' not in st.session_state:
    st.session_state.conversations = {}
if 'current_conversation' not in st.session_state:
    st.session_state.current_conversation = None

with st.sidebar:
    if st.button("New Chat"):
        new_conv_id = str(uuid.uuid4())
        st.session_state.conversations[new_conv_id] = {
            'title': f"Cuộc trò chuyện {len(st.session_state.conversations) + 1}",
            'messages': [],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.current_conversation = new_conv_id 

    st.markdown("### Lịch sử trò chuyện")
    for conv_id, conv_data in sorted(st.session_state.conversations.items(), key=lambda x: x[1]['created_at'], reverse=True):
        if st.button(conv_data['title'], key=f"conv_{conv_id}"):
            st.session_state.current_conversation = conv_id  

if st.session_state.current_conversation is None:
    if st.session_state.conversations:
        st.session_state.current_conversation = list(st.session_state.conversations.keys())[0]
    else:
        new_conv_id = str(uuid.uuid4())
        st.session_state.conversations[new_conv_id] = {
            'title': "Cuộc trò chuyện 1",
            'messages': [],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.current_conversation = new_conv_id

current_conv = st.session_state.conversations[st.session_state.current_conversation]

user_input = st.text_input("Nhập câu hỏi của bạn:", key=f"input_{st.session_state.current_conversation}")

if st.button("Gửi", key=f"send_{st.session_state.current_conversation}"):
    if user_input:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_conv['messages'].append({'sender': 'Bạn', 'message': user_input, 'timestamp': timestamp})
        save_message("Bạn", user_input, st.session_state.current_conversation)
        response = result_query(user_input)
        current_conv['messages'].append({'sender': 'Chatbot', 'message': response, 'timestamp': timestamp})
        save_message("Chatbot", response, st.session_state.current_conversation)

        if len(current_conv['messages']) == 2:
            current_conv['title'] = user_input[:30] + "..." if len(user_input) > 30 else user_input

for message in current_conv['messages']:
    if message['sender'] == "Bạn":
        st.markdown(f"""
            <div class="user-message">
                <strong>{message['sender']}:</strong> {message['message']}<br>
                <span class="timestamp">{message['timestamp']}</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="bot-message">
                <strong>{message['sender']}:</strong> {message['message']}<br>
                <span class="timestamp">{message['timestamp']}</span>
            </div>
        """, unsafe_allow_html=True)
