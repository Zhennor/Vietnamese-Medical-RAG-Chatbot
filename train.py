import json
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer, get_cosine_schedule_with_warmup
from sentence_transformers import losses, SentenceTransformer, InputExample
from torch.optim import AdamW


MODEL_NAME = "intfloat/e5-large"
BATCH_SIZE = 16 
EPOCHS = 5
LEARNING_RATE = 2e-5
WEIGHT_DECAY = 0.01
WARMUP_RATIO = 0.1  
GRADIENT_ACCUMULATION_STEPS = 2  
FP16 = True  

class MedicalDataset(Dataset):
    def __init__(self, file_path):
        self.data = json.load(open(file_path, "r", encoding="utf-8"))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = self.data[idx]
        question = sample["question"]
        true_context = sample["true_context"]
        negatives = sample["negatives"]
        
        return InputExample(texts=[question, true_context] + negatives)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = SentenceTransformer(MODEL_NAME)

train_dataset = MedicalDataset("/kaggle/input/medical-data/medical_train.json")
train_dataloader = DataLoader(
    train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4, pin_memory=True
)

train_loss = losses.MultipleNegativesRankingLoss(model)

optimizer = AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY, correct_bias=True)
num_training_steps = len(train_dataloader) * EPOCHS
num_warmup_steps = int(WARMUP_RATIO * num_training_steps)
scheduler = get_cosine_schedule_with_warmup(optimizer, num_warmup_steps, num_training_steps)

for epoch in range(EPOCHS):
    torch.cuda.empty_cache()  
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=1,
        warmup_steps=num_warmup_steps,
        optimizer_class=AdamW,
        optimizer_params={'lr': LEARNING_RATE, 'weight_decay': WEIGHT_DECAY, 'correct_bias': True},
        scheduler=scheduler,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        use_amp=FP16  
    )
    print(f"Epoch {epoch+1} completed.")

model.save("./e5_large_finetuned")
