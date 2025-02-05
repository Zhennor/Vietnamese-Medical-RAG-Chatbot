import json
import os
from typing import List
from tqdm import tqdm
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
fromt vector_db import MedicalVectorStore


if __name__ == "__main__":
    load_dotenv()
    vector_store = MedicalVectorStore(batch_size=100)
    vector_store.run("/kaggle/input/corpus/corpus_chunked.json")