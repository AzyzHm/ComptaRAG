from typing import TypedDict

class GraphState(TypedDict):
    query: str           # The initial user input
    category: str        # From the Router (ifrs, tax_code, etc.)
    context: str         # The retrieved text from ChromaDB or Tavily
    answer: str          # The final generated response
    is_valid: bool       # From the Validator node