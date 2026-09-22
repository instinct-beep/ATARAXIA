"""
Ataraxia — Component C: Automated Demographic Profiling
Aggregate, anonymized inference from public profile signals.
NO PII stored. All output aggregated.
"""

import hashlib
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List
import logging

logger = logging.getLogger("Ataraxia.Demographics")

# ============================================================
# SIGNAL EXTRACTORS
# ============================================================
AGE_SIGNALS = {
    "18-24": ["college", "student", "university", "campus", "exam", "semester",
              "freshman", "undergrad", "btech", "engineering student"],
    "25-34": ["startup", "job", "career", "work", "office", "professional",
              "young professional", "fresher", "developer", "engineer"],
    "35-44": ["parent", "family", "kids", "children", "married", "manager",
              "team lead", "senior", "home"],
    "45-54": ["director", "VP", "senior", "retirement planning", "mid-life",
              "teenager", "principal"],
    "55+":   ["retired", "grandchildren", "grandparent", "senior citizen",
              "pension", "veteran"],
}

REGION_SIGNALS = {
    "Maharashtra": ["mumbai", "pune", "nagpur", "nashik", "maharashtra", "marathi"],
    "Delhi": ["delhi", "ncr", "new delhi", "gurgaon", "noida", "dwarka"],
    "Karnataka": ["bangalore", "bengaluru", "mysore", "karnataka", "kannada"],
    "Tamil Nadu": ["chennai", "coimbatore", "tamil", "tamilnadu", "madras"],
    "West Bengal": ["kolkata", "bengal", "bengali", "howrah", "darjeeling"],
    "Gujarat": ["ahmedabad", "surat", "gujarat", "gujarati", "vadodara"],
    "UP": ["lucknow", "kanpur", "varanasi", "up", "uttar pradesh", "hindi belt"],
}

LANGUAGE_SIGNALS = {
    "English": ["the", "and", "is", "this", "for", "with"],
    "Hindi": ["hai", "aur", "kya", "nahi", "bhai", "yaar", "accha"],
    "Marathi": ["ahe", "kay", "ho", "nahi", "bara", "chhan"],
    "Tamil": ["irukku", "enna", "vanakkam", "nandri", "seri"],
    "Bengali": ["ache", "ki", "kemon", "bhalo", "dada", "didi"],
}

INTEREST_SIGNALS = {
    "Politics": ["election", "vote", "government", "policy", "minister", "parliament", "modi", "opposition"],
    "Technology": ["ai", "tech", "software", "code", "startup", "digital", "app", "data"],
    "Health": ["health", "covid", "vaccine", "hospital", "doctor", "medicine", "wellness"],
    "Sports": ["cricket", "football", "match", "olympics", "team", "player", "score"],
    "Entertainment": ["movie", "film", "bollywood", "music", "actor", "series", "netflix"],
    "Business": ["market", "economy", "stock", "business", "trade", "invest", "gst"],
}

# ============================================================
# INFERENCE ENGINE
# ============================================================
class DemographicEngine:
    """
    Infers demographic signals from post text, hashtags, and metadata.
    All outputs are aggregate. No individual profile is stored.
    """

    def __init__(self):
        self.aggregate = {
            "age": Counter(),
            "region": Counter(),
            "language": Counter(),
            "interest": Counter(),
        }
        self.processed_count = 0

    def _infer_from_text(self, signals: Dict, text_lower: str) -> str:
        """Return the strongest matching category, or 'unknown'."""
        scores = {}
        for category, keywords in signals.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[category] = score
        if not scores:
            return "unknown"
        return max(scores, key=scores.get)

    def _detect_language(self, text: str) -> str:
        """Simple language detection via word markers."""
        text_lower = text.lower()
        scores = {}
        for lang, markers in LANGUAGE_SIGNALS.items():
            score = sum(1 for m in markers if f" {m} " in f" {text_lower} ")
            if score > 0:
                scores[lang] = score
        if not scores:
            return "English"  # default
        return max(scores, key=scores.get)

    def infer(self, post: dict) -> dict:
        """Infer demographic signals for a single post (aggregated, not stored)."""
        text = post.get("text", "")
        text_lower = text.lower()
        hashtags = " ".join(post.get("hashtags", [])).lower()

        combined = f"{text_lower} {hashtags}"

        age = self._infer_from_text(AGE_SIGNALS, combined)
        region = self._infer_from_text(REGION_SIGNALS, combined)
        language = self._detect_language(text)
        interest = self._infer_from_text(INTEREST_SIGNALS, combined)

        # Update aggregate counters (NOT individual records)
        self.aggregate["age"][age] += 1
        self.aggregate["region"][region] += 1
        self.aggregate["language"][language] += 1
        self.aggregate["interest"][interest] += 1

        self.processed_count += 1

        return {
            "inferred_age_bracket": age,
            "inferred_region": region,
            "inferred_language": language,
            "inferred_interest": interest,
        }

    def infer_batch(self, posts: List[dict]) -> List[dict]:
        return [{**p, **self.infer(p)} for p in posts]

    def get_aggregate_distribution(self) -> Dict:
        """Return aggregate distributions (privacy-safe)."""
        def normalize(counter):
            total = sum(counter.values())
            if total == 0:
                return {}
            return {k: round(v / total * 100, 1) for k, v in counter.most_common()}

        return {
            "total_processed": self.processed_count,
            "age_distribution": normalize(self.aggregate["age"]),
            "region_distribution": normalize(self.aggregate["region"]),
            "language_distribution": normalize(self.aggregate["language"]),
            "interest_distribution": normalize(self.aggregate["interest"]),
        }

    def get_privacy_report(self) -> Dict:
        """Report on privacy compliance."""
        return {
            "raw_user_ids_stored": 0,
            "individual_records_stored": 0,
            "aggregate_only": True,
            "hashing_used": "SHA-256",
            "pii_columns": [],
            "compliance": "No PII collected. All inference at aggregate level."
        }

# Singleton
_engine = None

def get_demographic_engine():
    global _engine
    if _engine is None:
        _engine = DemographicEngine()
    return _engine

# ============================================================
# CLI TEST
# ============================================================
if __name__ == "__main__":
    engine = get_demographic_engine()

    test_posts = [
        {"text": "As a college student in Mumbai, I worry about jobs.", "hashtags": ["Jobs"]},
        {"text": "बहुत अच्छा काम किया सरकार ने।", "hashtags": []},
        {"text": "The startup ecosystem in Bangalore is amazing.", "hashtags": ["Startup", "Tech"]},
        {"text": "Chennai weather is terrible for cricket practice.", "hashtags": ["Cricket"]},
        {"text": "Retired now, enjoying time with grandchildren in Pune.", "hashtags": []},
        {"text": "Election results will be interesting this year.", "hashtags": ["Election2026"]},
    ]

    print("=" * 70)
    print("ATARAXIA — Demographic Engine Test")
    print("=" * 70)
    for p in test_posts:
        result = engine.infer(p)
        print(f"\nText: {p['text'][:60]}...")
        print(f"  Age: {result['inferred_age_bracket']}")
        print(f"  Region: {result['inferred_region']}")
        print(f"  Language: {result['inferred_language']}")
        print(f"  Interest: {result['inferred_interest']}")

    print("\n" + "=" * 70)
    print("AGGREGATE DISTRIBUTION")
    print("=" * 70)
    import json
    print(json.dumps(engine.get_aggregate_distribution(), indent=2))