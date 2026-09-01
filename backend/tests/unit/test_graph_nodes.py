import json

import graph.nodes.generate as generate_mod
import graph.nodes.retrieve as retrieve_mod
import graph.nodes.router as router_mod
import graph.nodes.validate as validate_mod
import graph.nodes.web_search as web_search_mod
from config.prompts import expert_prompt_v1, expert_prompt_v2


def _base_state(**overrides):
    state = {
        "query": "What is IFRS 16?",
        "category": "ifrs",
        "context": "",
        "answer": "",
        "is_valid": False,
    }
    state.update(overrides)
    return state


class FakeResponse:
    def __init__(self, text, usage_metadata=None):
        self.text = text
        self.usage_metadata = usage_metadata


class FakeUsage:
    def __init__(self, prompt_token_count=0, candidates_token_count=0, total_token_count=0):
        self.prompt_token_count = prompt_token_count
        self.candidates_token_count = candidates_token_count
        self.total_token_count = total_token_count


_ZERO_USAGE = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


class TestRouterNode:
    def test_route_query_returns_category_from_llm(self, monkeypatch):
        monkeypatch.setattr(
            router_mod,
            "getResponseFromLLM",
            lambda *a, **kw: FakeResponse(json.dumps({"category": "ifrs"})),
        )
        assert router_mod.route_query("What is IFRS 16?") == "ifrs"

    def test_route_query_falls_back_on_empty_response(self, monkeypatch):
        monkeypatch.setattr(router_mod, "getResponseFromLLM", lambda *a, **kw: FakeResponse(None))
        assert router_mod.route_query("hello") == "general_knowledge"

    def test_route_query_falls_back_on_malformed_json(self, monkeypatch):
        monkeypatch.setattr(
            router_mod, "getResponseFromLLM", lambda *a, **kw: FakeResponse("not json")
        )
        assert router_mod.route_query("hello") == "general_knowledge"

    def test_route_query_falls_back_on_missing_category_key(self, monkeypatch):
        monkeypatch.setattr(
            router_mod,
            "getResponseFromLLM",
            lambda *a, **kw: FakeResponse(json.dumps({"unexpected": "value"})),
        )
        assert router_mod.route_query("hello") == "general_knowledge"

    def test_route_query_falls_back_on_llm_exception(self, monkeypatch):
        def _raise(*a, **kw):
            raise RuntimeError("LLM unavailable")

        monkeypatch.setattr(router_mod, "getResponseFromLLM", _raise)
        assert router_mod.route_query("hello") == "general_knowledge"

    def test_router_node_wraps_category_in_state_dict(self, monkeypatch):
        monkeypatch.setattr(router_mod, "route_query", lambda query: "tax_code")
        result = router_mod.router_node(_base_state(query="Comment est calcule l'IS en Tunisie ?"))
        assert result == {"category": "tax_code"}


class TestValidateNode:
    def test_skips_llm_for_general_knowledge(self, monkeypatch):
        called = {}

        def _fail_if_called(*a, **kw):
            called["yes"] = True

        monkeypatch.setattr(validate_mod, "getResponseFromLLM", _fail_if_called)
        result = validate_mod.validate_node(_base_state(category="general_knowledge"))
        assert result == {"is_valid": True}
        assert "yes" not in called

    def test_returns_true_for_valid_context(self, monkeypatch):
        monkeypatch.setattr(
            validate_mod,
            "getResponseFromLLM",
            lambda *a, **kw: FakeResponse(json.dumps({"is_valid": True})),
        )
        state = _base_state(context="IFRS 16 covers lease accounting.")
        assert validate_mod.validate_node(state) == {"is_valid": True}

    def test_returns_false_for_invalid_context(self, monkeypatch):
        monkeypatch.setattr(
            validate_mod,
            "getResponseFromLLM",
            lambda *a, **kw: FakeResponse(json.dumps({"is_valid": False})),
        )
        state = _base_state(context="unrelated text")
        assert validate_mod.validate_node(state) == {"is_valid": False}

    def test_defaults_to_false_on_malformed_json(self, monkeypatch):
        monkeypatch.setattr(
            validate_mod, "getResponseFromLLM", lambda *a, **kw: FakeResponse("not json")
        )
        assert validate_mod.validate_node(_base_state(context="c")) == {"is_valid": False}

    def test_defaults_to_false_on_empty_response(self, monkeypatch):
        monkeypatch.setattr(validate_mod, "getResponseFromLLM", lambda *a, **kw: FakeResponse(None))
        assert validate_mod.validate_node(_base_state(context="c")) == {"is_valid": False}

    def test_defaults_to_false_on_llm_exception(self, monkeypatch):
        def _raise(*a, **kw):
            raise RuntimeError("LLM unavailable")

        monkeypatch.setattr(validate_mod, "getResponseFromLLM", _raise)
        assert validate_mod.validate_node(_base_state(context="c")) == {"is_valid": False}


class TestGenerateNode:
    def test_uses_v1_prompt_for_general_knowledge(self, monkeypatch):
        captured = {}

        def _fake(**kwargs):
            captured.update(kwargs)
            return FakeResponse("A concise answer.")

        monkeypatch.setattr(generate_mod, "getResponseFromLLM", _fake)
        state = _base_state(query="What is an asset?", context="", category="general_knowledge")

        assert generate_mod.generate_answer_node(state) == {
            "answer": "A concise answer.",
            "token_usage": _ZERO_USAGE,
        }
        assert captured["system_prompt"] == expert_prompt_v1
        assert captured["user_prompt"] == "QUESTION: What is an asset?"

    def test_uses_v1_prompt_when_context_missing_even_for_ifrs(self, monkeypatch):
        captured = {}
        monkeypatch.setattr(
            generate_mod,
            "getResponseFromLLM",
            lambda **kw: captured.update(kw) or FakeResponse("answer"),
        )
        generate_mod.generate_answer_node(_base_state(context=""))
        assert captured["system_prompt"] == expert_prompt_v1

    def test_uses_v2_prompt_when_context_present(self, monkeypatch):
        captured = {}
        monkeypatch.setattr(
            generate_mod,
            "getResponseFromLLM",
            lambda **kw: captured.update(kw) or FakeResponse("A grounded answer."),
        )
        state = _base_state(
            query="What are the recognition criteria for a provision?",
            context="IAS 37 requires a present obligation from a past event.",
        )
        result = generate_mod.generate_answer_node(state)

        assert result == {"answer": "A grounded answer.", "token_usage": _ZERO_USAGE}
        assert captured["system_prompt"] == expert_prompt_v2
        assert (
            "CONTEXT: IAS 37 requires a present obligation from a past event."
            in (captured["user_prompt"])
        )
        assert (
            "QUESTION: What are the recognition criteria for a provision?"
            in (captured["user_prompt"])
        )

    def test_passes_expected_temperature_and_format(self, monkeypatch):
        captured = {}
        monkeypatch.setattr(
            generate_mod,
            "getResponseFromLLM",
            lambda **kw: captured.update(kw) or FakeResponse("answer"),
        )
        generate_mod.generate_answer_node(_base_state(context="c"))
        assert captured["model_temp"] == 0.5
        assert captured["format"] == "text"

    def test_defaults_category_to_general_knowledge_when_absent(self, monkeypatch):
        captured = {}
        monkeypatch.setattr(
            generate_mod,
            "getResponseFromLLM",
            lambda **kw: captured.update(kw) or FakeResponse("answer"),
        )
        state = {"query": "q", "context": "some context"}
        generate_mod.generate_answer_node(state)
        assert captured["system_prompt"] == expert_prompt_v1

    def test_includes_recent_history_in_the_prompt(self, monkeypatch):
        captured = {}
        monkeypatch.setattr(
            generate_mod,
            "getResponseFromLLM",
            lambda **kw: captured.update(kw) or FakeResponse("answer"),
        )
        state = _base_state(
            query="And what about the VAT rate?",
            context="",
            category="general_knowledge",
            history=[
                {"role": "user", "content": "What is the corporate tax rate?"},
                {"role": "assistant", "content": "It is 15% for most companies."},
            ],
        )

        generate_mod.generate_answer_node(state)

        assert "CONVERSATION SO FAR:" in captured["user_prompt"]
        assert "User: What is the corporate tax rate?" in captured["user_prompt"]
        assert "Assistant: It is 15% for most companies." in captured["user_prompt"]
        assert "QUESTION: And what about the VAT rate?" in captured["user_prompt"]

    def test_omits_history_block_when_history_is_empty(self, monkeypatch):
        captured = {}
        monkeypatch.setattr(
            generate_mod,
            "getResponseFromLLM",
            lambda **kw: captured.update(kw) or FakeResponse("answer"),
        )
        generate_mod.generate_answer_node(_base_state(context="", history=[]))
        assert "CONVERSATION SO FAR" not in captured["user_prompt"]

    def test_only_keeps_the_last_ten_history_turns(self, monkeypatch):
        captured = {}
        monkeypatch.setattr(
            generate_mod,
            "getResponseFromLLM",
            lambda **kw: captured.update(kw) or FakeResponse("answer"),
        )
        history = [{"role": "user", "content": f"turn {i}"} for i in range(15)]
        generate_mod.generate_answer_node(_base_state(context="", history=history))

        assert "turn 5" in captured["user_prompt"]
        assert "turn 14" in captured["user_prompt"]
        assert "turn 4" not in captured["user_prompt"]

    def test_extracts_token_usage_from_response_metadata(self, monkeypatch):
        usage = FakeUsage(prompt_token_count=10, candidates_token_count=20, total_token_count=30)
        monkeypatch.setattr(
            generate_mod,
            "getResponseFromLLM",
            lambda **kw: FakeResponse("answer", usage_metadata=usage),
        )
        result = generate_mod.generate_answer_node(_base_state(context="c"))

        assert result["token_usage"] == {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        }

    def test_defaults_token_usage_to_zero_when_metadata_missing(self, monkeypatch):
        monkeypatch.setattr(generate_mod, "getResponseFromLLM", lambda **kw: FakeResponse("answer"))
        result = generate_mod.generate_answer_node(_base_state(context="c"))
        assert result["token_usage"] == _ZERO_USAGE


class TestWebSearchNode:
    def test_returns_context_from_search_service(self, monkeypatch):
        monkeypatch.setattr(
            web_search_mod,
            "search_web",
            lambda query: "Source: example.com\nContent: EUR/TND rate today.",
        )
        result = web_search_mod.web_search_node(_base_state(query="current EUR/TND exchange rate"))
        assert result == {"context": "Source: example.com\nContent: EUR/TND rate today."}

    def test_passes_query_through_unchanged(self, monkeypatch):
        captured = {}
        monkeypatch.setattr(
            web_search_mod,
            "search_web",
            lambda query: captured.setdefault("query", query) and "",
        )
        web_search_mod.web_search_node(_base_state(query="some question"))
        assert captured["query"] == "some question"

    def test_ignores_other_state_fields(self, monkeypatch):
        monkeypatch.setattr(web_search_mod, "search_web", lambda query: "context text")
        state = _base_state(category="tax_code", answer="stale", is_valid=False)
        assert web_search_mod.web_search_node(state) == {"context": "context text"}


class TestRetrieveNode:
    def test_retrieve_context_joins_documents_with_blank_line(self, monkeypatch):
        monkeypatch.setattr(
            retrieve_mod.ollama, "embed", lambda **kw: {"embeddings": [[0.1, 0.2, 0.3]]}
        )

        class _Collection:
            def query(self, **kwargs):
                return {"documents": [["Chunk one.", "Chunk two."]]}

        monkeypatch.setattr(retrieve_mod, "collection", _Collection())
        result = retrieve_mod.retrieve_context("What is IFRS 16?", "ifrs", n_results=5)
        assert result == "Chunk one.\n\nChunk two."

    def test_queries_with_category_filter_and_n_results(self, monkeypatch):
        monkeypatch.setattr(
            retrieve_mod.ollama, "embed", lambda **kw: {"embeddings": [[0.1, 0.2, 0.3]]}
        )
        captured = {}

        class _Collection:
            def query(self, **kwargs):
                captured.update(kwargs)
                return {"documents": [["chunk"]]}

        monkeypatch.setattr(retrieve_mod, "collection", _Collection())
        retrieve_mod.retrieve_context("query", "tax_code", n_results=3)

        assert captured["where"] == {"category": {"$eq": "tax_code"}}
        assert captured["n_results"] == 3
        assert captured["query_embeddings"] == [[0.1, 0.2, 0.3]]

    def test_uses_embeddinggemma_model(self, monkeypatch):
        captured = {}

        def _fake_embed(**kwargs):
            captured.update(kwargs)
            return {"embeddings": [[0.1]]}

        monkeypatch.setattr(retrieve_mod.ollama, "embed", _fake_embed)

        class _Collection:
            def query(self, **kwargs):
                return {"documents": [["chunk"]]}

        monkeypatch.setattr(retrieve_mod, "collection", _Collection())
        retrieve_mod.retrieve_context("some query", "ifrs")

        assert captured == {"model": "embeddinggemma", "input": "some query"}

    def test_returns_fallback_message_when_no_documents(self, monkeypatch):
        monkeypatch.setattr(
            retrieve_mod.ollama, "embed", lambda **kw: {"embeddings": [[0.1, 0.2, 0.3]]}
        )

        class _Collection:
            def query(self, **kwargs):
                return {"documents": [[]]}

        monkeypatch.setattr(retrieve_mod, "collection", _Collection())
        assert (
            retrieve_mod.retrieve_context("obscure query", "tax_code")
            == "No local documents found."
        )

    def test_returns_fallback_message_when_documents_key_missing(self, monkeypatch):
        monkeypatch.setattr(
            retrieve_mod.ollama, "embed", lambda **kw: {"embeddings": [[0.1, 0.2, 0.3]]}
        )

        class _Collection:
            def query(self, **kwargs):
                return {}

        monkeypatch.setattr(retrieve_mod, "collection", _Collection())
        assert retrieve_mod.retrieve_context("query", "ifrs") == "No local documents found."

    def test_retrieval_node_wraps_context_in_state_dict(self, monkeypatch):
        monkeypatch.setattr(
            retrieve_mod, "retrieve_context", lambda q, c, n: "Some retrieved context."
        )
        result = retrieve_mod.retrieval_node(_base_state(query="q", category="ifrs"))
        assert result == {"context": "Some retrieved context."}

    def test_retrieval_node_passes_query_category_and_default_n_results(self, monkeypatch):
        captured = {}
        monkeypatch.setattr(
            retrieve_mod,
            "retrieve_context",
            lambda q, c, n: captured.update(query=q, category=c, n_results=n) or "context",
        )
        retrieve_mod.retrieval_node(_base_state(query="some question", category="tax_code"))
        assert captured == {"query": "some question", "category": "tax_code", "n_results": 5}
