# db_utils.py
import sqlite3
from datetime import datetime
import os

def init_db():
    """Khởi tạo database và tạo bảng chat_history nếu chưa tồn tại"""
    try:
        conn = sqlite3.connect('app/database/chat_history.db')
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS chat_history
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            timestamp DATETIME,
            sender TEXT,
            message TEXT)
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
        raise

def save_message(sender, message, conversation_id):
    """Lưu tin nhắn vào database"""
    conn = sqlite3.connect('app/database/chat_history.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('''
        INSERT INTO chat_history 
        (conversation_id, timestamp, sender, message) 
        VALUES (?, ?, ?, ?)
    ''', (conversation_id, timestamp, sender, message))
    conn.commit()
    conn.close()

def get_chat_history(conversation_id=None):
    """Lấy lịch sử chat theo conversation_id hoặc danh sách các cuộc trò chuyện"""
    conn = sqlite3.connect('app/database/chat_history.db')
    c = conn.cursor()
    
    if conversation_id:
        c.execute('''
            SELECT timestamp, sender, message 
            FROM chat_history 
            WHERE conversation_id = ? 
            ORDER BY timestamp
        ''', (conversation_id,))
    else:
        c.execute('''
            SELECT DISTINCT conversation_id, 
                MIN(timestamp) as created_at,
                (SELECT message 
                    FROM chat_history h2 
                    WHERE h2.conversation_id = h1.conversation_id 
                    AND h2.sender = 'Bạn' 
                    LIMIT 1) as title
            FROM chat_history h1
            GROUP BY conversation_id
            ORDER BY created_at DESC
        ''')
    
    results = c.fetchall()
    conn.close()
    return results

def load_conversation_messages(conversation_id):
    """Load tất cả tin nhắn của một conversation"""
    conn = sqlite3.connect('app/database/chat_history.db')
    c = conn.cursor()
    c.execute('''
        SELECT timestamp, sender, message 
        FROM chat_history 
        WHERE conversation_id = ? 
        ORDER BY timestamp
    ''', (conversation_id,))
    messages = c.fetchall()
    conn.close()
    
    return [
        {
            'timestamp': msg[0],
            'sender': msg[1],
            'message': msg[2]
        }
        for msg in messages
    ]

def delete_conversation(conversation_id):
    """Xóa một cuộc trò chuyện và tất cả tin nhắn của nó"""
    try:
        conn = sqlite3.connect('app/database/chat_history.db')
        c = conn.cursor()
        c.execute('DELETE FROM chat_history WHERE conversation_id = ?', (conversation_id,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Error deleting conversation: {e}")
        return False