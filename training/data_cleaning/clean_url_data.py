import pandas as pd
import re
import os
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split

# -------------------------------
# Configuration
# -------------------------------
DATA_DIR = "../datasets/"
OUTPUT_DIR = "../cleaned_data/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------
# Helper: validate URL
# -------------------------------
def is_valid_url(url):
    if not isinstance(url, str):
        return False
    url = url.strip()
    if len(url) < 5 or len(url) > 2000:
        return False
    if not (url.startswith('http://') or url.startswith('https://')):
        return False
    if re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', url):
        return False
    return True

# -------------------------------
# Helper: clean list of URLs (skip non-strings)
# -------------------------------
def clean_urls(urls, label_name):
    cleaned = []
    for u in urls:
        if not isinstance(u, str):
            continue
        u = u.strip()
        if is_valid_url(u):
            cleaned.append(u)
    cleaned = list(set(cleaned))
    print(f"  {label_name}: {len(cleaned)} valid unique URLs")
    return cleaned

# -------------------------------
# 1. Load PhishTank
# -------------------------------
print("Loading PhishTank...")
phish_list = []
pt_path = os.path.join(DATA_DIR, "phishtank_raw.csv")
if os.path.exists(pt_path):
    try:
        df_pt = pd.read_csv(pt_path)
        url_col = None
        for col in ['url', 'phish_url', 'url_original']:
            if col in df_pt.columns:
                url_col = col
                break
        if url_col:
            urls = df_pt[url_col].dropna().astype(str).tolist()
            phish_list.extend(urls)
            print(f"  -> Loaded {len(urls)} entries from PhishTank")
        else:
            print(f"  -> PhishTank: no recognized URL column. Columns: {df_pt.columns.tolist()}")
    except Exception as e:
        print(f"  Error loading PhishTank: {e}")
else:
    print("  PhishTank file not found, skipping")

# -------------------------------
# 2. Load OpenPhish
# -------------------------------
op_path = os.path.join(DATA_DIR, "openphish_raw.txt")
if os.path.exists(op_path):
    with open(op_path, 'r') as f:
        op_urls = [line.strip() for line in f if line.strip()]
    phish_list.extend(op_urls)
    print(f"  Loaded {len(op_urls)} entries from OpenPhish")

# -------------------------------
# 3. Load LegitPhish (or other legitimate source)
# -------------------------------
legit_list = []
phish_from_legit = []
legitphish_path = os.path.join(DATA_DIR, "legitphish.csv")
if os.path.exists(legitphish_path):
    try:
        df_lp = pd.read_csv(legitphish_path)
        print(f"  LegitPhish columns found: {df_lp.columns.tolist()}")
        # Try to detect columns
        url_col = None
        label_col = None
        for col in df_lp.columns:
            if 'url' in col.lower():
                url_col = col
            if 'label' in col.lower() or 'type' in col.lower() or 'class' in col.lower() or 'category' in col.lower():
                label_col = col
        if url_col and label_col:
            urls = df_lp[url_col].dropna().astype(str).tolist()
            labels = df_lp[label_col].dropna().astype(str).str.lower().tolist()
            # Align lengths
            min_len = min(len(urls), len(labels))
            urls = urls[:min_len]
            labels = labels[:min_len]
            for url, lbl in zip(urls, labels):
                if lbl in ['1', 'legitimate', 'safe', 'benign', 'good', 'legit']:
                    legit_list.append(url)
                elif lbl in ['0', 'phishing', 'malicious', 'bad', 'phish']:
                    phish_from_legit.append(url)
            print(f"  Loaded {len(legit_list)} legit and {len(phish_from_legit)} phish from LegitPhish")
        else:
            print("  Could not detect url/label columns; check manually.")
    except Exception as e:
        print(f"  Error loading LegitPhish: {e}")
else:
    print("  LegitPhish file not found, using fallback legitimate URLs")

# -------------------------------
# 4. Large fallback legitimate URLs (generate thousands)
# -------------------------------
if len(legit_list) < 5000:
    print("  Generating large fallback list of legitimate URLs...")
    top_domains = [
        "google.com", "facebook.com", "amazon.com", "microsoft.com", "github.com",
        "wikipedia.org", "reddit.com", "twitter.com", "linkedin.com", "apple.com",
        "netflix.com", "yahoo.com", "bing.com", "cnn.com", "bbc.com",
        "nytimes.com", "stackoverflow.com", "dropbox.com", "spotify.com", "adobe.com"
    ]
    paths = ["", "login", "signin", "account", "dashboard", "home", "profile", "settings", "auth", "verify", "user", "admin", "help", "support", "contact"]
    subdomains = ["", "www.", "mail.", "secure.", "login.", "account."]
    legit_set = set()
    for domain in top_domains:
        for path in paths:
            for sub in subdomains:
                if path:
                    legit_set.add(f"https://{sub}{domain}/{path}")
                else:
                    legit_set.add(f"https://{sub}{domain}")
    legit_list = list(legit_set)
    print(f"  Generated {len(legit_list)} legitimate URLs from patterns")

# combine all phishing
all_phish = list(set(phish_list + phish_from_legit))
all_legit = list(set(legit_list))

print(f"\nBefore cleaning: {len(all_phish)} phishing, {len(all_legit)} legitimate")

# -------------------------------
# 5. Cleaning & deduplication
# -------------------------------
clean_phish = clean_urls(all_phish, "phishing")
clean_legit = clean_urls(all_legit, "legitimate")

# -------------------------------
# 6. Balance dataset (same number of each class)
# -------------------------------
if len(clean_phish) == 0 or len(clean_legit) == 0:
    print("ERROR: One of the classes has zero valid URLs. Exiting.")
    exit(1)

min_count = min(len(clean_phish), len(clean_legit))
balanced_phish = clean_phish[:min_count]
balanced_legit = clean_legit[:min_count]

print(f"\nBalanced dataset: {len(balanced_phish)} phishing, {len(balanced_legit)} legitimate")

# -------------------------------
# 7. Create labels and combine
# -------------------------------
urls = balanced_phish + balanced_legit
labels = [1]*len(balanced_phish) + [0]*len(balanced_legit)

# Shuffle
urls, labels = shuffle(urls, labels, random_state=42)

# -------------------------------
# 8. Train/validation/test split (70/15/15)
# -------------------------------
X_train, X_temp, y_train, y_temp = train_test_split(urls, labels, test_size=0.3, random_state=42, stratify=labels)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

print(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

# -------------------------------
# 9. Save to CSV
# -------------------------------
def save_csv(filename, urls, labels):
    df = pd.DataFrame({'url': urls, 'label': labels})
    df.to_csv(os.path.join(OUTPUT_DIR, filename), index=False)
    print(f"Saved {filename}")

save_csv("train.csv", X_train, y_train)
save_csv("val.csv", X_val, y_val)
save_csv("test.csv", X_test, y_test)

print("\n✅ Data cleaning complete! Files saved in '../cleaned_data/'")