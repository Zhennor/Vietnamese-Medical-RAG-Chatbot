import cohere
from typing import List, Tuple, Dict
from dotenv import load_dotenv
import os

load_dotenv()
COHERE_API_KEY = os.getenv('COHERE_API_KEY')
RERANK_MODEL = os.getenv('RERANK_MODEL')


class Cohere:
    def __init__(self, api_key: str, cohere_model: str):
        self.client = cohere.Client(api_key)
        self.cohere_model = cohere_model

    def rerank_documents(self, query: str, documents: List[str]) -> List[Tuple[str, float]]:
        try:
            response = self.client.rerank(
                model=self.cohere_model,
                query=query,
                documents=documents,
                top_n=5
            )
            
            reranked_documents = [
                (documents[res.index], res.relevance_score) for res in response.results
            ]
            
        except Exception as e:
            print(f"Error during reranking: {e}")
            reranked_documents = []

        return reranked_documents

    def rerank_links_with_documents(self, query: str, documents: List[Dict[str, str]]) -> List[Dict[str, str]]:
        doc_contents = [doc['content'] for doc in documents]
        doc_links = [doc['link'] for doc in documents]

        try:
            response = self.client.rerank(
                model=self.cohere_model,
                query=query,
                documents=doc_contents,
                top_n=5
            )
            
            reranked_results = [
                {
                    'link': doc_links[res.index],
                    'content': doc_contents[res.index],
                    'score': res.relevance_score
                }
                for res in response.results
            ]
        except Exception as e:
            print(f"Error during reranking: {e}")
            reranked_results = []

        return reranked_results
