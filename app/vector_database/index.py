import json
from typing import List
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from config.settings import QDRANT_API_KEY, QDRANT_URL, COLLECTION_NAME, MODEL_EMBEDDING
from vector_db import QdrantDB

if __name__ == "__main__":
    qdrant_search = QdrantDB(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=COLLECTION_NAME,
        model_embedding = MODEL_EMBEDDING,
        force_recreate=False  
        )



