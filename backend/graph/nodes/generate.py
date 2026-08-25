from graph.state import GraphState
from config.models import getResponseFromLLM
from config.prompts import expert_prompt_v1,expert_prompt_v2


def generate_answer_node(state: GraphState):
    """ Generate a final answer for the query """
    context = state.get("context", "")
    query = state.get("query", "")
    category = state.get("category", "general_knowledge")

    if not context or category == "general_knowledge":
        expert_prompt = expert_prompt_v1
        user_msg = f"QUESTION: {query}"
    else:
        expert_prompt = expert_prompt_v2
        user_msg = f"CONTEXT: {context}\n\nQUESTION: {query}"
    
    response = getResponseFromLLM(
        system_prompt=expert_prompt, 
        user_prompt=user_msg, 
        model_temp=0.5, 
        format="text"
    )
    
    return {"answer": response.text}