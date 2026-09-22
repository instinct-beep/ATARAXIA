# Ataraxia — AI-Driven Social Media Analytics Framework

**Problem Statement:** SIH26152 — Social Media Analytics
**Theme:** Blockchain & Cybersecurity
**Organisation:** National Technical Research Organisation (NTRO)

Ataraxia fuses four vectors of social media intelligence — **sentiment, demographics, trends, and network topology** — into a single unified pipeline that delivers causal intelligence instead of fragmented metrics.

## The Problem

Today's tools analyze sentiment, demographics, trends, and networks in isolation. The result is four dashboards and zero actionable intelligence. You know *what* is trending but not *who* started it. You know *who* is angry but not *why* or *what to do*. You know *who* influences whom but not *what* they're spreading.

**Fusion creates causation. Causation enables action.**

## Solution Components

| Component | Module | What It Does |
|-----------|--------|--------------|
| **A. Data Collection** | `collector.py` | Multi-platform ingestion (X, Telegram, Reddit) with deduplication and time-stamped storage |
| **B. Sentiment** | `sentiment_engine.py` | Two-layer classifier: emotional vs neutral → 6 specific emotions including sarcasm |
| **C. Demographics** | `demographics_engine.py` | Aggregate, anonymized inference of age, region, language, interests. Zero PII stored |
| **D. Trends** | `trends_engine.py` | Graph-based community detection, 27× faster than BERT baselines |
| **E. Network** | `network_engine.py` | KOL identification, centrality measures, diffusion simulation |
| **Unified Dashboard** | `app.py` | Streamlit interface integrating all five components |

## Quick Start

### Install dependencies

```bash
pip install -r requirements.txt