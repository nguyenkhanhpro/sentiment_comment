from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import torch
from data_preprocessing import dataset_preprocessing

model_path = "5CD-AI/Vietnamese-Sentiment-visobert"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path, num_labels=3)

def tokenize_fn(batch):
    return tokenizer(
        batch["comments"],
        truncation=True,
        padding="max_length",
        max_length=256  
    )

dataset = dataset_preprocessing()
dataset_tokenized = dataset.map(tokenize_fn, batched=True)

# QUAN TRỌNG: Đổi tên cột 'sentiment' thành 'labels'
dataset_tokenized = dataset_tokenized.rename_column("sentiment", "labels")

dataset_tokenized = dataset_tokenized.train_test_split(test_size=0.1)

training_args = TrainingArguments(
    output_dir="./results",
    eval_strategy="epoch",
    save_strategy="epoch",
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=5,
    learning_rate=2e-5,
    load_best_model_at_end=True,
    logging_dir="./logs",
    logging_steps=50,
    dataloader_pin_memory=False,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset_tokenized["train"],
    eval_dataset=dataset_tokenized["test"],
)

trainer.train()