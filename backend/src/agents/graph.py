from langgraph.graph import StateGraph, END

from src.services.state import CampaignState
from src.agents.strategy import strategy_node
from src.agents.content import content_node


def build_graph():
    graph = StateGraph(CampaignState)

    graph.add_node("strategy", strategy_node)
    graph.add_node("content", content_node)

    graph.set_entry_point("strategy")
    graph.add_edge("strategy", "content")
    graph.add_edge("content", END)

    return graph.compile()


campaign_graph = build_graph()
