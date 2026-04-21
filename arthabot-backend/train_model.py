"""
train_model.py
==============
Trains a multilingual BERT transformer for Hindi ambiguity detection.
Model: bert-base-multilingual-cased (supports Hindi Devanagari + Hinglish)
Task: Multi-label classification — predicts which ambiguity types are present.

Labels (8 classes):
  0: LEXICAL AMBIGUITY
  1: SYNTACTIC AMBIGUITY
  2: SEMANTIC AMBIGUITY
  3: PRAGMATIC AMBIGUITY
  4: REFERENTIAL AMBIGUITY
  5: SCOPE AMBIGUITY
  6: PHONOLOGICAL AMBIGUITY
  7: MORPHOLOGICAL AMBIGUITY

Run: python train_model.py
Output: saves model to ./saved_model/
"""

import json
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    get_linear_schedule_with_warmup
)
from torch.optim import AdamW
import os

# ── Config ──────────────────────────────────────────────────────────────────
MODEL_NAME   = "bert-base-multilingual-cased"
DATA_PATH    = "data/training_data.json"
SAVE_PATH    = "saved_model"
MAX_LEN      = 128
BATCH_SIZE   = 4
EPOCHS       = 15          # More epochs since dataset is small
LR           = 2e-5
NUM_LABELS   = 8

LABEL_NAMES = [
    "LEXICAL AMBIGUITY",
    "SYNTACTIC AMBIGUITY",
    "SEMANTIC AMBIGUITY",
    "PRAGMATIC AMBIGUITY",
    "REFERENTIAL AMBIGUITY",
    "SCOPE AMBIGUITY",
    "PHONOLOGICAL AMBIGUITY",
    "MORPHOLOGICAL AMBIGUITY",
]

# ── Dataset ──────────────────────────────────────────────────────────────────
class AmbiguityDataset(Dataset):
    def __init__(self, data, tokenizer, max_len):
        self.data      = data
        self.tokenizer = tokenizer
        self.max_len   = max_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item     = self.data[idx]
        sentence = item["sentence"]
        labels   = torch.tensor(item["labels"], dtype=torch.float)

        encoding = self.tokenizer(
            sentence,
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        return {
            "input_ids":      encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "labels":         labels
        }


# ── Training ─────────────────────────────────────────────────────────────────
def train():
    print("=" * 60)
    print("  ArthaBot — Transformer Training")
    print("  Model : bert-base-multilingual-cased")
    print("  Task  : Hindi/Hinglish Ambiguity Detection")
    print("=" * 60)

    # Load data
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
    print(f"\n✓ Loaded {len(raw)} training examples")

    # Tokenizer
    print(f"✓ Loading tokenizer: {MODEL_NAME}")
    tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)

    # Dataset + DataLoader
    dataset    = AmbiguityDataset(raw, tokenizer, MAX_LEN)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    # Model
    print(f"✓ Loading model: {MODEL_NAME}")
    model = BertForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=NUM_LABELS,
        problem_type="multi_label_classification"
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"✓ Device: {device}")
    model.to(device)

    # Optimizer + scheduler
    optimizer = AdamW(model.parameters(), lr=LR, weight_decay=0.01)
    total_steps = len(dataloader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=total_steps // 10,
        num_training_steps=total_steps
    )

    # Loss: BCEWithLogitsLoss for multi-label
    loss_fn = torch.nn.BCEWithLogitsLoss()

    print(f"\n── Training for {EPOCHS} epochs ──\n")

    model.train()
    for epoch in range(EPOCHS):
        total_loss = 0
        for batch in dataloader:
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels         = batch["labels"].to(device)

            optimizer.zero_grad()
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            loss    = loss_fn(outputs.logits, labels)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(dataloader)
        print(f"  Epoch {epoch+1:2d}/{EPOCHS}  |  Loss: {avg_loss:.4f}")

    # Save model + tokenizer
    os.makedirs(SAVE_PATH, exist_ok=True)
    model.save_pretrained(SAVE_PATH)
    tokenizer.save_pretrained(SAVE_PATH)

    # Save label names alongside model
    with open(os.path.join(SAVE_PATH, "label_names.json"), "w") as f:
        json.dump(LABEL_NAMES, f)

    print(f"\n✓ Model saved to ./{SAVE_PATH}/")
    print("✓ Training complete!\n")
    print("Next step: python server.py")


if __name__ == "__main__":
    train()
