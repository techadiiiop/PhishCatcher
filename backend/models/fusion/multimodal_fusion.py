import requests
import json
import os

class MultimodalPhishDetector:
    def __init__(self, visual_weight=0.4, nlp_weight=0.6, nlp_endpoint="http://localhost:8001/predict"):
        """
        visual_weight: weight for screenshot-based model (ResNet)
        nlp_weight: weight for URL-based model (DistilBERT)
        """
        self.visual_weight = visual_weight
        self.nlp_weight = nlp_weight
        self.nlp_endpoint = nlp_endpoint
        self.confidence_threshold = 0.70   # decoy triggers at >=70%

    def analyze_nlp(self, url):
        """
        Call DistilBERT microservice and return phishing probability.
        """
        try:
            response = requests.post(
                self.nlp_endpoint,
                json={"url": url},
                timeout=5
            )
            if response.status_code == 200:
                result = response.json()
                # result contains: {"url":..., "is_phishing": bool, "confidence": float}
                # The 'confidence' from the service is now probability of phishing (class 1)
                phishing_prob = result["confidence"]
                # We also keep the is_phishing flag for convenience
                return {
                    "is_phishing": result["is_phishing"],
                    "confidence": phishing_prob
                }
            else:
                return self._heuristic_fallback(url)
        except Exception as e:
            print(f"NLP service error: {e}")
            return self._heuristic_fallback(url)

    def _heuristic_fallback(self, url):
        """
        Simple keyword-based fallback if NLP service is down.
        """
        suspicious_keywords = ["login", "verify", "secure", "account", "update", "signin", "banking", "paypal"]
        score = 0.0
        url_lower = url.lower()
        for kw in suspicious_keywords:
            if kw in url_lower:
                score += 0.15
        score = min(score, 0.95)
        # Check trusted domains to lower score
        trusted = ["google.com", "facebook.com", "amazon.com", "microsoft.com", "github.com", "apple.com"]
        for t in trusted:
            if t in url_lower:
                score = max(0.0, score - 0.5)
        is_phish = score > 0.5
        return {"is_phishing": is_phish, "confidence": score}

    def analyze_visual(self, screenshot_base64=None):
        """
        Placeholder for visual model analysis.
        In Phase 5 (extension), we'll call the model in-browser via TensorFlow.js.
        For now, we simulate a low-confidence result (0.0) or could accept precomputed score.
        """
        if screenshot_base64 is None:
            return {"is_phishing": False, "confidence": 0.0, "available": False}
        else:
            # In a real scenario, we would run ONNX model here.
            # For now, return neutral.
            return {"is_phishing": False, "confidence": 0.5, "available": True}

    def compute_final_decision(self, url, screenshot_base64=None, visual_score=None):
        """
        Main method to combine both modalities.
        If visual_score is provided (e.g., from extension), use it; otherwise call analyze_visual().
        Returns dict with final decision, confidence, and individual results.
        """
        # Get NLP result (phishing probability)
        nlp_result = self.analyze_nlp(url)
        nlp_conf = nlp_result["confidence"]          # now correctly phishing probability

        # Get visual result
        if visual_score is not None:
            visual_conf = visual_score
            visual_available = True
        else:
            vis = self.analyze_visual(screenshot_base64)
            visual_conf = vis["confidence"]
            visual_available = vis.get("available", False)

        # Combine confidences (weighted average)
        if not visual_available:
            final_conf = nlp_conf
        else:
            final_conf = (self.visual_weight * visual_conf) + (self.nlp_weight * nlp_conf)

        is_phishing = final_conf > 0.5
        trigger_decoy = final_conf >= self.confidence_threshold

        return {
            "is_phishing": is_phishing,
            "confidence": final_conf,
            "trigger_decoy": trigger_decoy,
            "visual_confidence": visual_conf,
            "nlp_confidence": nlp_conf,
            "visual_available": visual_available
        }