import re
import json
from datasets import load_dataset

ds = load_dataset("itdainb/VIETNAMESE_RAG")

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

cleaned_data = []
for item in ds['test']:
    if item['domain'] == "MEDICAL":
        cleaned_item = {key: clean_text(value) if isinstance(value, str) else value for key, value in item.items()}
        cleaned_item.pop("domain", None)
        cleaned_data.append(cleaned_item)

output_file = "../data/medical_test.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

print(f"Dữ liệu đã được lưu vào {output_file} (Tổng: {len(cleaned_data)} mẫu)")
