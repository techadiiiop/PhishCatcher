from fastapi import FastAPI, HTTPException
from pydantic import BaseModel          # FIX 1: pydantic not pydatac
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from peft import PeftModel
import torch
import uvicorn                         # FIX 2: uvicorn not wicorn

app = FastAPI(title="PhishCatcher NLP Service", description="URL phishing detection using DistilBERT (returns phishing probability)")

# -------------------------------
# Load model and tokenizer
# -------------------------------
base_model_name = "distilbert-base-uncased"
lora_path = "./distilbert_phishing_final"   # path to your fine-tuned model

tokenizer = AutoTokenizer.from_pretrained(lora_path)

# FIX 3 & 4: specify num_labels=2 to match the LoRA adapter
base_model = AutoModelForSequenceClassification.from_pretrained(
    base_model_name,
    num_labels=2
)

model = PeftModel.from_pretrained(base_model, lora_path)
model.eval()

# -------------------------------
# Request/Response models
# -------------------------------
class URLRequest(BaseModel):
    url: str

class PredictionResponse(BaseModel):
    url: str
    is_phishing: bool
    confidence: float   # probability of being phishing (class 1)

# -------------------------------
# Prediction endpoint
# -------------------------------
@app.post("/predict", response_model=PredictionResponse)
async def predict(request: URLRequest):
    try:
        inputs = tokenizer(request.url, return_tensors="pt", truncation=True, max_length=128)
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)
            phishing_prob = probs[0][1].item()   # probability of class 1 (phishing)
            is_phishing = phishing_prob > 0.5
        return PredictionResponse(
            url=request.url,
            is_phishing=is_phishing,
            confidence=phishing_prob
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------
# Health check endpoint
# -------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}

# -------------------------------
# Run the server
# -------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)