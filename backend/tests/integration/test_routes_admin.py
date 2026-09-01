import pytest
from fastapi.testclient import TestClient

from core.security import get_current_user
from tests.setup.fakes import FakeFirestore


@pytest.fixture()
def admin_client(monkeypatch):
    """
    Yields a factory `make_client(current_user, users)` returning a TestClient
    with get_current_user overridden to `current_user` and routes.admin (plus
    core.stats, used by the stats endpoints) backed by a fresh FakeFirestore
    seeded with `users`.
    """
    import routes.admin as r_admin
    from core import stats as core_stats
    from main import app as _app

    def make_client(current_user, users):
        fake_db = FakeFirestore(users=users)
        monkeypatch.setattr(r_admin, "get_firestore_client", lambda: fake_db)
        monkeypatch.setattr(core_stats, "get_firestore_client", lambda: fake_db)
        _app.dependency_overrides[get_current_user] = lambda: current_user
        return TestClient(_app), fake_db

    yield make_client

    _app.dependency_overrides.pop(get_current_user, None)


class TestListUsers:
    def test_admin_can_list_users(self, admin_client):
        client, _fake_db = admin_client(
            current_user={"uid": "admin-1", "role": "ADMIN"},
            users={"u1": {"email": "a@a.com", "role": "USER"}},
        )

        response = client.get("/admin/users")

        assert response.status_code == 200
        assert response.json() == [{"uid": "u1", "email": "a@a.com", "role": "USER"}]

    def test_plain_user_cannot_list_users(self, admin_client):
        client, _fake_db = admin_client(current_user={"uid": "u1", "role": "USER"}, users={})

        response = client.get("/admin/users")

        assert response.status_code == 403


class TestUpdateUserRole:
    def test_super_admin_can_grant_admin_role(self, admin_client):
        client, _fake_db = admin_client(
            current_user={"uid": "super-1", "role": "SUPER_ADMIN"},
            users={"target": {"email": "t@t.com", "role": "USER"}},
        )

        response = client.patch("/admin/users/target/role", json={"role": "ADMIN"})

        assert response.status_code == 200
        assert response.json()["role"] == "ADMIN"

    def test_admin_cannot_grant_super_admin_role(self, admin_client):
        client, _fake_db = admin_client(
            current_user={"uid": "admin-1", "role": "ADMIN"},
            users={"target": {"email": "t@t.com", "role": "USER"}},
        )

        response = client.patch("/admin/users/target/role", json={"role": "SUPER_ADMIN"})

        assert response.status_code == 403

    def test_admin_cannot_modify_a_super_admin_account(self, admin_client):
        client, _fake_db = admin_client(
            current_user={"uid": "admin-1", "role": "ADMIN"},
            users={"target": {"email": "t@t.com", "role": "SUPER_ADMIN"}},
        )

        response = client.patch("/admin/users/target/role", json={"role": "USER"})

        assert response.status_code == 403

    def test_cannot_change_own_role(self, admin_client):
        client, _fake_db = admin_client(
            current_user={"uid": "admin-1", "role": "ADMIN"},
            users={"admin-1": {"email": "a@a.com", "role": "ADMIN"}},
        )

        response = client.patch("/admin/users/admin-1/role", json={"role": "USER"})

        assert response.status_code == 400

    def test_returns_404_for_unknown_user(self, admin_client):
        client, _fake_db = admin_client(
            current_user={"uid": "super-1", "role": "SUPER_ADMIN"}, users={}
        )

        response = client.patch("/admin/users/ghost/role", json={"role": "USER"})

        assert response.status_code == 404


class TestLoginStats:
    def test_admin_can_list_recent_logins_newest_first(self, admin_client):
        client, fake_db = admin_client(current_user={"uid": "admin-1", "role": "ADMIN"}, users={})
        fake_db.collection("login_events").document("e1").set(
            {"uid": "u1", "email": "a@a.com", "ip": "1.1.1.1", "created_at": 1}
        )
        fake_db.collection("login_events").document("e2").set(
            {"uid": "u2", "email": "b@b.com", "ip": "2.2.2.2", "created_at": 2}
        )

        response = client.get("/admin/stats/logins")

        assert response.status_code == 200
        emails = [event["email"] for event in response.json()]
        assert emails == ["b@b.com", "a@a.com"]

    def test_plain_user_cannot_view_login_stats(self, admin_client):
        client, _fake_db = admin_client(current_user={"uid": "u1", "role": "USER"}, users={})

        response = client.get("/admin/stats/logins")

        assert response.status_code == 403


class TestUsageStats:
    def test_admin_can_list_usage_totals(self, admin_client):
        client, fake_db = admin_client(current_user={"uid": "admin-1", "role": "ADMIN"}, users={})
        fake_db.collection("usage_totals").document("u1").set(
            {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15, "message_count": 1}
        )

        response = client.get("/admin/stats/usage")

        assert response.status_code == 200
        assert response.json() == [
            {
                "uid": "u1",
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
                "message_count": 1,
            }
        ]

    def test_plain_user_cannot_view_usage_stats(self, admin_client):
        client, _fake_db = admin_client(current_user={"uid": "u1", "role": "USER"}, users={})

        response = client.get("/admin/stats/usage")

        assert response.status_code == 403
