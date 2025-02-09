import cohere
from typing import List, Dict, Union
from dotenv import load_dotenv
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
from app.generate.gemini.reset_api_key import APIKeyManager

load_dotenv()
COHERE_API_KEY = os.getenv('COHERE_API_KEY')
RERANK_MODEL = os.getenv('RERANK_MODEL')

class Cohere:
    def __init__(self, api_key_manager: APIKeyManager, cohere_model: str, model_embedding: str):
        api_key = api_key_manager.get_next_key()
        self.client = cohere.Client(api_key)
        self.cohere_model = cohere_model
        self.embedding_model = SentenceTransformer(model_embedding)

    def rerank_documents(self, query: str, documents: List[Dict[str, str]]) -> List[Dict[str, str]]:
        valid_documents = [doc for doc in documents if 'content' in doc and doc['content'].strip()]

        if not valid_documents:
            print("No valid documents to rerank.")
            return []

        return self._rerank(query, valid_documents)

    def rerank_documents_with_links(self, query: str, documents: List[Dict[str, str]]) -> str:
        valid_documents_with_links = [
            {'content': doc['document'], 'link': doc['link']}
            for doc in documents
            if 'document' in doc and 'link' in doc and doc['document'].strip()
        ]

        if not valid_documents_with_links:
            print("No valid documents with links to rerank.")
            return ""

        reranked_docs = self._rerank(query, valid_documents_with_links, rerank_links=True)
        links = [doc['link'] for doc in reranked_docs]
        processed_links = "\n".join([f"{i+1}. {link}" for i, link in enumerate(links)])

        return processed_links

    def _rerank(self, query: str, documents: List[Dict[str, str]], rerank_links: bool = False) -> List[Dict[str, str]]:
        doc_contents = [doc['content'] for doc in documents]
        doc_links = [doc.get('link', '') for doc in documents]
        doc_ids = [doc.get('id', str(index)) for index, doc in enumerate(documents)]

        try:
            response = self.client.rerank(
                model=self.cohere_model,
                query=query,
                documents=doc_contents,
                top_n=5
            )

            reranked_documents = [
                {
                    'id': doc_ids[res.index],
                    'content': doc_contents[res.index],
                    'score': res.relevance_score,
                    'link': doc_links[res.index]
                }
                for res in response.results
            ]

            tfidf_vectorizer = TfidfVectorizer()
            tfidf_matrix = tfidf_vectorizer.fit_transform(doc_contents)
            query_tfidf = tfidf_vectorizer.transform([query])
            scores_tfidf = cosine_similarity(query_tfidf, tfidf_matrix).flatten()

            query_embedding = self.embedding_model.encode(query, convert_to_tensor=True)
            doc_embeddings = self.embedding_model.encode(doc_contents, convert_to_tensor=True)
            scores_cosine = util.pytorch_cos_sim(query_embedding, doc_embeddings).squeeze(0).cpu().numpy()

            combined_scores = 0.8 * scores_cosine + 0.2 * scores_tfidf

            if not rerank_links and all(score < 0.4 for score in combined_scores):
                return 1

            for idx, doc in enumerate(reranked_documents):
                doc['combined_score'] = combined_scores[idx]

            reranked_documents.sort(key=lambda x: x['combined_score'], reverse=True)

        except Exception as e:
            print(f"Error during reranking: {e}")
            return []

        return reranked_documents[:5]
