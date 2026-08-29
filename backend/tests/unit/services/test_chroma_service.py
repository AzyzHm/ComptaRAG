import importlib

import services.chroma_service as chroma_service


def test_chroma_service_constructs_persistent_client_with_expected_path(mocker):
    mock_client_cls = mocker.patch("chromadb.PersistentClient")
    mock_client_cls.return_value.get_collection.return_value = mocker.sentinel.collection

    reloaded = importlib.reload(chroma_service)

    mock_client_cls.assert_called_once_with(path="knowledge_base/chroma_db")
    assert reloaded.collection is mocker.sentinel.collection


def test_chroma_service_fetches_expected_collection_name(mocker):
    mock_client_cls = mocker.patch("chromadb.PersistentClient")

    reloaded = importlib.reload(chroma_service)

    reloaded.client.get_collection.assert_called_once_with(name="ai_assistant")


def test_chroma_service_propagates_error_when_collection_missing(mocker):
    mock_client_cls = mocker.patch("chromadb.PersistentClient")
    mock_client_cls.return_value.get_collection.side_effect = ValueError(
        "Collection [ai_assistant] does not exist"
    )

    try:
        importlib.reload(chroma_service)
        assert False, "expected reload to raise"
    except ValueError as exc:
        assert "does not exist" in str(exc)