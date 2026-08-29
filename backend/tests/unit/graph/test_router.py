import json

from graph.nodes.router import route_query, router_node


class FakeResponse:
    def __init__(self, text):
        self.text = text


def test_route_query_returns_category_from_llm(mocker):
    mocker.patch(
        "graph.nodes.router.getResponseFromLLM",
        return_value=FakeResponse(json.dumps({"category": "ifrs"})),
    )
    assert route_query("What is IFRS 16?") == "ifrs"


def test_route_query_falls_back_on_empty_response(mocker):
    mocker.patch(
        "graph.nodes.router.getResponseFromLLM",
        return_value=FakeResponse(None),
    )
    assert route_query("hello") == "general_knowledge"


def test_route_query_falls_back_on_malformed_json(mocker):
    mocker.patch(
        "graph.nodes.router.getResponseFromLLM",
        return_value=FakeResponse("not json"),
    )
    assert route_query("hello") == "general_knowledge"


def test_route_query_falls_back_on_missing_category_key(mocker):
    mocker.patch(
        "graph.nodes.router.getResponseFromLLM",
        return_value=FakeResponse(json.dumps({"unexpected": "value"})),
    )
    assert route_query("hello") == "general_knowledge"


def test_route_query_falls_back_on_llm_exception(mocker):
    mocker.patch(
        "graph.nodes.router.getResponseFromLLM",
        side_effect=RuntimeError("LLM unavailable"),
    )
    assert route_query("hello") == "general_knowledge"


def test_router_node_wraps_category_in_state_dict(mocker):
    mocker.patch("graph.nodes.router.route_query", return_value="tax_code")
    state = {"query": "Comment est calcule l'IS en Tunisie ?"}
    assert router_node(state) == {"category": "tax_code"}