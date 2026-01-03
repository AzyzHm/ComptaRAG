from app.graph.state import GraphState
from app.config.models import getResponseFromLLM
import json

VALIDATOR_SYSTEM_INSTRUCTION = """
You are a "Context Judge". Your sole task is to determine if the provided CONTEXT contains enough relevant information to accurately answer the USER QUERY.

Rules:
1. If the context is relevant and provides an answer (even partially), return {"is_valid": true}.
2. If the context is completely unrelated, nonsensical, or states no information is found, return {"is_valid": false}.
3. Do NOT try to answer the query itself. Just judge the relationship between the query and the context.

Output ONLY JSON: {"is_valid": boolean}
"""

def validate_node(state: GraphState):
    # If it's general knowledge, we skip validation as there is no context to judge
    if state["category"] == "general_knowledge":
        return {"is_valid": True}

    user_input = f"USER QUERY: {state["query"]}\n\nRETRIEVED CONTEXT: {state["context"]}"
    
    try:
        response = getResponseFromLLM(VALIDATOR_SYSTEM_INSTRUCTION, user_input, 0.0)
        if response.text is None:
            raise ValueError("LLM Response is empty")
        result = json.loads(response.text)
        
        is_valid = result.get("is_valid", False)
        return {"is_valid": is_valid}
    except Exception as e:
        print(f"Validation Error: {e}")
        return {"is_valid": False}