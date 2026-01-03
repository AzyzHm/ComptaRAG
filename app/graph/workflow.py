from langgraph.graph import StateGraph, END

from app.graph.state import GraphState
from app.graph.nodes.router import router_node
from app.graph.nodes.retrieve import retrieval_node
from app.graph.nodes.web_search import web_search_node
from app.graph.nodes.validate import validate_node
from app.graph.nodes.generate import generate_answer_node

from app.config.models import warm_up_embedding_model


def decide_next_node(state: GraphState):
    if state["category"] == "web_search":
        return "web_search"
    elif state["category"] == "general_knowledge":
        return "generate"
    else:
        return "retrieve"

def post_val_routing(state: GraphState):
    """
    Determines if we go to generation or try a web search fallback.
    """
    if state["is_valid"]:
        return "generate"
    else:
        return "web_search"


workflow = StateGraph(GraphState)

workflow.add_node("router", router_node)
workflow.add_node("retrieve", retrieval_node)
workflow.add_node("validate", validate_node) # New Node
workflow.add_node("web_search", web_search_node)
workflow.add_node("generate", generate_answer_node)

workflow.set_entry_point("router")

# 1. Router -> Local or Web or Direct
workflow.add_conditional_edges(
    "router",
    decide_next_node,
    {
        "web_search": "web_search",
        "generate": "generate",
        "retrieve": "retrieve"
    }
)

# 2. Retrieve -> Validate
workflow.add_edge("retrieve", "validate")

# 3. Validate -> Generate (if True) OR Web Search (if False)
workflow.add_conditional_edges(
    "validate",
    post_val_routing,
    {
        "generate": "generate",
        "web_search": "web_search"
    }
)

workflow.add_edge("web_search", "generate")
workflow.add_edge("generate", END)

app = workflow.compile()

if __name__ == "__main__":
    warm_up_embedding_model()
    test_input = {"query": "Under IFRS, what criteria must be met for an asset to be recognized on the statement of financial position?"}

    try:
        final_state = app.invoke(test_input) # type: ignore
        print("Answer:", final_state["answer"])
    except Exception as e:
        print(f"Execution Error: {e}")