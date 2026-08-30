from graph.state import GraphState
from services.search_service import search_web


def web_search_node(state: GraphState):
    """uses the web search service"""
    context = search_web(state["query"])
    return {"context": context}
