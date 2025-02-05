import json
import torch
from datasets import Dataset
from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformerTrainingArguments
from sentence_transformers import SentenceTransformer, losses, InputExample
from sentence_transformers import SentenceTransformerTrainer


def load_dataset(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    examples = []
    for sample in data:
        question = sample["question"]
        true_context = sample["true_context"]
        negatives = sample["negatives"]
        
        pos_example = {
            "texts": [question, true_context],  
            "label": 1.0  
        }
        examples.append(pos_example)
        
        for negative in negatives:
            neg_example = {
                "texts": [question, negative],  
                "label": 0.0  
            }
            examples.append(neg_example)
            
    return Dataset.from_list(examples)

train_dataset = load_dataset("/kaggle/input/medical-data/medical_train.json")
test_dataset = load_dataset("/kaggle/input/medical-data/medical_test.json")

MODEL_NAME = "intfloat/e5-large"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = SentenceTransformer(MODEL_NAME)

train_loss = losses.MultipleNegativesRankingLoss(model)

def tokenize_fn(examples):
    inputs = tokenizer(
        examples["texts"], 
        padding="max_length",
        truncation=True,
        max_length=512,
        return_tensors="pt"
    )
    return inputs
    
train_dataset = train_dataset.map(tokenize_fn, batched=True)
test_dataset = test_dataset.map(tokenize_fn, batched=True)

training_args = SentenceTransformerTrainingArguments(
    report_to="wandb",
    run_name="e5-medical",
    output_dir="./results",
    evaluation_strategy="epoch",  
    save_strategy="epoch",
    per_device_train_batch_size=16, 
    per_device_eval_batch_size=8,
    gradient_accumulation_steps=2,  
    learning_rate=5e-5,
    weight_decay=1e-4,
    num_train_epochs=3,
    warmup_steps=500,
    logging_dir="./logs",
    logging_steps=10,
    fp16=True,  
    save_total_limit=2
)

trainer = SentenceTransformerTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    loss=train_loss
)

trainer.train()
trainer.save_model("./e5_large_finetuned")
