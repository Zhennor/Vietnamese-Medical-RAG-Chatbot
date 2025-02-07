from app.generate.gemini.reset_api_key import APIKeyManager
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from typing import List
from sentence_transformers import SentenceTransformer, util
from langchain.prompts import ChatPromptTemplate

class QueryGenerator:
    def __init__(self, key_manager: APIKeyManager, model: str, model_embedding_query: SentenceTransformer):
        self.key_manager = key_manager
        self.model = model
        self.model_embedding_query = model_embedding_query

    def build_query_prompt(self, original_query: str):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", 
                "Bạn là một chuyên gia nghiên cứu về y tế. Nhiệm vụ của bạn là tạo ra 4 câu truy vấn tìm kiếm có ngữ nghĩa gần giống nhất với một truy vấn gốc. "
                "Câu truy vấn tạo sinh phải đảm bảo không thay đổi ngữ nghĩa so với câu truy vấn gốc và đạt tỷ lệ giống ngữ nghĩa ít nhất 85%. "
                "Khi tạo câu truy vấn mới, bạn có thể thay đổi vị trí của các thành phần trong câu gốc hoặc giữ nguyên các phần quan trọng như chủ ngữ, vị ngữ, động từ và tính từ. Bạn chỉ cần thêm các thành phần phụ vào câu để làm phong phú thêm nội dung, sao cho câu truy vấn mới không thay đổi ý nghĩa so với câu gốc."
                "Ví dụ: "
                "- 'Triệu chứng ban đầu của bệnh tiểu đường là gì?' có thể đổi thành:"
                "   + 'Bệnh tiểu đường có những triệu chứng ban đầu như thế nào?'"
                "   + 'Những triệu chứng nào cho thấy bạn có thể bị tiểu đường?'"
                "   + 'Làm sao để nhận biết các triệu chứng ban đầu của bệnh tiểu đường?'"
                "- 'Các phương pháp điều trị cao huyết áp hiệu quả?' có thể đổi thành:"
                "   + 'Những cách điều trị cao huyết áp nào hiệu quả nhất?'"
                "   + 'Có phương pháp nào hiệu quả trong điều trị cao huyết áp không?'"
                "   + 'Điều trị cao huyết áp hiệu quả bao gồm những gì?'"
                "- 'Nguyên nhân gây ra bệnh tim mạch là gì?' có thể đổi thành:"
                "   + 'Bệnh tim mạch do những nguyên nhân nào gây ra?'"
                "   + 'Các yếu tố dẫn đến bệnh tim mạch là gì?'"
                "   + 'Tại sao bạn lại mắc bệnh tim mạch?'"
                "- 'Vaccine COVID-19 hoạt động như thế nào?' có thể đổi thành:"
                "   + 'Cơ chế hoạt động của vaccine COVID-19 là gì?'"
                "   + 'Vaccine COVID-19 bảo vệ bạn bằng cách nào?'"
                "   + 'Làm sao vaccine COVID-19 giúc phòng ngừa bệnh?'"
                ),
                ("human", f"Vui lòng tạo ra 4 câu truy vấn tìm kiếm liên quan nhất đến: {original_query}. Chỉ trả về 4 câu truy vấn, không giải thích gì thêm.")
            ]
        )
        return prompt

    def generate_query(self, original_query: str) -> List[str]:
        prompt = self.build_query_prompt(original_query)
        model_gemini = ChatGoogleGenerativeAI(
            google_api_key=self.key_manager.get_next_key(),
            model=self.model,  
            max_tokens=1000,
            temperature=0, 
        )
        query_generator_chain = prompt | model_gemini | StrOutputParser()
        result = query_generator_chain.invoke({"original_query": original_query})
        generated_queries = result.strip().split('\n')
        cleaned_queries = [re.sub(r'^\d+\.\s*', '', query).strip() for query in generated_queries]
        
        valid_queries = []
        original_embedding = self.model_embedding_query.encode(original_query, convert_to_tensor=True)
        
        for query in cleaned_queries:
            query_embedding = self.model_embedding_query.encode(query, convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(original_embedding, query_embedding).item()
            if similarity >= 0.5:
                valid_queries.append(query)
        
        valid_queries.append(original_query)
        return valid_queries
