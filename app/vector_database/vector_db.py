import json
from typing import List
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

class QdrantDB:
    def __init__(self, url: str, api_key: str, collection_name: str, model_embedding, force_recreate: bool = False):
        self.url = url
        self.api_key = api_key
        self.collection_name = collection_name
        self.force_recreate = force_recreate
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_embedding, 
            model_kwargs={'device': 'cuda'}
        )
        self.sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        self.client = self._initialize_qdrant()
        self.vector_store = self._setup_vector_store()

    def _initialize_qdrant(self) -> QdrantClient:
        client = QdrantClient(url=self.url, api_key=self.api_key)
        collections = client.get_collections().collections
        collection_exists = any(col.name == self.collection_name for col in collections)
        
        if collection_exists and self.force_recreate:
            client.delete_collection(collection_name=self.collection_name)
            collection_exists = False
        
        if not collection_exists:
            client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    "dense": VectorParams(size=768, distance=Distance.COSINE),
                    "sparse": VectorParams(size=8192, distance=Distance.DOT, on_disk=True)
                }
            )
        
        return client

    def _setup_vector_store(self) -> QdrantVectorStore:
        if self.force_recreate:
            documents = self.load_documents("/kaggle/input/corpus/corpus_chunked.json")
            vector_store = QdrantVectorStore.from_documents(
                documents=documents,
                embedding=self.embeddings,
                sparse_embedding=self.sparse_embeddings,
                url=self.url,
                api_key=self.api_key,
                collection_name=self.collection_name,
                retrieval_mode=RetrievalMode.HYBRID,
                vector_name="dense",
                sparse_vector_name="sparse",
                force_recreate=self.force_recreate
            )
        else:
            vector_store = QdrantVectorStore.from_existing_collection(
                embedding=self.embeddings,
                sparse_embedding=self.sparse_embeddings,
                url=self.url,
                api_key=self.api_key,
                collection_name=self.collection_name,
                retrieval_mode=RetrievalMode.HYBRID,
                vector_name="dense",
                sparse_vector_name="sparse"
            )
        return vector_store

    @staticmethod
    def load_documents(json_file: str) -> List[Document]:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        documents = [
            Document(
                page_content=item['text'],
                metadata={'chunk_id': item['chunk_id'], 'cid': item['cid']}
            ) for item in data
        ]
        return documents

    def search_documents(self, query: str, k: int = 5) -> List[Document]:
        return self.vector_store.similarity_search(query=query, k=k)