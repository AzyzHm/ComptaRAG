from app.services.search_service import search_web
from app.graph.state import GraphState

def web_search_node(state: GraphState):
    context = search_web(state["query"])
    return {"context": context}