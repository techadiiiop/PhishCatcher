import requests
import csv
import os
from datetime import datetime

# --- Configuration ---
DATA_DIR = "."  # This will save files in the current directory
PHISHTANK_URL = "http://data.phishtank.com/data/online-valid.csv"
OPENPHISH_URL = "https://openphish.com/feed.txt"
LEGITPHISH_CSV_PATH = "legitphish.csv"  # Use the path to your downloaded file

def download_phishtank():
    print("Downloading PhishTank feed...")
    try:
        response = requests.get(PHISHTANK_URL, timeout=30)
        response.raise_for_status()
        file_path = os.path.join(DATA_DIR, "phishtank_raw.csv")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"  [OK] Downloaded to {file_path}")
        return file_path
    except Exception as e:
        print(f"  [ERROR] Failed to download PhishTank: {e}")
        return None

def download_openphish():
    print("Downloading OpenPhish feed...")
    try:
        response = requests.get(OPENPHISH_URL, timeout=30)
        response.raise_for_status()
        file_path = os.path.join(DATA_DIR, "openphish_raw.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"  [OK] Downloaded to {file_path}")
        return file_path
    except Exception as e:
        print(f"  [ERROR] Failed to download OpenPhish: {e}")
        return None

def load_legitphish():
    print("Loading LegitPhish dataset...")
    if not os.path.exists(LEGITPHISH_CSV_PATH):
        print(f"  [SKIP] LegitPhish file not found at {LEGITPHISH_CSV_PATH}")
        return None, None
    try:
        legit_urls = []
        phish_urls = []
        with open(LEGITPHISH_CSV_PATH, 'r', encoding='utf-8') as f:
            # Assuming CSV has a header and columns like 'url' and 'label'
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get('url')
                label = row.get('label')
                if url and label:
                    if label == '1' or label == 'legitimate':
                        legit_urls.append(url)
                    elif label == '0' or label == 'phishing':
                        phish_urls.append(url)
        print(f"  [OK] LegitPhish loaded: {len(legit_urls)} legit, {len(phish_urls)} phish")
        return legit_urls, phish_urls
    except Exception as e:
        print(f"  [ERROR] Failed to parse LegitPhish: {e}")
        return None, None

if __name__ == "__main__":
    print("--- Starting Data Download ---")
    download_phishtank()
    download_openphish()
    legit_phish_urls, legit_legit_urls = load_legitphish()
    print("--- Data Download Complete ---")