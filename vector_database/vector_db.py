from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from tqdm import tqdm
import os
from typing import List
import json

class MedicalVectorStore:
    def __init__(self, batch_size: int = 100):
        self.embeddings = HuggingFaceEmbeddings(model_name="hiieu/halong_embedding")
        self.url = os.getenv('QDRANT_URL')
        self.api_key = os.getenv('QDRANT_API_KEY')
        self.batch_size = batch_size
        
        self.client = QdrantClient(url=self.url, api_key=self.api_key)
        
    def create_collection(self, collection_name: str = "medical_corpus"):
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )
        
    def read_corpus(self, file_path: str) -> List[dict]:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def convert_to_documents(self, corpus: List[dict]) -> List[Document]:
        return [Document(
            page_content=item["text"],
            metadata={"chunk_id": item["chunk_id"], "cid": item["cid"]}
        ) for item in corpus]
        
    def process_documents(self, documents: List[Document], collection_name: str = "medical_corpus"):
        vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            embedding=self.embeddings,
        )
        
        for i in tqdm(range(0, len(documents), self.batch_size)):
            batch = documents[i:i + self.batch_size]
            vector_store.add_documents(documents=batch)
            
    def run(self, file_path: str, collection_name: str = "medical_corpus"):
        self.create_collection(collection_name)
        corpus = self.read_corpus(file_path)
        documents = self.convert_to_documents(corpus)
        self.process_documents(documents, collection_name)