import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from core.rate_limit import rate_limit_key


@pytest.fixture()
def limited_client():
    """
    A throwaway FastAPI app with its own `Limiter`, using the same key
    function as production (`core.rate_limit.rate_limit_key`) and the same
    middleware/exception-handler wiring as `main.py`, with one route capped
    at 2/minute. This exercises the real slowapi wiring end to end (429s,
    per-IP buckets, response shape) without touching a real route.

    A fresh Limiter is built per test rather than reusing the shared
    `core.rate_limit.limiter`: slowapi accumulates a registration every time
    `@limiter.limit(...)` decorates a route, and those registrations are not
    cleared by `limiter.reset()` (which only clears the hit counters), so
    reusing one Limiter across several throwaway "/probe" routes would
    double- and triple-count hits across tests. The rest of the suite never
    hits this, since it decorates each real route exactly once, at import
    time.
    """
    limiter = Limiter(key_func=rate_limit_key, enabled=True)

    app = FastAPI()
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    @app.get("/probe")
    @limiter.limit("2/minute")
    async def probe(request: Request):
        return {"ok": True}

    with TestClient(app) as client:
        yield client


class TestLimiterEndToEnd:
    def test_allows_requests_within_the_limit(self, limited_client):
        assert limited_client.get("/probe").status_code == 200
        assert limited_client.get("/probe").status_code == 200

    def test_blocks_the_request_that_exceeds_the_limit(self, limited_client):
        limited_client.get("/probe")
        limited_client.get("/probe")
        response = limited_client.get("/probe")
        assert response.status_code == 429

    def test_exceeded_response_names_the_limit(self, limited_client):
        limited_client.get("/probe")
        limited_client.get("/probe")
        response = limited_client.get("/probe")
        assert "2 per 1 minute" in response.json()["error"]

    def test_exceeded_response_still_returns_normal_json_shape(self, limited_client):
        limited_client.get("/probe")
        limited_client.get("/probe")
        response = limited_client.get("/probe")
        assert response.headers["content-type"].startswith("application/json")
        assert set(response.json().keys()) == {"error"}

    def test_different_caller_ips_get_independent_buckets(self, limited_client):
        headers_a = {"X-Forwarded-For": "203.0.113.1"}
        limited_client.get("/probe", headers=headers_a)
        limited_client.get("/probe", headers=headers_a)
        blocked = limited_client.get("/probe", headers=headers_a)
        assert blocked.status_code == 429

        headers_b = {"X-Forwarded-For": "203.0.113.2"}
        allowed = limited_client.get("/probe", headers=headers_b)
        assert allowed.status_code == 200


class TestLimiterDisabledByDefaultInTests:
    def test_real_app_ignores_the_limit_when_disabled(self, app):
        """The shared fixture in tests/conftest.py builds the real `main.app`
        with no overrides, so this locks in that RATE_LIMIT_ENABLED=false
        (set for the whole suite in tests/setup/mock_modules.py) actually
        takes effect: firing well past every configured limit on a real
        route never trips a 429."""
        client, _fake_graph, fake_db = app
        fake_db.collection("chats").document("c1").set(
            {"owner_uid": "test-uid", "title": "Untitled chat", "updated_at": 1}
        )

        statuses = {client.get("/chats/c1").status_code for _ in range(25)}

        assert statuses == {200}
