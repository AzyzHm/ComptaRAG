import pytest
from fastapi.testclient import TestClient

from tests.setup import mock_modules
from tests.setup.fakes import FakeChatGraph

DEFAULT_TEST_USER = {
    "uid": "test-uid",
    "email": "test@example.com",
    "display_name": "Test User",
    "role": "USER",
}


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

    Also overrides the get_current_user auth dependency with a fixed USER
    profile, so tests that only care about chat behavior don't need to
    send a real Firebase ID token. Auth/role behavior itself is covered
    separately by tests/unit/test_core_security.py and
    tests/integration/test_routes_admin.py.
    """
    import routes.chat as r_chat
    from core.security import get_current_user

    fake_graph = FakeChatGraph()
    original_app = r_chat.app
    r_chat.app = fake_graph

    from main import app as _app

    _app.dependency_overrides[get_current_user] = lambda: DEFAULT_TEST_USER

    with TestClient(_app) as client:
        yield client, fake_graph

    r_chat.app = original_app
    _app.dependency_overrides.pop(get_current_user, None)
