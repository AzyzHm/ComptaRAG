from backend.services.search_service import search_web
from backend.graph.state import GraphState

def web_search_node(state: GraphState):
    """ uses the web search service """
    context = search_web(state["query"])
    return {"context": context}