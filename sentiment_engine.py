"""
Ataraxia — Component B: Multi-Dimensional Sentiment Inference
Two-layer classifier: emotional vs neutral → specific emotion (sarcasm-aware)
"""

import re
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger("Ataraxia.Sentiment")

# ============================================================
# LEXICONS (In production: replace with fine-tuned RoBERTa)
# ============================================================
LEXICONS = {
    "joy": {
        "words": ["great", "amazing", "wonderful", "fantastic", "happy", "celebrate",
                  "good", "excellent", "love", "best", "awesome", "brilliant"],
        "emojis": ["😊", "😀", "🎉", "❤️", "😍", "👏", "🙌", "✨"],
    },
    "anger": {
        "words": ["angry", "furious", "outrage", "disgusting", "hate", "terrible",
                  "awful", "worst", "damn", "pathetic", "shameful"],
        "emojis": ["😡", "🤬", "😠", "💢"],
    },
    "anxiety": {
        "words": ["worried", "scared", "terrified", "anxious", "fear", "panic",
                  "nervous", "concerned", "danger", "threat", "emergency", "warning"],
        "emojis": ["😰", "😨", "😱", "😟"],
    },
    "sarcasm": {
        "patterns": [
            r"just\s+great", r"oh\s+sure", r"yeah\s+right", r"wonderful\s+\(not\)",
            r"🙄", r"great\s+job\s+\(sarcasm\)", r"totally\s+fine", r"brilliant\s+idea\s+🙄"
        ],
        "indicators": ["(not)", "🙄", "sure", "obviously", "totally"],
    },
    "supportive": {
        "words": ["support", "stand with", "solidarity", "together", "unity",
                  "backing", "endorse", "for", "yes", "agree", "correct"],
        "emojis": ["✊", "🤝", "💪", "❤️‍🔥"],
    },
    "against": {
        "words": ["against", "oppose", "reject", "no", "down with", "boycott",
                  "protest", "condemn", "denounce", "resist"],
        "emojis": ["❌", "🚫", "👎"],
    },
}

INTENSITY_MODIFIERS = {
    "very": 1.5, "extremely": 1.8, "absolutely": 1.9, "completely": 1.7,
    "really": 1.4, "so": 1.3, "totally": 1.6, "utterly": 1.9,
    "slightly": 0.5, "somewhat": 0.6, "a bit": 0.7,
}

# ============================================================
# LAYER 1: EMOTIONAL vs NEUTRAL
# ============================================================
def is_emotional(text: str) -> Tuple[bool, float]:
    """Layer 1: Determine if text carries emotional content."""
    if not text:
        return False, 0.0

    text_lower = text.lower()
    score = 0

    for emotion, data in LEXICONS.items():
        for word in data.get("words", []):
            if word in text_lower:
                score += 1
        for emoji in data.get("emojis", []):
            if emoji in text:
                score += 1

    # Sarcasm patterns
    for pattern in LEXICONS["sarcasm"].get("patterns", []):
        if re.search(pattern, text_lower):
            score += 2

    # Punctuation intensity
    if "!" in text:
        score += text.count("!")
    if "?" in text and text.count("?") > 1:
        score += 1

    confidence = min(score / 3.0, 1.0)
    return score > 0, confidence

# ============================================================
# LAYER 2: SPECIFIC EMOTION CLASSIFICATION
# ============================================================
def classify_emotion(text: str) -> Dict:
    """Layer 2: Classify specific emotion with sarcasm priority."""
    if not text:
        return {"emotion": "neutral", "confidence": 1.0, "all_scores": {}}

    text_lower = text.lower()
    scores = {emotion: 0.0 for emotion in LEXICONS.keys()}

    # Check sarcasm first (highest priority)
    sarcasm_score = 0
    for pattern in LEXICONS["sarcasm"].get("patterns", []):
        if re.search(pattern, text_lower):
            sarcasm_score += 3
    for indicator in LEXICONS["sarcasm"].get("indicators", []):
        if indicator in text_lower:
            sarcasm_score += 1
    scores["sarcasm"] = sarcasm_score

    # Score other emotions
    for emotion, data in LEXICONS.items():
        if emotion == "sarcasm":
            continue
        for word in data.get("words", []):
            if word in text_lower:
                scores[emotion] += 1.0
                # Check for intensity modifiers
                for mod, mult in INTENSITY_MODIFIERS.items():
                    if f"{mod} {word}" in text_lower:
                        scores[emotion] += (mult - 1.0)
        for emoji in data.get("emojis", []):
            if emoji in text:
                scores[emotion] += 1.5

    # Normalize
    total = sum(scores.values())
    if total == 0:
        return {"emotion": "neutral", "confidence": 1.0, "all_scores": scores}

    dominant = max(scores, key=scores.get)
    confidence = scores[dominant] / total

    return {
        "emotion": dominant,
        "confidence": round(confidence, 3),
        "all_scores": {k: round(v, 3) for k, v in scores.items() if v > 0}
    }

# ============================================================
# MAIN ANALYZER
# ============================================================
class SentimentEngine:
    """Two-layer sentiment inference engine."""

    def __init__(self):
        self.processed_count = 0
        self.emotion_counts = {e: 0 for e in list(LEXICONS.keys()) + ["neutral"]}

    def analyze(self, post: dict) -> dict:
        """Analyze a single post. Returns enriched post with sentiment."""
        text = post.get("text", "")

        # Layer 1
        emotional, layer1_conf = is_emotional(text)

        # Layer 2
        if emotional:
            result = classify_emotion(text)
        else:
            result = {"emotion": "neutral", "confidence": 1.0, "all_scores": {}}

        self.processed_count += 1
        self.emotion_counts[result["emotion"]] = self.emotion_counts.get(result["emotion"], 0) + 1

        return {
            **post,
            "sentiment": result["emotion"],
            "sentiment_confidence": result["confidence"],
            "layer1_emotional": emotional,
            "layer1_confidence": round(layer1_conf, 3),
            "all_emotion_scores": result["all_scores"],
        }

    def analyze_batch(self, posts: List[dict]) -> List[dict]:
        return [self.analyze(p) for p in posts]

    def get_stats(self) -> dict:
        return {
            "processed": self.processed_count,
            "distribution": self.emotion_counts
        }

    def explain(self, text: str) -> dict:
        """Explain why a text was classified the way it was."""
        emotional, conf1 = is_emotional(text)
        emotion_result = classify_emotion(text) if emotional else {"emotion": "neutral", "confidence": 1.0, "all_scores": {}}

        return {
            "text": text,
            "layer1": {
                "emotional": emotional,
                "confidence": round(conf1, 3),
                "reason": "Emotional markers detected" if emotional else "No emotional markers"
            },
            "layer2": emotion_result,
            "final": emotion_result["emotion"]
        }

# Singleton
_engine = None

def get_sentiment_engine():
    global _engine
    if _engine is None:
        _engine = SentimentEngine()
    return _engine

# ============================================================
# CLI TEST
# ============================================================
if __name__ == "__main__":
    engine = get_sentiment_engine()

    test_posts = [
        "This policy is just great 🙄",
        "I'm terrified about the flood situation",
        "Finally some good news today!",
        "Oh sure, that'll work (not)",
        "We stand with the farmers ✊",
        "Absolutely against this decision. Down with corruption.",
        "The weather is nice today.",
        "EXTREMELY angry about this! Worst decision ever!",
    ]

    print("=" * 70)
    print("ATARAXIA — Sentiment Engine Test")
    print("=" * 70)
    for text in test_posts:
        result = engine.explain(text)
        print(f"\nText: {text}")
        print(f"  Layer 1: Emotional={result['layer1']['emotional']} (conf={result['layer1']['confidence']})")
        print(f"  Layer 2: {result['layer2']['emotion']} (conf={result['layer2'].get('confidence', 'N/A')})")
        print(f"  Final: {result['final']}")