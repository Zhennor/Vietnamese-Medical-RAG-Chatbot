import json
from typing import List
from langchain_core.documents import Document
from app.vector_database.vector_db import QdrantDB
from config.settings import QDRANT_API_KEY, QDRANT_URL, COLLECTION_NAME, MODEL_EMBEDDING

def search_documents_from_user(query: str, top_k: int = 5) -> List[Document]:

    qdrant_search = QdrantDB(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=COLLECTION_NAME,
        model_embedding=MODEL_EMBEDDING,
        force_recreate=False  
    )
    results = qdrant_search.search_documents(query=query, k=top_k)

    return results

def search() -> List[Document]:
    query = input("Nhập truy vấn tìm kiếm: ")
    results = search_documents_from_user(query) 
    return results
