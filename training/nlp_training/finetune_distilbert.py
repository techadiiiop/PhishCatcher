import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, DataCollatorWithPadding
)
from datasets import Dataset
from peft import LoraConfig, get_peft_model, TaskType
import torch

# -------------------------------
# Step 1: Load CSV data
# -------------------------------
train_df = pd.read_csv("url_data/train.csv")
test_df = pd.read_csv("url_data/test.csv")

print(f"Train size: {len(train_df)}, Test size: {len(test_df)}")
print(train_df.head())

# Convert pandas to HuggingFace Dataset
train_dataset = Dataset.from_pandas(train_df)
test_dataset = Dataset.from_pandas(test_df)

# -------------------------------
# Step 2: Tokenize URLs
# -------------------------------
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)

def tokenize_function(examples):
    return tokenizer(examples["url"], truncation=True, padding="max_length", max_length=128)

# Only remove 'url' and possible index columns, keep 'label'
columns_to_remove = [col for col in ["url", "__index_level_0__"] if col in train_dataset.column_names]

train_tokenized = train_dataset.map(tokenize_function, batched=True, remove_columns=columns_to_remove)
test_tokenized = test_dataset.map(tokenize_function, batched=True, remove_columns=columns_to_remove)

# Rename 'label' to 'labels'
train_tokenized = train_tokenized.rename_column("label", "labels")
test_tokenized = test_tokenized.rename_column("label", "labels")

# Set format
train_tokenized.set_format("torch", columns=["input_ids", "attention_mask", "labels"])
test_tokenized.set_format("torch", columns=["input_ids", "attention_mask", "labels"])

# -------------------------------
# Step 3: Model with LoRA
# -------------------------------
id2label = {0: "legitimate", 1: "phishing"}
label2id = {"legitimate": 0, "phishing": 1}

base_model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=2,
    id2label=id2label,
    label2id=label2id
)

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_lin", "v_lin"],
    lora_dropout=0.1,
    bias="none",
    task_type=TaskType.SEQ_CLS
)

model = get_peft_model(base_model, lora_config)
print(f"Trainable parameters: {model.num_parameters(only_trainable=True)} / {model.num_parameters()}")

# -------------------------------
# Step 4: Training arguments
# -------------------------------
training_args = TrainingArguments(
    output_dir="./distilbert_phishing_model",
    eval_strategy="epoch",          # fixed
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    num_train_epochs=5,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=50,
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    push_to_hub=False,
)

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    acc = accuracy_score(labels, predictions)
    f1 = f1_score(labels, predictions, average="weighted")
    return {"accuracy": acc, "f1": f1}

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# -------------------------------
# Step 5: Trainer (fixed: removed tokenizer argument)
# -------------------------------
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_tokenized,
    eval_dataset=test_tokenized,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
    # tokenizer=tokenizer,  # <-- REMOVED (caused error)
)

print("Starting training...")
trainer.train()

# -------------------------------
# Step 6: Save final model
# -------------------------------
model.save_pretrained("./distilbert_phishing_final")
tokenizer.save_pretrained("./distilbert_phishing_final")

print("✅ Model fine-tuning complete. Saved to ./distilbert_phishing_final")