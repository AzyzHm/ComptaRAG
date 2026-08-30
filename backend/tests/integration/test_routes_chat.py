class TestChatRoute:
    def test_returns_answer_and_category_on_success(self, app):
        client, fake_graph = app
        fake_graph.answer = "IFRS 16 requires lessees to recognize a right-of-use asset."
        fake_graph.category = "ifrs"

        response = client.post("/chat/", json={"query": "What is IFRS 16?"})

        assert response.status_code == 200
        assert response.json() == {
            "response": "IFRS 16 requires lessees to recognize a right-of-use asset.",
            "category": "ifrs",
        }

    def test_passes_query_into_initial_graph_state(self, app):
        client, fake_graph = app

        client.post("/chat/", json={"query": "Comment calculer la TVA ?"})

        assert fake_graph.last_invoke_state == {"query": "Comment calculer la TVA ?"}

    def test_returns_null_category_when_missing_from_graph_result(self, app):
        client, fake_graph = app
        fake_graph.category = None

        response = client.post("/chat/", json={"query": "q"})

        assert response.status_code == 200
        assert response.json()["category"] is None

    def test_returns_500_with_error_detail_when_graph_raises(self, app):
        client, fake_graph = app
        fake_graph.raise_exc = RuntimeError("LLM unavailable")

        response = client.post("/chat/", json={"query": "q"})

        assert response.status_code == 500
        assert response.json() == {"detail": "LLM unavailable"}

    def test_returns_422_when_query_field_missing(self, app):
        client, fake_graph = app

        response = client.post("/chat/", json={})

        assert response.status_code == 422
        assert fake_graph.last_invoke_state is None

    def test_returns_422_when_query_is_wrong_type(self, app):
        client, fake_graph = app

        response = client.post("/chat/", json={"query": 123})

        assert response.status_code == 422
        assert fake_graph.last_invoke_state is None

    def test_accepts_empty_string_query(self, app):
        client, fake_graph = app

        response = client.post("/chat/", json={"query": ""})

        assert response.status_code == 200
        assert fake_graph.last_invoke_state == {"query": ""}
