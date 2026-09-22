# Ataraxia — Architecture

## System Overview

Ataraxia is a multi-layer social media analytics platform that ingests data from multiple platforms, processes it through four AI layers, and delivers fused intelligence via a unified dashboard.

## Layer 1: Data Ingestion

**Inputs:**
- X (Twitter) API v2 — Filtered Stream (Essential)
- Telegram Bot API — Telethon Event Handler (Essential)
- Reddit API — PRAW Streaming (Desirable)
- Instagram Graph API (Extensible)
- Facebook Graph API (Extensible)

**Processing:**
- Every post normalized into a unified schema
- SHA-256 hashing of user IDs before storage
- Hash-based deduplication
- ISO 8601 UTC timestamps

**Storage:**
- Apache Kafka topic: `raw-social-posts`
- PostgreSQL + TimescaleDB hypertable
- 90-day retention policy on raw posts

## Layer 2: Sentiment Analysis

**Method:** Two-layer classifier
- Layer 1: Emotional vs neutral (rule-based + emoji signals)
- Layer 2: 6 specific emotions — joy, anger, anxiety, sarcasm, supportive, against

**Sarcasm Handling:**
- Regex patterns: "oh sure", "yeah right", "just great (not)"
- Emoji markers: 🙄, 😐
- Priority in classification pipeline

**Production Path:** Fine-tuned RoBERTa (F1: 96.97% based on *Scientific Reports* 2026)

## Layer 3: Demographic Inference

**Method:** Signal extraction from text, hashtags, metadata
- Age bracket (5 classes)
- Region (7 Indian states)
- Language (5 languages)
- Interest (6 categories)

**Privacy:**
- Zero PII stored
- Only aggregate counters updated
- SHA-256 user hashing
- DPDP Act 2023 compliant

**Production Path:** Graph Neural Network using social connection patterns

## Layer 4: Trend Detection

**Method:** Graph-based community detection
1. Extract keywords (hashtags + filtered words)
2. Build co-occurrence graph
3. Run Louvain algorithm for community detection
4. Rank by velocity (mentions/hour)

**Performance:** 27× faster than BERT baselines (IEEE 2026)

## Layer 5: Network Analysis

**Method:** Directed graph of users and interactions
- Nodes: SHA-256 hashed user IDs
- Edges: mentions, replies, retweets

**Metrics:**
- PageRank — broadcasters
- Betweenness centrality — bridges
- Degree centrality — connectors
- Diffusion simulation — spread prediction

## Layer 6: Unified Dashboard

**Framework:** Streamlit
**Charts:** Plotly
**Graph Visualization:** NetworkX + Plotly

**Views:**
- Unified Dashboard
- Component A — Data Collection
- Component B — Sentiment
- Component C — Demographics
- Component D — Trends
- Component E — Network

## Production Architecture
┌──────────────────────────────────────────────────────────────┐
│ INGESTION LAYER │
│ X API v2 │ Telegram API │ Reddit API │ Kafka Producer │
└──────────────────────┬───────────────────────────────────────┘
│
▼
┌──────────────────────────────────────────────────────────────┐
│ APACHE KAFKA — raw-social-posts │
│ 3 partitions │ 7-day retention │ Replication factor: 2 │
└──────────────────────┬───────────────────────────────────────┘
│
▼
┌──────────────────────────────────────────────────────────────┐
│ CONSUMER + PROCESSOR │
│ Deduplication │ Validation │ Enrichment │
└──────────────────────┬───────────────────────────────────────┘
│
▼
┌──────────────────────────────────────────────────────────────┐
│ POSTGRESQL + TIMESCALEDB (Hypertable) │
│ Continuous Aggregates │ Retention Policies │ Read Replicas │
└──────────────────────┬───────────────────────────────────────┘
│
┌──────────────┼──────────────┐
▼ ▼ ▼
Sentiment Demographics Trends
Service Service Service
│ │ │
└──────────────┼──────────────┘
▼
Network Service
│
▼
FastAPI Gateway
│
▼
Streamlit Dashboard
│
▼
JWT Auth │ Audit Logs

text

## Security

- JWT authentication on dashboard
- SHA-256 hashed user IDs
- Aggregate-only demographic output
- Encrypted columns for sensitive data (Fernet)
- Audit logs for all API calls
- No PII stored — DPDP Act 2023 compliant