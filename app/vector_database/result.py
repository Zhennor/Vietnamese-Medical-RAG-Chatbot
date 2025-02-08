import os
from dotenv import load_dotenv
from app.generate.gemini.reset_api_key import APIKeyManager
from app.generate.gemini.gemini import Gemini
from sentence_transformers import SentenceTransformer
from app.vector_database.vector_db import QdrantDB
from app.rerank.cohere_rerank import Cohere
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

MODEL_GENERATOR = os.getenv("GEMINI_MODEL")
GEMINI_API_LIST = os.getenv('GEMINI_API_LIST').split(',')
MODEL_RERANKER = os.getenv("MODEL_RERANKER")
COHERE_API_KEY = os.getenv("COHERE_API_KEY").split(',')
MODEL_EMBEDDING = os.getenv("MODEL_EMBEDDING")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

KEY_MANAGER_GEMINI = APIKeyManager(GEMINI_API_LIST)
KEY_MANAGER_COHERE = APIKeyManager(COHERE_API_KEY)
URL_QDRANT = os.getenv("QDRANT_URL")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

model_embedding_query = SentenceTransformer(MODEL_EMBEDDING)
embedding_search = HuggingFaceEmbeddings(model_name=MODEL_EMBEDDING)
model_reranker = Cohere(KEY_MANAGER_COHERE, MODEL_RERANKER, MODEL_EMBEDDING)
model_gemini = Gemini(KEY_MANAGER_GEMINI, MODEL_GENERATOR, model_embedding_query, model_reranker)

def result_query(original_query):
    vector_db = QdrantDB(URL_QDRANT, QDRANT_API_KEY, COLLECTION_NAME, MODEL_EMBEDDING)
    
    check_query_user = model_gemini.check_query(original_query)
    print(type(check_query_user))
    
    if check_query_user == '0':
        generated_queries = model_gemini.generate_query(original_query)
        print(generated_queries)

        all_docs = []
        for query in generated_queries:
            docs = vector_db.search_documents(query)
            all_docs.extend(docs)

        unique_docs = {doc['id']: doc for doc in all_docs}.values()
        result_rerank = model_reranker.rerank_documents(original_query, list(unique_docs))
        if result_rerank == 1:
            response = model_gemini.generate_response_link(original_query, vector_db)
            return f"{response}"
        else:
            response = model_gemini.generate_response(original_query, result_rerank)
            return response
    
    elif check_query_user == '1':
        return model_gemini.generate_usually(original_query)
    elif check_query_user == '2':
        return model_gemini.generate_introduction(original_query)
    elif check_query_user == '3':
        return 'Xin lỗi bạn, tôi không được huấn luyện để trả lời câu hỏi này. Tôi chỉ hỗ trợ các câu hỏi liên quan đến y tế và sức khỏe.'

