from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.vector_database.result import result_query
from db_utils import init_db, save_message, get_chat_history, load_conversation_messages, delete_conversation
import uuid

app = FastAPI()

init_db()

templates = Jinja2Templates(directory="template")

app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    conversation_id: str
    message: str

@app.get("/")
def serve_chat_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
def chat_endpoint(chat_request: ChatRequest):
    conversation_id = chat_request.conversation_id or str(uuid.uuid4())  
    user_message = chat_request.message
    
    save_message("Bạn", user_message, conversation_id)
    
    response = result_query(user_message)
    save_message("Chatbot", response, conversation_id)
    
    return {"conversation_id": conversation_id, "response": response}

@app.get("/history")
def get_history():
    conversations = get_chat_history()
    return [{"conversation_id": conv_id, "title": title or f"Cuộc trò chuyện {conv_id[:8]}"} for conv_id, created_at, title in conversations]

@app.get("/conversation/{conversation_id}")
def get_conversation(conversation_id: str):
    """Lấy tất cả tin nhắn của một cuộc trò chuyện"""
    messages = load_conversation_messages(conversation_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"conversation_id": conversation_id, "messages": messages}

@app.post("/new_chat")
def new_chat():
    """Tạo một cuộc trò chuyện mới"""
    new_conv_id = str(uuid.uuid4()) 
    save_message("System", "Conversation started", new_conv_id)
    return {"conversation_id": new_conv_id}

@app.delete("/conversation/{conversation_id}")
async def delete_conversation_endpoint(conversation_id: str):
    """API endpoint để xóa một cuộc trò chuyện"""
    success = delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete conversation")
    return {"status": "success", "message": "Conversation deleted"}