import json
from config.models import getResponseFromLLM
from graph.state import GraphState
from config.prompts import router_prompt

def route_query(user_query : str) -> str:
    """
    Routes the user query using an LLM to decide which database to search.
    """
    try:
        response = getResponseFromLLM(router_prompt,user_query,0.0)
        if response.text is None:
            raise ValueError("LLM response is empty")
        
        result = json.loads(response.text)
        return result.get("category", "general_knowledge")

    except Exception as e:
        print(f"Router Error: {e}")
        return "general_knowledge"

def router_node(state: GraphState):
    user_query = state["query"] 
    category = route_query(user_query)
    return {"category": category}