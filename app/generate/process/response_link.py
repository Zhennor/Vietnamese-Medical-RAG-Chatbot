from app.generate.gemini.reset_api_key import APIKeyManager
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from app.etl.etl import LinkDataExtractor
from app.rerank.cohere_rerank import Cohere

class LinkReranker:
    def __init__(self, key_manager: APIKeyManager, model: str, model_reranker: Cohere):
        self.key_manager = key_manager
        self.model = model
        self.model_reranker = model_reranker

    def built_response_prompt_links(self, original_query: str, links):
        processed_links = "\n".join([f"{i+1}. {link}" for i, link in enumerate(links)])
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", 
                """
                Bạn là một trợ lý AI chuyên gia về y tế và sức khỏe. 
                Nhiệm vụ của bạn là tìm các nguồn thông tin liên quan đến câu hỏi của người dùng và trình bày lại các kết quả tìm kiếm với tiêu đề và đường link rõ ràng.
                """), 
                ("human", f"""
                **Câu hỏi của người dùng**:  
                '{original_query}'  

                **Danh sách các đường link**:
                {processed_links}

                **Yêu cầu định dạng**:
                1. Hiển thị thông báo: 
                "Xin lỗi bạn, với kiến thức của tôi, câu hỏi của bạn chưa thể được giải quyết. Dưới đây là các nguồn thông tin mà tôi tìm thấy thông qua tìm kiếm Google liên quan đến câu hỏi của bạn:"
                2. Danh sách các link được trình bày với định dạng sau:
                "[Số thứ tự]. Tiêu đề bài viết: đường link"
                ví dụ: 1. Cách phòng ngừa bệnh tim mạch: https://healthcare.com.vn/phong-ngua-benh-tim-mach
                3. Không được:
                - Sắp xếp lại danh sách.
                - Thêm ký tự đặc biệt hoặc ký hiệu không cần thiết.
                4. Đảm bảo mỗi đường link nằm trên **một dòng riêng biệt**.
                """)
            ]
        )
        return prompt

    def generate_response_links(self, original_query: str, qdrant_db ) -> str:
        model_gemini = ChatGoogleGenerativeAI(
            google_api_key=self.key_manager.get_next_key(),
            model=self.model,  
            max_tokens=1000,
            temperature=0, 
        )
        
        extractor = LinkDataExtractor(query=original_query)
        extractor.run(qdrant_db)
        reranked_links = self.model_reranker.rerank_documents_with_links(original_query, extractor.get_results())
        response_chain = self.built_response_prompt_links(original_query, reranked_links) | model_gemini | StrOutputParser()
        final_response = response_chain.invoke({"original_query": original_query}).strip()
        return final_response
