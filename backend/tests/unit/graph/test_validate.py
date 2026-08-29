import json

from graph.nodes.validate import validate_node


class FakeResponse:
    def __init__(self, text):
        self.text = text


def test_validate_node_skips_llm_for_general_knowledge(mocker):
    spy = mocker.patch("graph.nodes.validate.getResponseFromLLM")
    state = {"category": "general_knowledge", "query": "hi", "context": ""}

    assert validate_node(state) == {"is_valid": True}
    spy.assert_not_called()


def test_validate_node_returns_true_for_valid_context(mocker):
    mocker.patch(
        "graph.nodes.validate.getResponseFromLLM",
        return_value=FakeResponse(json.dumps({"is_valid": True})),
    )
    state = {
        "category": "ifrs",
        "query": "What is IFRS 16?",
        "context": "IFRS 16 covers lease accounting.",
    }
    assert validate_node(state) == {"is_valid": True}


def test_validate_node_returns_false_for_invalid_context(mocker):
    mocker.patch(
        "graph.nodes.validate.getResponseFromLLM",
        return_value=FakeResponse(json.dumps({"is_valid": False})),
    )
    state = {"category": "ifrs", "query": "What is IFRS 16?", "context": "unrelated text"}
    assert validate_node(state) == {"is_valid": False}


def test_validate_node_defaults_to_false_on_malformed_json(mocker):
    mocker.patch(
        "graph.nodes.validate.getResponseFromLLM",
        return_value=FakeResponse("not json"),
    )
    state = {"category": "ifrs", "query": "q", "context": "c"}
    assert validate_node(state) == {"is_valid": False}


def test_validate_node_defaults_to_false_on_empty_response(mocker):
    mocker.patch(
        "graph.nodes.validate.getResponseFromLLM",
        return_value=FakeResponse(None),
    )
    state = {"category": "ifrs", "query": "q", "context": "c"}
    assert validate_node(state) == {"is_valid": False}


def test_validate_node_defaults_to_false_on_llm_exception(mocker):
    mocker.patch(
        "graph.nodes.validate.getResponseFromLLM",
        side_effect=RuntimeError("LLM unavailable"),
    )
    state = {"category": "ifrs", "query": "q", "context": "c"}
    assert validate_node(state) == {"is_valid": False}