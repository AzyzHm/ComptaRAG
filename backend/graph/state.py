from typing import TypedDict

class GraphState(TypedDict):
    query: str
    category: str
    context: str
    answer: str
    is_valid: bool