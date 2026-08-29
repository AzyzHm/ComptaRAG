from config.prompts import expert_prompt_v1, expert_prompt_v2
from graph.nodes.generate import generate_answer_node


class FakeResponse:
    def __init__(self, text):
        self.text = text


def test_generate_uses_v1_prompt_for_general_knowledge(mocker):
    spy = mocker.patch(
        "graph.nodes.generate.getResponseFromLLM",
        return_value=FakeResponse("A concise answer."),
    )
    state = {"query": "What is an asset?", "context": "", "category": "general_knowledge"}

    assert generate_answer_node(state) == {"answer": "A concise answer."}
    _, kwargs = spy.call_args
    assert kwargs["system_prompt"] == expert_prompt_v1
    assert kwargs["user_prompt"] == "QUESTION: What is an asset?"


def test_generate_uses_v1_prompt_when_context_missing_even_for_ifrs(mocker):
    spy = mocker.patch(
        "graph.nodes.generate.getResponseFromLLM",
        return_value=FakeResponse("answer"),
    )
    state = {"query": "q", "context": "", "category": "ifrs"}
    generate_answer_node(state)

    _, kwargs = spy.call_args
    assert kwargs["system_prompt"] == expert_prompt_v1


def test_generate_uses_v2_prompt_when_context_present(mocker):
    spy = mocker.patch(
        "graph.nodes.generate.getResponseFromLLM",
        return_value=FakeResponse("A grounded answer."),
    )
    state = {
        "query": "What are the recognition criteria for a provision?",
        "context": "IAS 37 requires a present obligation from a past event.",
        "category": "ifrs",
    }
    result = generate_answer_node(state)

    assert result == {"answer": "A grounded answer."}
    _, kwargs = spy.call_args
    assert kwargs["system_prompt"] == expert_prompt_v2
    assert "CONTEXT: IAS 37 requires a present obligation from a past event." in kwargs["user_prompt"]
    assert "QUESTION: What are the recognition criteria for a provision?" in kwargs["user_prompt"]


def test_generate_passes_expected_temperature_and_format(mocker):
    spy = mocker.patch(
        "graph.nodes.generate.getResponseFromLLM",
        return_value=FakeResponse("answer"),
    )
    state = {"query": "q", "context": "c", "category": "ifrs"}
    generate_answer_node(state)

    _, kwargs = spy.call_args
    assert kwargs["model_temp"] == 0.5
    assert kwargs["format"] == "text"


def test_generate_defaults_category_to_general_knowledge_when_absent(mocker):
    spy = mocker.patch(
        "graph.nodes.generate.getResponseFromLLM",
        return_value=FakeResponse("answer"),
    )
    state = {"query": "q", "context": "some context"}
    generate_answer_node(state)

    _, kwargs = spy.call_args
    assert kwargs["system_prompt"] == expert_prompt_v1