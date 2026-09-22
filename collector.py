"""
Ataraxia — Continuous Data Collection Engine
SIH26152 Component A: Multi-Platform Ingestion Pipeline
"""

import json
import hashlib
import time
import threading
from datetime import datetime, timezone
from queue import Queue, Empty
from dataclasses import dataclass, asdict
from typing import Optional, Callable
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("AtaraxiaCollector")

# ============================================================
# UNIFIED DATA MODEL
# ============================================================
@dataclass
class UnifiedPost:
    """Normalized post across all platforms."""
    post_id: str
    platform: str
    timestamp: str
    text: str
    user_hash: str
    user_display: str
    language: str
    hashtags: list
    mentions: list
    metrics: dict
    thread_context: Optional[str] = None
    media_urls: Optional[list] = None
    geo: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict())

# ============================================================
# KAFKA PRODUCER (Simulated — swap with confluent_kafka in prod)
# ============================================================
class KafkaProducerWrapper:
    """
    Wraps Kafka producer. In production, replace with:
    from confluent_kafka import Producer
    """
    def __init__(self, topic="raw-social-posts", bootstrap_servers="localhost:9092"):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.buffer = []
        self.lock = threading.Lock()
        self.total_produced = 0
        logger.info(f"Kafka producer initialized: topic={topic}")

    def produce(self, post: UnifiedPost):
        """Send a normalized post to Kafka topic."""
        with self.lock:
            self.buffer.append(post.to_dict())
            self.total_produced += 1
            # In production: self.producer.produce(self.topic, value=post.to_json())
            # self.producer.flush()
            if self.total_produced % 100 == 0:
                logger.info(f"Produced {self.total_produced} posts to {self.topic}")

    def get_stats(self):
        return {
            "topic": self.topic,
            "total_produced": self.total_produced,
            "buffer_size": len(self.buffer)
        }

# ============================================================
# DEDUPLICATION ENGINE
# ============================================================
class DeduplicationEngine:
    """Hash-based deduplication to prevent duplicate ingestion."""
    def __init__(self, max_cache=100000):
        self.seen = set()
        self.max_cache = max_cache

    def is_duplicate(self, post_id: str, platform: str) -> bool:
        key = hashlib.sha256(f"{platform}:{post_id}".encode()).hexdigest()[:16]
        if key in self.seen:
            return True
        self.seen.add(key)
        if len(self.seen) > self.max_cache:
            # Remove oldest 10%
            self.seen = set(list(self.seen)[self.max_cache // 10:])
        return False

# ============================================================
# PLATFORM CONNECTOR: X (Twitter) — Filtered Stream
# ============================================================
class TwitterConnector:
    """
    Connects to X API v2 Filtered Stream.

    Requirements:
    - Bearer token (X Developer Portal)
    - pip install tweepy

    In production:
        client = tweepy.StreamingClient(bearer_token)
        client.add_rules(tweepy.StreamRule("india OR election OR flood"))
        client.filter(tweet_fields=["created_at","lang","geo"])
    """
    PLATFORM = "X (Twitter)"

    def __init__(self, bearer_token: str, rules: list = None):
        self.bearer_token = bearer_token
        self.rules = rules or ["india", "election", "flood", "health"]
        self.is_running = False
        self.connection_status = "idle"
        logger.info(f"Twitter connector configured with {len(self.rules)} rules")

    def start(self, on_post: Callable[[UnifiedPost], None]):
        """Start streaming (simulated for prototype)."""
        self.is_running = True
        self.connection_status = "connected"
        logger.info("Twitter filtered stream started (simulated)")

    def simulate_post(self):
        """Generate a realistic post for demo purposes."""
        import random
        texts = [
            "The flood situation in Assam is getting worse. Need immediate action. #AssamFloods",
            "Great initiative by the government on digital India. #DigitalIndia #Progress",
            "This policy is just wonderful 🙄 (sarcasm). #PolicyFail",
            "Standing with the farmers. #FarmersProtest #Support",
            "Anxiety about the upcoming elections. Too much misinformation spreading.",
            "Tech news: AI revolution is changing everything. #AI #Tech",
            "Health alert: New strain detected. Stay safe. #HealthAlert",
            "Against this decision completely. #Protest",
        ]
        hashtag_pool = ["AssamFloods", "DigitalIndia", "FarmersProtest", "AI", "Election2026", "HealthAlert", "ClimateAction", "TechNews"]
        post = UnifiedPost(
            post_id=f"x_{int(time.time())}_{random.randint(1000,9999)}",
            platform=self.PLATFORM,
            timestamp=datetime.now(timezone.utc).isoformat(),
            text=random.choice(texts),
            user_hash=hashlib.sha256(f"x_user_{random.randint(1,500)}".encode()).hexdigest()[:12],
            user_display=f"@user_{random.randint(1,500)}",
            language="en",
            hashtags=random.sample(hashtag_pool, random.randint(1, 3)),
            mentions=[],
            metrics={
                "likes": random.randint(0, 500),
                "retweets": random.randint(0, 200),
                "replies": random.randint(0, 50)
            }
        )
        return post

# ============================================================
# PLATFORM CONNECTOR: Telegram — Telethon Event Handler
# ============================================================
class TelegramConnector:
    """
    Connects to Telegram via Telethon.

    Requirements:
    - api_id, api_hash from my.telegram.org
    - pip install telethon

    In production:
        from telethon import TelegramClient, events
        client = TelegramClient('session', api_id, api_hash)
        @client.on(events.NewMessage(chats=['channel1','channel2']))
        async def handler(event):
            post = event.message.text
    """
    PLATFORM = "Telegram"

    def __init__(self, api_id: str = None, api_hash: str = None, channels: list = None):
        self.api_id = api_id
        self.api_hash = api_hash
        self.channels = channels or ["@newsindia", "@healthalert", "@election2026"]
        self.is_running = False
        self.connection_status = "idle"
        logger.info(f"Telegram connector configured with {len(self.channels)} channels")

    def start(self, on_post: Callable[[UnifiedPost], None]):
        self.is_running = True
        self.connection_status = "connected"
        logger.info("Telegram event handler started (simulated)")

    def simulate_post(self):
        import random
        texts = [
            "🚨 BREAKING: Flood warning issued for 3 districts. Evacuate immediately.",
            "Forwarded from a trusted source: Election dates announced.",
            "Health ministry update: New vaccination drive starts Monday.",
            "Farmers protest continues at Delhi border. Support needed.",
            "Warning: Fake news circulating about water supply. Verify before sharing.",
            "AI can now detect early signs of disease. Remarkable progress.",
        ]
        post = UnifiedPost(
            post_id=f"tg_{int(time.time())}_{random.randint(1000,9999)}",
            platform=self.PLATFORM,
            timestamp=datetime.now(timezone.utc).isoformat(),
            text=random.choice(texts),
            user_hash=hashlib.sha256(f"tg_user_{random.randint(1,300)}".encode()).hexdigest()[:12],
            user_display=f"tg_user_{random.randint(1,300)}",
            language=random.choice(["en", "hi", "mr"]),
            hashtags=random.sample(["Breaking", "Flood", "Election", "Health", "Farmers", "AI"], random.randint(0, 2)),
            mentions=[],
            metrics={"views": random.randint(100, 5000), "forwards": random.randint(0, 300)}
        )
        return post

# ============================================================
# PLATFORM CONNECTOR: Reddit — PRAW Streaming
# ============================================================
class RedditConnector:
    """
    Connects to Reddit via PRAW streaming.

    Requirements:
    - Reddit API credentials (client_id, client_secret)
    - pip install praw

    In production:
        import praw
        reddit = praw.Reddit(...)
        for comment in reddit.subreddit("india+worldnews").stream.comments():
            process(comment)
    """
    PLATFORM = "Reddit"

    def __init__(self, client_id: str = None, client_secret: str = None, subreddits: list = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.subreddits = subreddits or ["india", "worldnews", "technology"]
        self.is_running = False
        self.connection_status = "idle"
        logger.info(f"Reddit connector configured with {len(self.subreddits)} subreddits")

    def start(self, on_post: Callable[[UnifiedPost], None]):
        self.is_running = True
        self.connection_status = "connected"

    def simulate_post(self):
        import random
        texts = [
            "ELI5: Why is the flood situation in Assam so severe this year?",
            "Analysis: The election misinformation problem is getting worse.",
            "Health study: Vitamin D deficiency is rampant in urban India.",
            "Discussion: How AI is being used for disaster response.",
            "Opinion: We need better climate policy before it's too late.",
        ]
        post = UnifiedPost(
            post_id=f"rd_{int(time.time())}_{random.randint(1000,9999)}",
            platform=self.PLATFORM,
            timestamp=datetime.now(timezone.utc).isoformat(),
            text=random.choice(texts),
            user_hash=hashlib.sha256(f"rd_user_{random.randint(1,200)}".encode()).hexdigest()[:12],
            user_display=f"u/user_{random.randint(1,200)}",
            language="en",
            hashtags=[],
            mentions=[],
            metrics={"upvotes": random.randint(0, 2000), "comments": random.randint(0, 500)}
        )
        return post

# ============================================================
# INGESTION ORCHESTRATOR
# ============================================================
class IngestionOrchestrator:
    """Manages all platform connectors, Kafka producer, and deduplication."""

    def __init__(self):
        self.producer = KafkaProducerWrapper()
        self.dedup = DeduplicationEngine()
        self.connectors = {}
        self.collected_posts = []
        self.is_running = False
        self.total_collected = 0
        self.duplicates_blocked = 0
        self.start_time = None
        self._lock = threading.Lock()

    def register_connector(self, name: str, connector):
        self.connectors[name] = connector
        logger.info(f"Registered connector: {name} ({connector.PLATFORM})")

    def ingest_post(self, post: UnifiedPost) -> bool:
        """Ingest a single post: deduplicate → produce to Kafka → store."""
        if self.dedup.is_duplicate(post.post_id, post.platform):
            with self._lock:
                self.duplicates_blocked += 1
            return False

        self.producer.produce(post)

        with self._lock:
            self.collected_posts.append(post.to_dict())
            self.total_collected += 1
            if len(self.collected_posts) > 500:
                self.collected_posts = self.collected_posts[-500:]

        return True

    def start_all(self):
        self.is_running = True
        self.start_time = datetime.now(timezone.utc)
        for name, conn in self.connectors.items():
            conn.start(lambda p: self.ingest_post(p))
        logger.info(f"All {len(self.connectors)} connectors started")

    def stop_all(self):
        self.is_running = False
        for conn in self.connectors.values():
            conn.is_running = False
        logger.info("All connectors stopped")

    def collect_batch(self, n=10):
        """Collect n posts from each active connector."""
        for conn in self.connectors.values():
            if conn.is_running:
                for _ in range(n):
                    if hasattr(conn, 'simulate_post'):
                        post = conn.simulate_post()
                        self.ingest_post(post)

    def get_status(self):
        return {
            "is_running": self.is_running,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "total_collected": self.total_collected,
            "duplicates_blocked": self.duplicates_blocked,
            "connectors": {
                name: {
                    "platform": conn.PLATFORM,
                    "status": conn.connection_status,
                    "running": conn.is_running
                } for name, conn in self.connectors.items()
            },
            "kafka": self.producer.get_stats(),
            "buffer_size": len(self.collected_posts)
        }

    def get_recent_posts(self, n=50):
        return self.collected_posts[-n:]

# ============================================================
# GLOBAL INSTANCE (for Streamlit import)
# ============================================================
_orchestrator = None

def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = IngestionOrchestrator()
        _orchestrator.register_connector("twitter", TwitterConnector(bearer_token="DEMO"))
        _orchestrator.register_connector("telegram", TelegramConnector(api_id="DEMO", api_hash="DEMO"))
        _orchestrator.register_connector("reddit", RedditConnector(client_id="DEMO", client_secret="DEMO"))
        _orchestrator.start_all()
    return _orchestrator

# ============================================================
# CLI TEST
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("ATARAXIA — Data Collection Engine Test")
    print("=" * 60)
    orch = get_orchestrator()
    print("\n[Simulating 30 seconds of collection...]\n")
    for i in range(30):
        orch.collect_batch(n=3)
        time.sleep(0.1)
        if (i + 1) % 10 == 0:
            status = orch.get_status()
            print(f"T+{i+1}s | Collected: {status['total_collected']} | Dupes blocked: {status['duplicates_blocked']}")
    print("\n" + "=" * 60)
    print("FINAL STATUS")
    print("=" * 60)
    print(json.dumps(orch.get_status(), indent=2))
    print("\nRecent posts sample:")
    for p in orch.get_recent_posts(3):
        print(f"  [{p['platform']}] {p['text'][:60]}...")