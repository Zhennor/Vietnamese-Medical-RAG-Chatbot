import json
from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_medical_corpus(input_file: str, output_file: str, chunk_size: int = 400, chunk_overlap: int = 50):
    with open(input_file, 'r', encoding='utf-8') as f:
        corpus = json.load(f)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    chunks_data = []
    stt = 0
    for idx, entry in enumerate(corpus):
        chunks = text_splitter.split_text(entry['text'])
        for chunk_idx, chunk in enumerate(chunks):
            chunk_data = {
                "chunk_id": f"{idx}_{chunk_idx}",
                "text": chunk,
                "stt": stt
            }
            chunks_data.append(chunk_data)
            stt += 1

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunks_data, f, ensure_ascii=False, indent=4)

    print(f"✅ Đã lưu dữ liệu chunked vào file '{output_file}'")

split_medical_corpus('../data/medical_corpus.json', 'corpus_chunked.json')
