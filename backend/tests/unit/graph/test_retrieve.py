from graph.nodes.retrieve import retrieval_node, retrieve_context


def test_retrieve_context_joins_documents_with_blank_line(mocker):
    mocker.patch(
        "graph.nodes.retrieve.ollama.embed",
        return_value={"embeddings": [[0.1, 0.2, 0.3]]},
    )
    mock_collection = mocker.patch("graph.nodes.retrieve.collection")
    mock_collection.query.return_value = {"documents": [["Chunk one.", "Chunk two."]]}

    result = retrieve_context("What is IFRS 16?", "ifrs", n_results=5)

    assert result == "Chunk one.\n\nChunk two."


def test_retrieve_context_queries_with_category_filter_and_n_results(mocker):
    mocker.patch(
        "graph.nodes.retrieve.ollama.embed",
        return_value={"embeddings": [[0.1, 0.2, 0.3]]},
    )
    mock_collection = mocker.patch("graph.nodes.retrieve.collection")
    mock_collection.query.return_value = {"documents": [["chunk"]]}

    retrieve_context("query", "tax_code", n_results=3)

    _, kwargs = mock_collection.query.call_args
    assert kwargs["where"] == {"category": {"$eq": "tax_code"}}
    assert kwargs["n_results"] == 3
    assert kwargs["query_embeddings"] == [[0.1, 0.2, 0.3]]


def test_retrieve_context_uses_embeddinggemma_model(mocker):
    embed_spy = mocker.patch(
        "graph.nodes.retrieve.ollama.embed",
        return_value={"embeddings": [[0.1]]},
    )
    mocker.patch("graph.nodes.retrieve.collection").query.return_value = {
        "documents": [["chunk"]]
    }

    retrieve_context("some query", "ifrs")

    embed_spy.assert_called_once_with(model="embeddinggemma", input="some query")


def test_retrieve_context_returns_fallback_message_when_no_documents(mocker):
    mocker.patch(
        "graph.nodes.retrieve.ollama.embed",
        return_value={"embeddings": [[0.1, 0.2, 0.3]]},
    )
    mock_collection = mocker.patch("graph.nodes.retrieve.collection")
    mock_collection.query.return_value = {"documents": [[]]}

    assert retrieve_context("obscure query", "tax_code") == "No local documents found."


def test_retrieve_context_returns_fallback_message_when_documents_key_missing(mocker):
    mocker.patch(
        "graph.nodes.retrieve.ollama.embed",
        return_value={"embeddings": [[0.1, 0.2, 0.3]]},
    )
    mock_collection = mocker.patch("graph.nodes.retrieve.collection")
    mock_collection.query.return_value = {}

    assert retrieve_context("query", "ifrs") == "No local documents found."


def test_retrieval_node_wraps_context_in_state_dict(mocker):
    mocker.patch(
        "graph.nodes.retrieve.retrieve_context",
        return_value="Some retrieved context.",
    )
    state = {"query": "q", "category": "ifrs"}

    assert retrieval_node(state) == {"context": "Some retrieved context."}


def test_retrieval_node_passes_query_category_and_default_n_results(mocker):
    spy = mocker.patch("graph.nodes.retrieve.retrieve_context", return_value="context")
    state = {"query": "some question", "category": "tax_code"}

    retrieval_node(state)

    spy.assert_called_once_with("some question", "tax_code", 5)