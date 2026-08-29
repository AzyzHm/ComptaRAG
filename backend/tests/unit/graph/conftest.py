from unittest.mock import MagicMock, patch

_patcher = patch("chromadb.PersistentClient")
_mock_client_cls = _patcher.start()
_mock_client_cls.return_value.get_collection.return_value = MagicMock()