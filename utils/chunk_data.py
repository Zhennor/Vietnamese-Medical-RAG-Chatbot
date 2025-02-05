import json
from langchain.text_splitter import RecursiveCharacterTextSplitter

with open('../data/medical_corpus.json', 'r', encoding='utf-8') as f:
    corpus = json.load(f)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)

chunks_data = []
stt=0
for idx, entry in enumerate(corpus):
    chunks = text_splitter.split_text(entry['text'])
    for chunk_idx, chunk in enumerate(chunks):
        chunk_data = {
            "chunk_id": f"{idx}_{chunk_idx}",
            "text": chunk,
            "stt": stt
        }
        chunks_data.append(chunk_data)
        stt+=1

with open('template.json', 'w', encoding='utf-8') as f:
    json.dump(chunks_data, f, ensure_ascii=False, indent=4)

print("Đã lưu dữ liệu chunked vào file 'template.json'")
