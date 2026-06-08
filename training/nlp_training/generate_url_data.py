import random
import csv
import os

# Create output folder if not exists
os.makedirs("url_data", exist_ok=True)

# Lists of words for constructing legitimate URLs
legit_domains = ["google.com", "facebook.com", "amazon.com", "microsoft.com", "apple.com", 
                 "github.com", "stackoverflow.com", "linkedin.com", "twitter.com", "netflix.com"]
legit_paths = ["login", "signin", "account", "auth", "verify", "secure", "dashboard", "profile", "settings", "home"]

# Lists for phishing URL components
phish_domains = ["paypal-verify.xyz", "amazon-secure.net", "facebook-login.org", "appleid-verify.tk",
                 "microsoft-update.ml", "bankofamerica-acc.ga", "netflix-account.cf", "google-sigin.xyz",
                 "instagram-verify.icu", "whatsapp-web.top"]
phish_paths = ["secure/login", "verify-now", "account/update", "signin/confirm", "auth/verify", 
               "login/verify", "security-check", "confirm-identity", "password-reset", "unlock-account"]

# Also add some misspelled or weird patterns (e.g., double domain, @ symbol, numeric IPs)
def generate_phish_url():
    # 70% from domain+path, 30% from tricky patterns
    if random.random() < 0.7:
        domain = random.choice(phish_domains)
        path = random.choice(phish_paths)
        return f"https://{domain}/{path}"
    else:
        # tricky patterns: using @, IP address, or double domain
        pattern = random.choice(["at", "ip", "double"])
        if pattern == "at":
            # e.g., https://google.com@evil.com/login
            fake = random.choice(legit_domains)
            real = random.choice(phish_domains)
            return f"https://{fake}@{real}/login"
        elif pattern == "ip":
            ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
            return f"http://{ip}/~{random.choice(phish_paths)}"
        else:  # double domain
            dd = random.choice(legit_domains).replace(".", "-")
            return f"https://{dd}.{random.choice(phish_domains)}/secure"

def generate_legit_url():
    domain = random.choice(legit_domains)
    path = random.choice(legit_paths)
    return f"https://{domain}/{path}"

# Generate datasets
urls = []
for _ in range(1000):
    urls.append({"url": generate_legit_url(), "label": 0})  # 0 = legitimate
for _ in range(1000):
    urls.append({"url": generate_phish_url(), "label": 1})  # 1 = phishing

# Shuffle the list
random.shuffle(urls)

# Split into train (80%) and test (20%)
split_idx = int(0.8 * len(urls))
train_urls = urls[:split_idx]
test_urls = urls[split_idx:]

# Save to CSV files
with open("url_data/train.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["url", "label"])
    writer.writeheader()
    writer.writerows(train_urls)

with open("url_data/test.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["url", "label"])
    writer.writeheader()
    writer.writerows(test_urls)

print(f"Generated {len(train_urls)} training URLs and {len(test_urls)} test URLs.")
print("Sample legitimate:", generate_legit_url())
print("Sample phishing:", generate_phish_url())