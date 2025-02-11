let currentConversationId = null;

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('vi-VN');
}

async function deleteConversation(conversationId, event) {
    event.stopPropagation();
    
    try {
        const response = await fetch(`/conversation/${conversationId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            if (conversationId === currentConversationId) {
                await startNewChat();
            }
            await loadChatHistory();
        } else {
            throw new Error('Failed to delete conversation');
        }
    } catch (error) {
        console.error('Error deleting conversation:', error);
        alert('Không thể xóa cuộc trò chuyện. Vui lòng thử lại.');
    }
}

async function loadChatHistory() {
    try {
        const response = await fetch('/history');
        const data = await response.json();
        const conversationList = document.getElementById("conversationList");
        conversationList.innerHTML = "";
        
        data.forEach(chat => {
            const chatItem = document.createElement("div");
            chatItem.className = "chat-item";
            
            const title = chat.title || `Cuộc trò chuyện ${chat.conversation_id.substring(0, 8)}`;
            const timestamp = formatTimestamp(chat.created_at);
            
            chatItem.innerHTML = `
                <div class="chat-content" onclick="loadChat('${chat.conversation_id}')">
                    <div class="chat-title">${title}</div>
                </div>
                <button class="delete-btn" onclick="deleteConversation('${chat.conversation_id}', event)">
                    <img src="../static/assets/remove.png" 
                        alt="Xóa" width="20" 
                        style="filter: brightness(0) saturate(100%) invert(100%);">
                </button>
            `;
            
            conversationList.appendChild(chatItem);
        });
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

async function startNewChat() {
    try {
        const response = await fetch('/new_chat', { method: 'POST' });
        const data = await response.json();
        currentConversationId = data.conversation_id;
        
        document.getElementById("chatContent").innerHTML = `
            <div class="chat_side bot-message"> 
                <img src="../static/assets/chatbot_conversational_ai_virtual_assistant_automated_chat_messaging_bot_icon_260869.png" 
                    alt="Chatbot" width="40" 
                    style="filter: brightness(0) saturate(100%) invert(100%);">    
                Xin chào, tôi có thể giúp gì cho bạn?
            </div>
        `;
        
        await loadChatHistory();
    } catch (error) {
        console.error('Error starting new chat:', error);
    }
}

async function loadChat(chatId) {
    try {
        currentConversationId = chatId;
        const response = await fetch(`/conversation/${chatId}`);
        const data = await response.json();
        
        const messages = data.messages;
        
        const chatContent = document.getElementById("chatContent");
        chatContent.innerHTML = "";
        
        messages.forEach(msg => {
            const messageDiv = document.createElement("div");
            messageDiv.className = `chat_side ${msg.sender === "Chatbot" ? 'bot-message' : 'user-message'}`;
            
            const timestamp = formatTimestamp(msg.timestamp);
            
            messageDiv.innerHTML = `
                <div class="message-header">
                    <img src="../static/assets/${msg.sender === "Chatbot" ? 
                        'chatbot_conversational_ai_virtual_assistant_automated_chat_messaging_bot_icon_260869.png' : 
                        'user-icon.png'}" 
                        alt="${msg.sender}" width="40" 
                        style="filter: brightness(0) saturate(100%) invert(100%);">
                </div>
                <div class="message-content">
                    <pre style="white-space: pre-wrap; font-family: inherit; margin: 0;">${msg.message}</pre>
                </div>
            `;
            
            chatContent.appendChild(messageDiv);
        });
        
        chatContent.scrollTop = chatContent.scrollHeight;
    } catch (error) {
        console.error('Error loading chat:', error);
        document.getElementById("chatContent").innerHTML = `
            <div class="chat_side bot-message">
                <img src="../static/assets/chatbot_conversational_ai_virtual_assistant_automated_chat_messaging_bot_icon_260869.png" 
                    alt="Chatbot" width="40" 
                    style="filter: brightness(0) saturate(100%) invert(100%);">
                Xin lỗi, không thể tải tin nhắn. Vui lòng thử lại.
            </div>
        `;
    }
}
function handleKeyPress(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
}

async function sendMessage() {
    const userInput = document.getElementById("userInput");
    const message = userInput.value.trim();
    const sendButton = document.querySelector(".btn_send");
    
    if (!message) return;
    userInput.disabled = true;
    sendButton.disabled = true;

    const originalButtonContent = sendButton.innerHTML;
    sendButton.innerHTML = `
        <div class="loading-spinner">
            <svg class="spinner" viewBox="0 0 50 50">
                <circle class="spinner-path" cx="25" cy="25" r="20" fill="none" stroke-width="5"></circle>
            </svg>
        </div>
    `;
    
    if (!currentConversationId) {
        const response = await fetch('/new_chat', { method: 'POST' });
        const data = await response.json();
        currentConversationId = data.conversation_id;
    }

    const timestamp = new Date().toLocaleString('vi-VN');
    const messageDiv = document.createElement("div");
    messageDiv.className = "chat_side user-message";
    messageDiv.innerHTML = `
        <div class="message-header">
            <img src="../static/assets/user-icon.png" 
                alt="User" width="40" 
                style="filter: brightness(0) saturate(100%) invert(100%);">
        </div>
        <div class="message-content">
            <pre style="white-space: pre-wrap; font-family: inherit; margin: 0;">${message}</pre>
        </div>
    `;
    
    document.getElementById("chatContent").appendChild(messageDiv);
    userInput.value = "";

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                conversation_id: currentConversationId,
                message: message
            })
        });
        
        const data = await response.json();
        const botMessageDiv = document.createElement("div");
        botMessageDiv.className = "chat_side bot-message";
        botMessageDiv.innerHTML = `
            <div class="message-header">
                <img src="../static/assets/chatbot_conversational_ai_virtual_assistant_automated_chat_messaging_bot_icon_260869.png" 
                    alt="Chatbot" width="40" 
                    style="filter: brightness(0) saturate(100%) invert(100%);">
            </div>
            <div class="message-content">
                <pre style="white-space: pre-wrap; font-family: inherit; margin: 0;">${data.response}</pre>
            </div>
        `;
        
        document.getElementById("chatContent").appendChild(botMessageDiv);
        document.getElementById("chatContent").scrollTop = document.getElementById("chatContent").scrollHeight;
        
        await loadChatHistory();
        
    } catch (error) {
        console.error('Error:', error);
        const errorDiv = document.createElement("div");
        errorDiv.className = "chat_side bot-message";
        errorDiv.innerHTML = `
            <div class="message-header">
                <img src="../static/assets/chatbot_conversational_ai_virtual_assistant_automated_chat_messaging_bot_icon_260869.png" 
                    alt="Chatbot" width="40" 
                    style="filter: brightness(0) saturate(100%) invert(100%);">
            </div>
            <div class="message-content">Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại.</div>
        `;
        document.getElementById("chatContent").appendChild(errorDiv);
    } finally {
        sendButton.innerHTML = originalButtonContent;
        sendButton.disabled = false;
        userInput.disabled = false;
    }
}

document.addEventListener("DOMContentLoaded", function() {
    loadChatHistory();
    
    const sidebar = document.querySelector(".main__sidebar");
    const mainChat = document.querySelector(".main__chat");
    const toggleBtn = document.querySelector(".btnhisimg");
    const showSidebarBtn = document.querySelector(".show-sidebar-btn");

    function hideSidebar() {
        sidebar.classList.add("hidden");
        mainChat.classList.add("expanded");
        showSidebarBtn.classList.add("visible");
    }

    function showSidebar() {
        sidebar.classList.remove("hidden");
        mainChat.classList.remove("expanded");
        showSidebarBtn.classList.remove("visible");
    }

    toggleBtn.addEventListener("click", hideSidebar);
    showSidebarBtn.addEventListener("click", showSidebar);
});