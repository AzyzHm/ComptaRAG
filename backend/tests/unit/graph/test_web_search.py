from graph.nodes.web_search import web_search_node


def test_web_search_node_returns_context_from_search_service(mocker):
    mocker.patch(
        "graph.nodes.web_search.search_web",
        return_value="Source: example.com\nContent: EUR/TND rate today.",
    )
    state = {"query": "current EUR/TND exchange rate"}

    assert web_search_node(state) == {
        "context": "Source: example.com\nContent: EUR/TND rate today."
    }


def test_web_search_node_passes_query_through_unchanged(mocker):
    spy = mocker.patch("graph.nodes.web_search.search_web", return_value="")
    state = {"query": "some question"}
    web_search_node(state)
    spy.assert_called_once_with("some question")


def test_web_search_node_ignores_other_state_fields(mocker):
    mocker.patch("graph.nodes.web_search.search_web", return_value="context text")
    state = {"query": "q", "category": "tax_code", "answer": "stale", "is_valid": False}

    assert web_search_node(state) == {"context": "context text"}