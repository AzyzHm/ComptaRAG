import importlib
from unittest.mock import MagicMock

import chromadb

import services.chroma_service as chroma_service_mod


class TestChromaService:
    def test_constructs_persistent_client_with_expected_path(self, monkeypatch):
        mock_client_cls = MagicMock()
        mock_client_cls.return_value.get_or_create_collection.return_value = (
            "the-collection"
        )
        monkeypatch.setattr(chromadb, "PersistentClient", mock_client_cls)

        reloaded = importlib.reload(chroma_service_mod)

        mock_client_cls.assert_called_once_with(path="knowledge_base/chroma_db")
        assert reloaded.collection == "the-collection"

    def test_gets_or_creates_expected_collection(self, monkeypatch):
        mock_client_cls = MagicMock()
        monkeypatch.setattr(chromadb, "PersistentClient", mock_client_cls)

        reloaded = importlib.reload(chroma_service_mod)

        reloaded.client.get_or_create_collection.assert_called_once_with(
            name="ai_assistant",
            metadata={"hnsw:space": "cosine"},
        )

    def test_collection_is_created_when_missing(self, monkeypatch):
        mock_client_cls = MagicMock()
        mock_client_cls.return_value.get_or_create_collection.return_value = (
            "new-collection"
        )
        monkeypatch.setattr(chromadb, "PersistentClient", mock_client_cls)

        reloaded = importlib.reload(chroma_service_mod)

        assert reloaded.collection == "new-collection"
        reloaded.client.get_or_create_collection.assert_called_once_with(
            name="ai_assistant",
            metadata={"hnsw:space": "cosine"},
        )