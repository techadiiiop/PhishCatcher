import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models, transforms
from torch.utils.data import DataLoader, Dataset
from PIL import Image
from sklearn.model_selection import train_test_split

# -------------------------------
# Step 1: Load images from folders
# -------------------------------

class PhishingImageDataset(Dataset):
    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img = Image.open(self.image_paths[idx]).convert('RGB')
        label = self.labels[idx]
        if self.transform:
            img = self.transform(img)
        return img, label

def load_data(phish_dir, legit_dir):
    phish_paths = [os.path.join(phish_dir, f) for f in os.listdir(phish_dir) if f.endswith('.png')]
    legit_paths = [os.path.join(legit_dir, f) for f in os.listdir(legit_dir) if f.endswith('.png')]
    
    all_paths = phish_paths + legit_paths
    all_labels = [1] * len(phish_paths) + [0] * len(legit_paths)  # 1 = phishing, 0 = legit
    
    # Split into train (80%) and validation (20%)
    X_train, X_val, y_train, y_val = train_test_split(
        all_paths, all_labels, test_size=0.2, random_state=42, stratify=all_labels
    )
    
    print(f"Training samples: {len(X_train)} (phishing: {sum(y_train)}, legit: {len(y_train)-sum(y_train)})")
    print(f"Validation samples: {len(X_val)}")
    
    return X_train, y_train, X_val, y_val

# -------------------------------
# Step 2: Define transforms and dataloaders
# -------------------------------

data_transforms = {
    'train': transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'val': transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
}

# -------------------------------
# Step 3: Setup device and model
# -------------------------------

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Load pre-trained ResNet-18
model = models.resnet18(weights='IMAGENET1K_V1')
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 2)  # 2 classes: legit (0), phishing (1)
model = model.to(device)

# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)

# -------------------------------
# Step 4: Training function
# -------------------------------

def train_model(model, train_loader, val_loader, epochs=15):
    best_acc = 0.0
    for epoch in range(epochs):
        print(f'Epoch {epoch+1}/{epochs}')
        print('-' * 20)
        
        # Training phase
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        
        train_acc = 100 * correct / total
        train_loss = running_loss / len(train_loader)
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                _, predicted = torch.max(outputs, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        val_acc = 100 * val_correct / val_total
        val_loss = val_loss / len(val_loader)
        
        print(f'Train Loss: {train_loss:.4f} Acc: {train_acc:.2f}%')
        print(f'Val Loss: {val_loss:.4f} Acc: {val_acc:.2f}%')
        
        # Save best model
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), 'best_resnet18_phishing.pth')
            print(f'  -> Saved best model with val acc {val_acc:.2f}%')
        
        scheduler.step()
    
    print(f'Training complete. Best val accuracy: {best_acc:.2f}%')
    return model

# -------------------------------
# Step 5: Run training
# -------------------------------

if __name__ == "__main__":
    # Paths to your dataset folders
    phish_dir = "../datasets/phishing_screenshots/"
    legit_dir = "../datasets/legitimate_screenshots/"
    
    # Load data
    X_train, y_train, X_val, y_val = load_data(phish_dir, legit_dir)
    
    # Create datasets
    train_dataset = PhishingImageDataset(X_train, y_train, transform=data_transforms['train'])
    val_dataset = PhishingImageDataset(X_val, y_val, transform=data_transforms['val'])
    
    # Create dataloaders
    batch_size = 16
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Train
    model = train_model(model, train_loader, val_loader, epochs=15)
    
    print("✅ Model training finished. Model saved as 'best_resnet18_phishing.pth'")