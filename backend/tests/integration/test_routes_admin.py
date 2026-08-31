import pytest
from fastapi.testclient import TestClient

from core.security import get_current_user
from tests.setup.fakes import FakeFirestore


@pytest.fixture()
def admin_client(monkeypatch):
    """
    Yields a factory `make_client(current_user, users)` returning a TestClient
    with get_current_user overridden to `current_user` and routes.admin backed
    by a fresh FakeFirestore seeded with `users`.
    """
    import routes.admin as r_admin
    from main import app as _app

    def make_client(current_user, users):
        fake_db = FakeFirestore(users=users)
        monkeypatch.setattr(r_admin, "get_firestore_client", lambda: fake_db)
        _app.dependency_overrides[get_current_user] = lambda: current_user
        return TestClient(_app)

    yield make_client

    _app.dependency_overrides.pop(get_current_user, None)


class TestListUsers:
    def test_admin_can_list_users(self, admin_client):
        client = admin_client(
            current_user={"uid": "admin-1", "role": "ADMIN"},
            users={"u1": {"email": "a@a.com", "role": "USER"}},
        )

        response = client.get("/admin/users")

        assert response.status_code == 200
        assert response.json() == [{"uid": "u1", "email": "a@a.com", "role": "USER"}]

    def test_plain_user_cannot_list_users(self, admin_client):
        client = admin_client(current_user={"uid": "u1", "role": "USER"}, users={})

        response = client.get("/admin/users")

        assert response.status_code == 403


class TestUpdateUserRole:
    def test_super_admin_can_grant_admin_role(self, admin_client):
        client = admin_client(
            current_user={"uid": "super-1", "role": "SUPER_ADMIN"},
            users={"target": {"email": "t@t.com", "role": "USER"}},
        )

        response = client.patch("/admin/users/target/role", json={"role": "ADMIN"})

        assert response.status_code == 200
        assert response.json()["role"] == "ADMIN"

    def test_admin_cannot_grant_super_admin_role(self, admin_client):
        client = admin_client(
            current_user={"uid": "admin-1", "role": "ADMIN"},
            users={"target": {"email": "t@t.com", "role": "USER"}},
        )

        response = client.patch("/admin/users/target/role", json={"role": "SUPER_ADMIN"})

        assert response.status_code == 403

    def test_admin_cannot_modify_a_super_admin_account(self, admin_client):
        client = admin_client(
            current_user={"uid": "admin-1", "role": "ADMIN"},
            users={"target": {"email": "t@t.com", "role": "SUPER_ADMIN"}},
        )

        response = client.patch("/admin/users/target/role", json={"role": "USER"})

        assert response.status_code == 403

    def test_cannot_change_own_role(self, admin_client):
        client = admin_client(
            current_user={"uid": "admin-1", "role": "ADMIN"},
            users={"admin-1": {"email": "a@a.com", "role": "ADMIN"}},
        )

        response = client.patch("/admin/users/admin-1/role", json={"role": "USER"})

        assert response.status_code == 400

    def test_returns_404_for_unknown_user(self, admin_client):
        client = admin_client(current_user={"uid": "super-1", "role": "SUPER_ADMIN"}, users={})

        response = client.patch("/admin/users/ghost/role", json={"role": "USER"})

        assert response.status_code == 404
