import pandas as pd
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
import torch
import numpy as np

# ===== Load model =====
model_path = "5CD-AI/Vietnamese-Sentiment-visobert"
tokenizer = AutoTokenizer.from_pretrained(model_path)
config = AutoConfig.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

# ===== Load CSV =====
df = pd.read_csv("comments_text.csv")

sentiments = []

# ===== Predict từng comment =====
for text in df["comments"]:
    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256).to(device)

        with torch.no_grad():
            logits = model(**inputs).logits

        scores = logits.softmax(dim=-1).cpu().numpy()[0]

        # Lấy nhãn có xác suất cao nhất
        max_idx = np.argmax(scores)
        label = config.id2label[max_idx]

        # ===== Map nhãn sang số =====
        if label == "POS":
            label_num = 2
        elif label == "NEU":
            label_num = 1
        elif label == "NEG":
            label_num = 0
            
    except Exception as e:
        label_num = -1

    sentiments.append(label_num)

# ===== Ghi kết quả =====
df["sentiment"] = sentiments
df.to_csv("comments_text_labeled.csv", index=False)

print("Xong! File output: comments_text_labeled.csv")