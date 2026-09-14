import importlib
from types import SimpleNamespace

import core.rate_limit as rate_limit_mod


class TestRateLimitKey:
    def test_prefers_the_forwarded_for_first_hop(self):
        request = SimpleNamespace(
            headers={"X-Forwarded-For": "203.0.113.5, 10.0.0.1"},
            client=SimpleNamespace(host="10.0.0.1"),
        )
        assert rate_limit_mod.rate_limit_key(request) == "203.0.113.5"

    def test_falls_back_to_the_socket_peer(self):
        request = SimpleNamespace(headers={}, client=SimpleNamespace(host="10.0.0.1"))
        assert rate_limit_mod.rate_limit_key(request) == "10.0.0.1"

    def test_falls_back_to_get_remote_address_when_no_client_info_is_available(self, monkeypatch):
        request = SimpleNamespace(headers={}, client=None)
        monkeypatch.setattr(rate_limit_mod, "get_remote_address", lambda _req: "unknown")
        assert rate_limit_mod.rate_limit_key(request) == "unknown"


class TestRateLimitEnabledSetting:
    def test_enabled_by_default(self, monkeypatch):
        monkeypatch.delenv("RATE_LIMIT_ENABLED", raising=False)
        reloaded = importlib.reload(rate_limit_mod)
        assert reloaded.limiter.enabled is True

    def test_disabled_when_set_to_false(self, monkeypatch):
        monkeypatch.setenv("RATE_LIMIT_ENABLED", "false")
        reloaded = importlib.reload(rate_limit_mod)
        assert reloaded.limiter.enabled is False

    def test_disabled_value_is_case_insensitive(self, monkeypatch):
        monkeypatch.setenv("RATE_LIMIT_ENABLED", "FALSE")
        reloaded = importlib.reload(rate_limit_mod)
        assert reloaded.limiter.enabled is False

    def test_any_other_value_stays_enabled(self, monkeypatch):
        monkeypatch.setenv("RATE_LIMIT_ENABLED", "yes")
        reloaded = importlib.reload(rate_limit_mod)
        assert reloaded.limiter.enabled is True

    def teardown_method(self):
        import os

        os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
        os.environ["RATE_LIMIT_ENABLED"] = "false"
        importlib.reload(rate_limit_mod)
