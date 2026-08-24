"""
Two compiled LangGraph pipelines — selected at campaign creation time.

Config A — Sequential (baseline):
    strategy_node ──► content_node ──► END
    One LLM plans ALL platforms together, then content_node enriches each post.

Config B — Hierarchical (treatment):
    orchestrator_node ──► [platform sub-agents run in parallel] ──► content_node ──► END
    Orchestrator briefs isolated platform specialists, then content_node adds images.
"""

from langgraph.graph import StateGraph, END

from src.services.state import CampaignState
from src.agents.strategy import strategy_node
from src.agents.content import content_node
from src.agents.orchestrator import orchestrator_node


def build_sequential_graph():
    """Config A — sequential pipeline (baseline)."""
    graph = StateGraph(CampaignState)
    graph.add_node("strategy", strategy_node)
    graph.add_node("content", content_node)
    graph.set_entry_point("strategy")
    graph.add_edge("strategy", "content")
    graph.add_edge("content", END)
    return graph.compile()


def build_hierarchical_graph():
    """Config B — hierarchical pipeline (treatment)."""
    graph = StateGraph(CampaignState)
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("content", content_node)
    graph.set_entry_point("orchestrator")
    graph.add_edge("orchestrator", "content")
    graph.add_edge("content", END)
    return graph.compile()


# Pre-compiled instances — imported by main.py
sequential_graph   = build_sequential_graph()    # Config A
hierarchical_graph = build_hierarchical_graph()  # Config B

# Backwards-compatible alias (Config A)
campaign_graph = sequential_graph


def get_graph(orchestration_mode: str):
    """Return the correct compiled graph based on orchestration mode."""
    if orchestration_mode == "hierarchical":
        return hierarchical_graph
    return sequential_graph
