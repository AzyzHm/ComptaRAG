from typing import TypedDict


class HistoryTurn(TypedDict):
    role: str
    content: str


class TokenUsage(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class GraphState(TypedDict):
    query: str
    history: list[HistoryTurn]
    category: str
    context: str
    answer: str
    is_valid: bool
    token_usage: TokenUsage
