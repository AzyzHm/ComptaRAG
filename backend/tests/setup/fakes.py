class FakeChatGraph:
    """
    Stand-in for the compiled LangGraph workflow (graph.workflow.app).
    Configure `.answer`, `.category`, or `.raise_exc` before making a
    request to control the outcome of POST /chat/.
    """

    def __init__(self, answer="Mocked AI reply", category="ifrs", raise_exc=None):
        self.answer = answer
        self.category = category
        self.raise_exc = raise_exc
        self.last_invoke_state = None

    def invoke(self, state):
        self.last_invoke_state = state
        if self.raise_exc:
            raise self.raise_exc
        result = {"answer": self.answer}
        if self.category is not None:
            result["category"] = self.category
        return result
