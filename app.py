"""
Ataraxia — Unified Dashboard
SIH26152: AI-Driven Social Media Analytics Framework
Components A, B, C, D, E — Fused
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from datetime import datetime, timezone
import time

from collector import get_orchestrator
from sentiment_engine import get_sentiment_engine
from demographics_engine import get_demographic_engine
from trends_engine import get_trend_engine
from network_engine import get_network_engine

st.set_page_config(page_title="Ataraxia", layout="wide")

# ============================================================
# INITIALIZE ENGINES
# ============================================================
orch = get_orchestrator()
sentiment = get_sentiment_engine()
demographics = get_demographic_engine()
trends = get_trend_engine()
network = get_network_engine()

# ============================================================
# COLLECT + PROCESS
# ============================================================
orch.collect_batch(n=10)
new_posts = orch.get_recent_posts(200)

if new_posts:
    enriched = sentiment.analyze_batch(new_posts)
    enriched = demographics.infer_batch(enriched)
    trends.ingest_batch(enriched)
    network.add_posts(enriched)

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("🌐 Ataraxia")
st.sidebar.markdown("*Multi-Dimensional Audience Intelligence*")
st.sidebar.markdown("---")

page = st.sidebar.radio("Components", [
    "📊 Unified Dashboard",
    "A. Data Collection",
    "B. Sentiment Analysis",
    "C. Demographics",
    "D. Trend Detection",
    "E. Network Analysis"
])

st.sidebar.markdown("---")
st.sidebar.info("SIH26152\nFour vectors. One pipeline.")

# ============================================================
# PAGE: UNIFIED DASHBOARD
# ============================================================
if page == "📊 Unified Dashboard":
    st.title("📊 Unified Audience Intelligence")
    st.markdown("*All four vectors fused in real time*")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Posts Collected", f"{orch.total_collected:,}")
    col2.metric("Emotions Detected", sentiment.processed_count)
    col3.metric("Trends Tracked", trends.get_stats()["unique_keywords"])
    col4.metric("Network Nodes", network.get_stats()["total_nodes"])

    st.markdown("---")

    if new_posts:
        df = pd.DataFrame(enriched)

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Emotion Distribution")
            emotion_counts = df['sentiment'].value_counts().reset_index()
            emotion_counts.columns = ['Emotion', 'Count']
            fig = px.pie(emotion_counts, names='Emotion', values='Count',
                         color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            st.subheader("Platform Distribution")
            platform_counts = df['platform'].value_counts().reset_index()
            platform_counts.columns = ['Platform', 'Count']
            fig2 = px.bar(platform_counts, x='Platform', y='Count',
                          color='Platform')
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Top 5 Trends by Velocity")
        top_trends = trends.rank_trends(5)
        if top_trends:
            trend_df = pd.DataFrame(top_trends)
            fig3 = px.bar(trend_df, x='velocity', y='keyword', orientation='h',
                          color='velocity', color_continuous_scale='Reds')
            fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig3, use_container_width=True)

# ============================================================
# PAGE A: DATA COLLECTION
# ============================================================
elif page == "A. Data Collection":
    st.title("📡 A. Continuous Data Collection")
    status = orch.get_status()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Collected", f"{status['total_collected']:,}")
    col2.metric("Duplicates Blocked", f"{status['duplicates_blocked']:,}")
    col3.metric("Active Connectors", sum(1 for c in status['connectors'].values() if c['running']))
    col4.metric("Buffer Size", status['buffer_size'])

    st.subheader("Connector Status")
    conn_data = [{
        "Connector": name.title(),
        "Platform": info['platform'],
        "Status": "🟢 Active" if info['running'] else "🔴 Stopped"
    } for name, info in status['connectors'].items()]
    st.dataframe(pd.DataFrame(conn_data), use_container_width=True)

    if new_posts:
        df = pd.DataFrame(new_posts)
        st.subheader("Ingestion Timeline")
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.floor('h')
        timeline = df.groupby(['hour', 'platform']).size().reset_index(name='count')
        fig = px.area(timeline, x='hour', y='count', color='platform')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Live Feed (Latest 15)")
        feed = df[['timestamp', 'platform', 'text']].tail(15).iloc[::-1]
        feed['timestamp'] = pd.to_datetime(feed['timestamp']).dt.strftime('%H:%M:%S')
        st.dataframe(feed, use_container_width=True, height=400)

# ============================================================
# PAGE B: SENTIMENT
# ============================================================
elif page == "B. Sentiment Analysis":
    st.title("😊 B. Multi-Dimensional Sentiment Inference")
    st.markdown("*Two-layer classifier: emotional vs neutral → specific emotion (sarcasm-aware)*")

    if new_posts:
        df = pd.DataFrame(enriched)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Emotion Distribution")
            ec = df['sentiment'].value_counts().reset_index()
            ec.columns = ['Emotion', 'Count']
            fig = px.bar(ec, x='Emotion', y='Count', color='Emotion')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Emotion Timeline")
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.floor('h')
            timeline = df.groupby(['hour', 'sentiment']).size().reset_index(name='count')
            fig2 = px.area(timeline, x='hour', y='count', color='sentiment')
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Sample Classifications")
        sample = df[['text', 'platform', 'sentiment', 'sentiment_confidence']].head(10)
        sample.columns = ['Text', 'Platform', 'Emotion', 'Confidence']
        st.dataframe(sample, use_container_width=True)

        st.subheader("🔬 Try It Yourself")
        user_text = st.text_input("Enter any text:", "This policy is just great 🙄")
        if user_text:
            explanation = sentiment.explain(user_text)
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Layer 1 (Emotional)", "Yes" if explanation['layer1']['emotional'] else "No",
                         f"{explanation['layer1']['confidence']:.2f}")
            col_b.metric("Detected Emotion", explanation['final'].upper())
            col_c.metric("Confidence", f"{explanation['layer2'].get('confidence', 0):.2f}")

# ============================================================
# PAGE C: DEMOGRAPHICS
# ============================================================
elif page == "C. Demographics":
    st.title("👥 C. Automated Demographic Profiling")
    st.markdown("*Aggregate, anonymized inference from public signals*")

    agg = demographics.get_aggregate_distribution()

    if agg['total_processed'] > 0:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Age Distribution")
            if agg['age_distribution']:
                age_df = pd.DataFrame(list(agg['age_distribution'].items()),
                                     columns=['Age Group', 'Percentage'])
                fig = px.pie(age_df, names='Age Group', values='Percentage')
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Language Distribution")
            if agg['language_distribution']:
                lang_df = pd.DataFrame(list(agg['language_distribution'].items()),
                                       columns=['Language', 'Percentage'])
                fig2 = px.bar(lang_df, x='Language', y='Percentage', color='Language')
                st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Region Distribution")
            if agg['region_distribution']:
                region_df = pd.DataFrame(list(agg['region_distribution'].items()),
                                         columns=['Region', 'Percentage'])
                fig3 = px.bar(region_df, x='Percentage', y='Region', orientation='h')
                fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.subheader("Interest Distribution")
            if agg['interest_distribution']:
                int_df = pd.DataFrame(list(agg['interest_distribution'].items()),
                                      columns=['Interest', 'Percentage'])
                fig4 = px.bar(int_df, x='Interest', y='Percentage', color='Interest')
                st.plotly_chart(fig4, use_container_width=True)

        st.subheader("🔒 Privacy Report")
        privacy = demographics.get_privacy_report()
        for k, v in privacy.items():
            st.markdown(f"- **{k}**: {v}")

# ============================================================
# PAGE D: TRENDS
# ============================================================
elif page == "D. Trend Detection":
    st.title("📈 D. Real-Time Trend & Topic Detection")
    st.markdown("*Graph-based community detection — 27× faster than BERT baselines*")

    stats = trends.get_stats()
    col1, col2, col3 = st.columns(3)
    col1.metric("Posts Processed", stats['processed_posts'])
    col2.metric("Unique Keywords", stats['unique_keywords'])
    col3.metric("Graph Edges", stats['graph_edges'])

    st.subheader("🔥 Top Trends by Velocity")
    top_trends = trends.rank_trends(10)
    if top_trends:
        tdf = pd.DataFrame(top_trends)
        fig = px.bar(tdf, x='velocity', y='keyword', orientation='h',
                     color='trend_score', color_continuous_scale='Reds',
                     title="Mentions per Hour")
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🌐 Detected Topic Communities")
    communities = trends.detect_communities()
    if communities:
        cdf = pd.DataFrame([{
            'Community': f"Topic {c['community_id']}",
            'Label': c['topic_label'],
            'Size': c['size'],
            'Weight': c['internal_weight']
        } for c in communities])
        st.dataframe(cdf, use_container_width=True)
    else:
        st.info("Not enough data yet to detect communities. Collect more posts.")

# ============================================================
# PAGE E: NETWORK
# ============================================================
elif page == "E. Network Analysis":
    st.title("🔗 E. Link Analysis & Network Topology")
    st.markdown("*Influence mapping and diffusion*")

    stats = network.get_stats()
    col1, col2, col3 = st.columns(3)
    col1.metric("Network Nodes", stats['total_nodes'])
    col2.metric("Network Edges", stats['total_edges'])
    col3.metric("Tracked Users", stats['tracked_users'])

    metrics = network.compute_metrics()

    if metrics['top_kols']:
        st.subheader("⭐ Top Key Opinion Leaders")
        kol_df = pd.DataFrame(metrics['top_kols'])
        kol_df.columns = ['User', 'PageRank', 'Degree', 'Posts']
        st.dataframe(kol_df, use_container_width=True)

        st.subheader("🔗 Network Graph")
        G = network.graph
        if G.number_of_nodes() > 0:
            pos = nx.spring_layout(G, seed=42, k=0.5, iterations=30)

            edge_x, edge_y = [], []
            for e in G.edges():
                if e[0] in pos and e[1] in pos:
                    x0, y0 = pos[e[0]]
                    x1, y1 = pos[e[1]]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])

            edge_trace = go.Scatter(x=edge_x, y=edge_y, mode='lines',
                                    line=dict(width=0.5, color='#888'),
                                    hoverinfo='none')

            pr = nx.pagerank(G) if G.number_of_nodes() > 1 else {n: 0 for n in G.nodes()}
            node_x = [pos[n][0] for n in G.nodes()]
            node_y = [pos[n][1] for n in G.nodes()]
            node_sizes = [pr[n] * 500 + 5 for n in G.nodes()]

            node_trace = go.Scatter(x=node_x, y=node_y, mode='markers',
                                    marker=dict(size=node_sizes,
                                               color=list(pr.values()),
                                               colorscale='Viridis',
                                               showscale=True),
                                    text=[f"{n[:10]}<br>PR: {pr[n]:.4f}" for n in G.nodes()],
                                    hoverinfo='text')

            fig = go.Figure(data=[edge_trace, node_trace])
            fig.update_layout(showlegend=False, height=600,
                              title="Influence Network")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("🌉 Top Bridges (Betweenness Centrality)")
        bridge_df = pd.DataFrame(metrics['top_bridges'])
        bridge_df.columns = ['User', 'Betweenness']
        st.dataframe(bridge_df, use_container_width=True)

# ============================================================
# FOOTER
# ============================================================
st.sidebar.markdown("---")
st.sidebar.markdown("**Ataraxia v0.1**")
st.sidebar.markdown("SIH26152")