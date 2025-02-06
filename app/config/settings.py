import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL=os.getenv("QDRANT_URL")
QDRANT_API_KEY=os.getenv("QDRANT_API_KEY")
COLLECTION_NAME=os.getenv("COLLECTION_NAME")
MODEL_EMBEDDING=os.getenv("MODEL_EMBEDDING")
COHERE_API_KEY=os.getenv("COHERE_API_KEY")
RERANK_MODEL= os.getenv("RERANK_MODEL")