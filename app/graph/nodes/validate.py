from app.graph.state import GraphState
from app.config.models import getResponseFromLLM
from app.config.prompts import validator_prompt
import json

def validate_node(state: GraphState):
    if state["category"] == "general_knowledge":
        return {"is_valid": True}

    user_input = f"USER QUERY: {state["query"]}\n\nRETRIEVED CONTEXT: {state["context"]}"
    
    try:
        response = getResponseFromLLM(validator_prompt, user_input, 0.0)
        if response.text is None:
            raise ValueError("LLM Response is empty")
        result = json.loads(response.text)
        
        is_valid = result.get("is_valid", False)
        return {"is_valid": is_valid}
    except Exception as e:
        print(f"Validation Error: {e}")
        return {"is_valid": False}