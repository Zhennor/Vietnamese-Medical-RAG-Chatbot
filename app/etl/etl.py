import requests
from bs4 import BeautifulSoup
from typing import List
from googlesearch import search

class LinkDataExtractor:
    def __init__(self, query: str, num_results: int = 10, lang: str = 'vi'):
        self.query = query
        self.num_results = num_results
        self.lang = lang
        self.links = []
        self.documents = []

    def get_links(self) -> List[str]:
        try:
            self.links = list(search(self.query, num_results=self.num_results, lang=self.lang))
        except Exception as e:
            print(f"Lỗi khi tìm kiếm: {e}")
            self.links = []
        return self.links

    def extract_documents(self) -> List[str]:
        headers = {'User-Agent': 'Mozilla/5.0'}
        self.documents = []

        for link in self.links:
            try:
                response = requests.get(link, headers=headers, timeout=5)
                soup = BeautifulSoup(response.content, 'html.parser')
                text = ' '.join([p.get_text().strip() for p in soup.find_all('p')])
                self.documents.append(text if text else "Nội dung không tìm thấy")
            except Exception as e:
                print(f"Lỗi khi lấy nội dung từ {link}: {e}")
                self.documents.append("Nội dung không tìm thấy")
                
        return self.documents

    def run(self) -> None:
        self.get_links()
        self.extract_documents()

    def get_results(self) -> List[dict]:
        return [{"link": link, "document": doc} for link, doc in zip(self.links, self.documents)]
