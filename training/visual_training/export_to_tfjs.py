import torch
import torch.nn as nn
from torchvision import models
import numpy as np

# Load your trained model
model = models.resnet18(pretrained=False)
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 2)
model.load_state_dict(torch.load('best_resnet18_phishing.pth', map_location='cpu'))
model.eval()

# Create dummy input for tracing
dummy_input = torch.randn(1, 3, 224, 224)

# Trace the model
traced_model = torch.jit.trace(model, dummy_input)

# Save as TorchScript
traced_model.save('resnet18_phishing_scripted.pt')

print("✅ Model exported to TorchScript (will be converted to TF.js later)")

# Optional: Also export via ONNX for completeness
import onnx
torch.onnx.export(model, dummy_input, "resnet18_phishing.onnx", 
                  input_names=['input'], output_names=['output'],
                  dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}})
print("✅ ONNX model saved")