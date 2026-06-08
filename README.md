# 🛡️ PhishCatcher – AI‑Powered Phishing Detection Chrome Extension

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Chrome Web Store](https://img.shields.io/badge/Chrome-Extension-blue)](https://chrome.google.com/webstore)

**PhishCatcher** is a real‑time browser extension that uses a **BiGRU deep learning model** to detect phishing URLs instantly. It combines URL analysis with optional visual inspection (ResNet) and includes a decoy‑based threat intelligence module.

![Demo Screenshot](demo-screenshot.png) <!-- Add a screenshot later -->

## ✨ Features

- 🔍 **Real‑time URL classification** – checks every page you visit
- 🧠 **BiGRU character‑level model** – lightweight, <0.1s inference
- 🔄 **Continuous data pipeline** – ingests fresh phishing feeds (PhishTank, OpenPhish)
- ⚠️ **Warning overlay** – immediate visual alert on suspicious pages
- 🎭 **Decoy server** – logs attacker credentials when confidence ≥70%
- 📊 **Extension popup** – shows scan statistics and manual scan button

## 🛠️ Tech Stack

| Component        | Technology                               |
|------------------|------------------------------------------|
| **Model**        | BiGRU (TensorFlow / Keras)               |
| **Backend**      | Flask + Flask‑CORS                       |
| **Extension**    | Chrome Manifest V3 (JS)                  |
| **Data sources** | PhishTank, OpenPhish, LegitPhish (fallback) |
| **Deployment**   | Local / Any cloud (Render, Hugging Face) |

## 📁 Project Structure
PhishCatcher/
├── backend/ # Flask API + BiGRU wrapper
├── extension/ # Chrome extension (MV3)
├── training/ # Data cleaning + model training
├── cleaned_data/ # Balanced CSV datasets
└── README.md

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10+
- Google Chrome browser

### 1. Clone the repository

git clone https://github.com/YOUR_USERNAME/PhishCatcher.git
cd PhishCatcher

### 2. Set up Python environment
## bash
- conda create -n phishcatcher python=3.10 -y
- conda activate phishcatcher
- pip install -r backend/requirements.txt 

### 3. Download the trained model
The model file is not included in GitHub due to size. Download it from [this link] and place bigru_phishing_best.h5 and tokenizer.pkl inside backend/.

### 4. Run the backend
- cd backend
- python app.py
- Server runs at http://localhost:5000

### 5. Load the Chrome extension
- Open chrome://extensions/
- Enable Developer mode
- Click Load unpacked → select extension folder
