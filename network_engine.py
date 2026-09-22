"""
Ataraxia — Component E: Link Analysis & Network Topology
Influence mapping, KOL identification, diffusion tracking.
"""

import networkx as nx
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger("Ataraxia.Network")

class NetworkEngine:
    """
    Builds a user interaction graph and computes influence metrics.
    Nodes: users (hashed)
    Edges: interactions (reply, mention, retweet)
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self.user_activity = defaultdict(int)  # user_hash -> post count
        self.interaction_types = Counter()

    def add_post(self, post: dict):
        """Add a post to the network. Creates edges from mentions/replies."""
        user = post.get("user_hash")
        if not user:
            return

        # Ensure user is a node
        if not self.graph.has_node(user):
            self.graph.add_node(user, platform=post.get("platform", "unknown"))

        self.user_activity[user] += 1

        # Add edges from mentions
        for mention in post.get("mentions", []) or []:
            self.graph.add_edge(user, mention, type="mention")
            self.interaction_types["mention"] += 1

        # Add edges from reply context
        reply_to = post.get("thread_context")
        if reply_to:
            self.graph.add_edge(user, reply_to, type="reply")
            self.interaction_types["reply"] += 1

    def add_posts(self, posts: List[dict]):
        for p in posts:
            self.add_post(p)

    def compute_metrics(self) -> Dict:
        """Compute centrality measures."""
        if self.graph.number_of_nodes() < 2:
            return {
                "nodes": self.graph.number_of_nodes(),
                "edges": self.graph.number_of_edges(),
                "top_kols": [],
                "top_bridges": [],
            }

        # Centrality measures
        degree = dict(self.graph.degree())
        try:
            pagerank = nx.pagerank(self.graph, alpha=0.85)
        except:
            pagerank = {n: 0 for n in self.graph.nodes()}

        try:
            betweenness = nx.betweenness_centrality(self.graph)
        except:
            betweenness = {n: 0 for n in self.graph.nodes()}

        # Top KOLs (highest PageRank)
        top_kols = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10]

        # Top bridges (highest betweenness)
        top_bridges = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "density": round(nx.density(self.graph), 4) if self.graph.number_of_nodes() > 1 else 0,
            "top_kols": [
                {
                    "user": u[:12],
                    "pagerank": round(p, 4),
                    "degree": degree.get(u, 0),
                    "posts": self.user_activity[u]
                } for u, p in top_kols
            ],
            "top_bridges": [
                {
                    "user": u[:12],
                    "betweenness": round(b, 4),
                } for u, b in top_bridges
            ],
            "interaction_breakdown": dict(self.interaction_types)
        }

    def detect_communities(self) -> List[Dict]:
        """Detect communities of users."""
        if self.graph.number_of_nodes() < 5:
            return []

        undirected = self.graph.to_undirected()
        try:
            communities = nx.community.louvain_communities(undirected, seed=42)
        except:
            communities = nx.community.greedy_modularity_communities(undirected)

        results = []
        for i, community in enumerate(communities):
            community = list(community)
            results.append({
                "community_id": i,
                "size": len(community),
                "users_sample": [u[:8] for u in community[:5]]
            })

        return sorted(results, key=lambda x: x['size'], reverse=True)

    def simulate_diffusion(self, start_node: str, steps: int = 5) -> List[Dict]:
        """Simulate information diffusion from a starting node."""
        if start_node not in self.graph:
            return []

        infected = {start_node}
        timeline = [{"step": 0, "infected": 1, "new": [start_node[:8]]}]

        frontier = {start_node}
        for step in range(1, steps + 1):
            new_infected = set()
            for node in frontier:
                for neighbor in self.graph.neighbors(node):
                    if neighbor not in infected:
                        new_infected.add(neighbor)
                for pred in self.graph.predecessors(node):
                    if pred not in infected:
                        new_infected.add(pred)

            infected.update(new_infected)
            timeline.append({
                "step": step,
                "infected": len(infected),
                "new": [u[:8] for u in list(new_infected)[:5]]
            })
            frontier = new_infected

            if not frontier:
                break

        return timeline

    def get_stats(self) -> Dict:
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "tracked_users": len(self.user_activity),
        }

# Singleton
_engine = None

def get_network_engine():
    global _engine
    if _engine is None:
        _engine = NetworkEngine()
    return _engine

# ============================================================
# CLI TEST
# ============================================================
if __name__ == "__main__":
    import random
    random.seed(42)

    engine = get_network_engine()

    # Create synthetic interactions
    users = [f"user_{i}" for i in range(30)]
    for _ in range(200):
        u1 = random.choice(users)
        u2 = random.choice(users)
        if u1 != u2:
            engine.add_post({
                "user_hash": u1,
                "mentions": [u2],
                "platform": "X",
                "text": "test"
            })

    print("=" * 70)
    print("ATARAXIA — Network Engine Test")
    print("=" * 70)

    print("\n📊 Network Stats:")
    for k, v in engine.get_stats().items():
        print(f"  {k}: {v}")

    metrics = engine.compute_metrics()
    print(f"\n📈 Metrics:")
    print(f"  Density: {metrics['density']}")
    print(f"  Interactions: {metrics['interaction_breakdown']}")

    print(f"\n⭐ Top 5 KOLs (by PageRank):")
    for k in metrics['top_kols'][:5]:
        print(f"  {k['user']}... PR={k['pagerank']}, degree={k['degree']}")

    print(f"\n🌉 Top 3 Bridges (by Betweenness):")
    for b in metrics['top_bridges'][:3]:
        print(f"  {b['user']}... BC={b['betweenness']}")

    print(f"\n🌐 Communities:")
    for c in engine.detect_communities()[:3]:
        print(f"  Community {c['community_id']}: size={c['size']}")

    if metrics['top_kols']:
        top_user = metrics['top_kols'][0]['user']
        # Find actual node
        for node in engine.graph.nodes():
            if node.startswith(top_user.split('_')[0]) or node[:12].startswith(top_user[:8]):
                print(f"\n🚀 Diffusion simulation from top KOL:")
                for step in engine.simulate_diffusion(node, steps=5):
                    print(f"  Step {step['step']}: {step['infected']} infected")
                break