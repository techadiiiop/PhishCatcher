import os
from PIL import Image, ImageDraw, ImageFont
import random

# Create directories if they don't exist
phish_dir = "../datasets/phishing_screenshots/"
legit_dir = "../datasets/legitimate_screenshots/"

os.makedirs(phish_dir, exist_ok=True)
os.makedirs(legit_dir, exist_ok=True)

def create_legitimate_image(filename):
    """Create a clean, normal login page screenshot (white background, simple form)"""
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple login box (light gray rectangle)
    draw.rectangle([200, 150, 600, 450], fill='#f0f0f0', outline='#cccccc')
    
    # Draw "Login" title
    try:
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_label = ImageFont.truetype("arial.ttf", 16)
    except:
        font_title = ImageFont.load_default()
        font_label = ImageFont.load_default()
    
    draw.text((350, 180), "Login", fill='black', font=font_title)
    draw.text((250, 230), "Username:", fill='black', font=font_label)
    draw.text((250, 280), "Password:", fill='black', font=font_label)
    
    # Draw input fields (white rectangles)
    draw.rectangle([350, 225, 550, 250], fill='white', outline='gray')
    draw.rectangle([350, 275, 550, 300], fill='white', outline='gray')
    
    # Draw login button
    draw.rectangle([350, 340, 450, 380], fill='#4CAF50', outline='green')
    draw.text((370, 352), "Sign In", fill='white', font=font_label)
    
    img.save(filename)
    print(f"Created legitimate: {filename}")

def create_phishing_image(filename):
    """Create a suspicious login page with red warnings, urgency text, etc."""
    img = Image.new('RGB', (800, 600), color='#fff0f0')  # light red background
    draw = ImageDraw.Draw(img)
    
    # Red warning banner
    draw.rectangle([0, 0, 800, 60], fill='#ff4444')
    try:
        font_warning = ImageFont.truetype("arial.ttf", 18)
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_label = ImageFont.truetype("arial.ttf", 16)
    except:
        font_warning = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_label = ImageFont.load_default()
    
    draw.text((150, 20), "⚠️ SECURITY ALERT: Verify Your Account Immediately ⚠️", fill='white', font=font_warning)
    
    # Suspicious login box
    draw.rectangle([200, 150, 600, 450], fill='#ffe0e0', outline='#ff8888')
    draw.text((300, 180), "Verify Account", fill='darkred', font=font_title)
    
    draw.text((250, 230), "Email Address:", fill='black', font=font_label)
    draw.text((250, 280), "Password:", fill='black', font=font_label)
    
    draw.rectangle([350, 225, 550, 250], fill='white', outline='gray')
    draw.rectangle([350, 275, 550, 300], fill='white', outline='gray')
    
    draw.rectangle([350, 340, 450, 380], fill='#ff4444', outline='darkred')
    draw.text((370, 352), "Verify Now", fill='white', font=font_label)
    
    # Small text at bottom
    draw.text((250, 420), "Your account will be suspended if you don't verify within 24 hours.", fill='red', font=font_label)
    draw.text((250, 450), "Click here to update your billing information.", fill='blue', font=font_label)
    
    img.save(filename)
    print(f"Created phishing: {filename}")

# Generate 100 legitimate images
for i in range(100):
    filename = os.path.join(legit_dir, f"legit_{i:03d}.png")
    create_legitimate_image(filename)

# Generate 100 phishing images
for i in range(100):
    filename = os.path.join(phish_dir, f"phish_{i:03d}.png")
    create_phishing_image(filename)

print("✅ Dataset generation complete! 200 images total (100 legit, 100 phish).")