import pytest
from fastapi.testclient import TestClient

from tests.setup import mock_modules
from tests.setup.fakes import FakeChatGraph


@pytest.fixture()
def app():
    """
    Yields (TestClient, FakeChatGraph).

    Replaces the compiled LangGraph workflow (routes.chat.app) with a fake
    before the TestClient is built, so chat requests never touch a real
    ChromaDB collection, Ollama embedding call, or Gemini API call. Those
    are already stubbed at the module level by mock_modules, this replaces
    the graph's actual routing/retrieval/generation *logic* too, which is
    covered separately by tests/unit/test_graph_nodes.py.
    """
    import routes.chat as r_chat

    fake_graph = FakeChatGraph()
    original_app = r_chat.app
    r_chat.app = fake_graph

    from main import app as _app

    with TestClient(_app) as client:
        yield client, fake_graph

    r_chat.app = original_app
