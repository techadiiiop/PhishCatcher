from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from models.fusion.multimodal_fusion import MultimodalPhishDetector
import json
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow extension to call this backend

# Initialize detector
detector = MultimodalPhishDetector(visual_weight=0.4, nlp_weight=0.6)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory stats (for popup)
stats = {
    "total_analyses": 0,
    "total_threats": 0
}

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Expected JSON: {"url": "...", "screenshot": "base64..." (optional), "visual_score": (optional)}
    Returns analysis result.
    """
    data = request.get_json()
    url = data.get('url')
    screenshot_base64 = data.get('screenshot')   # may be None
    visual_score = data.get('visual_score')      # if extension ran visual model locally

    if not url:
        return jsonify({"error": "URL is required"}), 400

    logger.info(f"Analyzing URL: {url}")

    # Get decision from multimodal fusion
    result = detector.compute_final_decision(url, screenshot_base64, visual_score)

    # Update stats
    stats["total_analyses"] += 1
    if result["is_phishing"]:
        stats["total_threats"] += 1

    # Log to a file for later analysis
    with open("analysis_log.json", "a") as f:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "result": result
        }
        f.write(json.dumps(log_entry) + "\n")

    return jsonify(result)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Return analysis statistics for the extension popup."""
    return jsonify(stats)

@app.route('/decoy', methods=['GET'])
def decoy_page():
    """Serve the decoy HTML page."""
    redirect_url = request.args.get('redirect', 'https://www.google.com')
    return render_template('decoy.html', redirect_url=redirect_url)

@app.route('/api/decoy/report', methods=['POST'])
def decoy_report():
    """
    Log credentials entered on the decoy page.
    In a real system, you would store them securely for threat intelligence.
    For academic project, we just log to a file.
    """
    data = request.get_json()
    logger.warning(f"Decoy triggered! Captured credentials from IP: {request.remote_addr}")
    with open("decoy_captured.json", "a") as f:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "ip": request.remote_addr,
            "user_agent": request.headers.get('User-Agent'),
            "username": data.get('username'),
            "password": data.get('password'),
            "original_url": data.get('original_url')
        }
        f.write(json.dumps(entry) + "\n")
    return jsonify({"status": "logged"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)