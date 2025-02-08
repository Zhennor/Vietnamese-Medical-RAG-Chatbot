import uuid
from typing import List
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from urllib.parse import urlparse

class LinkDataExtractor:
    def __init__(self, query: str, num_results: int = 10, lang: str = 'vi'):
        self.query = query
        self.num_results = num_results
        self.lang = lang
        self.links = []
        self.documents = []

    def is_valid_url(self, url):
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https')

    def get_links(self) -> List[str]:
        try:
            links = list(search(self.query, num_results=self.num_results, lang=self.lang))
            self.links = [link for link in links if self.is_valid_url(link)]
        except Exception as e:
            print(f"Lỗi khi tìm kiếm: {e}")
            self.links = []
        return self.links

    def extract_documents(self) -> List[str]:
        headers = {'User-Agent': 'Mozilla/5.0'}
        self.documents = []
        
        for link in self.links:
            try:
                response = requests.get(link, headers=headers, timeout=15)
                soup = BeautifulSoup(response.content, 'html.parser')
                text = ' '.join([p.get_text().strip() for p in soup.find_all('p')])
                self.documents.append(text if text else "Nội dung không tìm thấy")
            except Exception as e:
                print(f"Lỗi khi lấy nội dung từ {link}: {e}")
                self.documents.append("Nội dung không tìm thấy")
                
        return self.documents

    def run(self,qdrant_db) -> None:
        self.get_links()
        self.extract_documents()
        self.add_to_qdrant(qdrant_db)

    def get_results(self) -> List[dict]:
        return [{"link": link, "document": doc} for link, doc in zip(self.links, self.documents)]

    def add_to_qdrant(self, qdrant_db, batch_size=50) -> int:
        if not self.documents:
            self.run()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
        documents = []
        
        for idx, (link, doc) in enumerate(zip(self.links, self.documents)):
            if doc != "Nội dung không tìm thấy":
                chunks = text_splitter.split_text(doc)
                for chunk_idx, chunk in enumerate(chunks):
                    unique_id = str(uuid.uuid4())
                    documents.append(
                        Document(
                            page_content=chunk,
                            metadata={
                                'chunk_id': f"web_{idx}_{chunk_idx}_{unique_id}",
                                'cid': f"web_{self.query}_{idx}",
                                'source_url': link,
                                'query': self.query
                            }
                        )
                    )
        
        try:
            total_added = 0
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                qdrant_db.vector_store.add_documents(batch)
                total_added += len(batch)
                print(f"Đã thêm {total_added}/{len(documents)} documents")

            print(f"Đã thêm tổng cộng {total_added} documents vào collection '{qdrant_db.collection_name}'")
            return total_added
                
        except Exception as e:
            print(f"Lỗi khi thêm vào Qdrant: {e}")
            return 0

