import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Bidirectional, GRU, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.model_selection import train_test_split

# -------------------------------
# Load cleaned data
# -------------------------------
train_df = pd.read_csv("../cleaned_data/train.csv")
val_df = pd.read_csv("../cleaned_data/val.csv")
test_df = pd.read_csv("../cleaned_data/test.csv")

X_train = train_df['url'].values
y_train = train_df['label'].values
X_val = val_df['url'].values
y_val = val_df['label'].values
X_test = test_df['url'].values
y_test = test_df['label'].values

print(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

# -------------------------------
# Tokenization
# -------------------------------
MAX_WORDS = 50000   # vocabulary size
MAX_LEN = 200       # max characters per URL

tokenizer = Tokenizer(num_words=MAX_WORDS, char_level=True, oov_token='<OOV>')
tokenizer.fit_on_texts(X_train)

# convert to sequences
X_train_seq = tokenizer.texts_to_sequences(X_train)
X_val_seq = tokenizer.texts_to_sequences(X_val)
X_test_seq = tokenizer.texts_to_sequences(X_test)

# pad sequences
X_train_pad = pad_sequences(X_train_seq, maxlen=MAX_LEN, padding='post', truncating='post')
X_val_pad = pad_sequences(X_val_seq, maxlen=MAX_LEN, padding='post', truncating='post')
X_test_pad = pad_sequences(X_test_seq, maxlen=MAX_LEN, padding='post', truncating='post')

print(f"Shape X_train: {X_train_pad.shape}")

# -------------------------------
# Build BiGRU model
# -------------------------------
model = Sequential([
    Embedding(MAX_WORDS, 64, input_length=MAX_LEN),
    Bidirectional(GRU(64, return_sequences=False)),
    Dropout(0.5),
    Dense(32, activation='relu'),
    Dropout(0.3),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()

# -------------------------------
# Training
# -------------------------------
callbacks = [
    EarlyStopping(patience=3, restore_best_weights=True),
    ModelCheckpoint('bigru_phishing_best.h5', save_best_only=True)
]

history = model.fit(
    X_train_pad, y_train,
    validation_data=(X_val_pad, y_val),
    epochs=20,
    batch_size=64,
    callbacks=callbacks
)

# -------------------------------
# Evaluation
# -------------------------------
loss, acc = model.evaluate(X_test_pad, y_test)
print(f"Test Accuracy: {acc:.4f}")

# Save tokenizer
import pickle
with open('tokenizer.pkl', 'wb') as f:
    pickle.dump(tokenizer, f)

print("✅ Model and tokenizer saved.")