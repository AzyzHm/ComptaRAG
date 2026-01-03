import json
from app.config.models import getResponseFromLLM
from app.graph.state import GraphState


ROUTER_SYSTEM_INSTRUCTION = """ 
You are an expert financial and legal intent classifier for a Retrieval-Augmented Generation (RAG) system. 
Your job is to categorize a user's query into exactly one of the following three categories.

### Categories:
1. "ifrs": 
   - Use this for questions regarding "International Financial Reporting Standards" (IAS/IFRS).
   - Keywords: IFRS, IAS, International accounting, consolidation (international context).

2. "tax_code":
   - Use this for questions regarding the **Tunisian** tax system.
   - Includes: Code de l'IRPP et de l'IS, TVA (VAT), fiscal procedures, registration duties, and local finance laws in Tunisia.
   - Any vague question about "tax" or "fisc" implies Tunisia unless stated otherwise.

3. "accounting_standards":
   - Use this for questions regarding **Tunisian** local accounting standards.
   - Includes: The "Système Comptable des Entreprises" (SCE), local chart of accounts (NCT / Normes Comptables Tunisiennes).

4. "web_search": REQUIRES live internet data.
   - Includes: Current exchange rates, 2025 news, specific recent Tunisian political events, or specific data from the current year.

5. "general_knowledge": The LLM can answer this immediately. 
   - Includes: Greetings, general definitions ("What is an asset?"), generic advice, or simple explanations of concepts.

### Output Format:
You must output ONLY a JSON object with a single key "category".
Example: {"category": "tax_code"}
"""

def route_query(user_query : str):
    """
    Routes the user query using Gemini Flash to decide which database to search.
    """
    try:
        response = getResponseFromLLM(ROUTER_SYSTEM_INSTRUCTION,user_query,0.0)
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