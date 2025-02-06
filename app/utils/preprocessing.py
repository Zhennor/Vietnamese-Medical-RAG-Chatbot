import json
import re

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  
    text = re.sub(r"\s+", " ", text).strip()  
    return text

with open("../data/corpus_chunked.json", "r", encoding="utf-8") as f:
    corpus = json.load(f)

for item in corpus:
    item["text"] = clean_text(item["text"])

with open("../data/corpus_chunked.json", "w", encoding="utf-8") as f:
    json.dump(corpus, f, ensure_ascii=False, indent=4)

print("Saved to ../data/corpus_chunked.json.json")
