import streamlit as st
from app.vector_database.result import result_query

st.title("Chatbot Hỗ Trợ Y Tế")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Nhập câu hỏi của bạn:", "")

if st.button("Gửi"):
    if user_input:
        st.session_state.chat_history.append(("Bạn", user_input))

        response = result_query(user_input)
        st.session_state.chat_history.append(("Chatbot", response))

for sender, message in st.session_state.chat_history:
    if sender == "Bạn":
        st.markdown(f"**{sender}:** {message}")
    else:
        st.markdown(f"**{sender}:** {message}")