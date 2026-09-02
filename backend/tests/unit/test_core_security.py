from core.security import update_profile_fields
from tests.setup.fakes import FakeFirestore


class TestUpdateProfileFields:
    def test_updates_display_name_only(self, monkeypatch):
        import core.security as core_security

        fake_db = FakeFirestore(users={"u1": {"email": "a@a.com", "display_name": "Old Name"}})
        monkeypatch.setattr(core_security, "get_firestore_client", lambda: fake_db)

        result = update_profile_fields("u1", display_name="New Name")

        assert result["display_name"] == "New Name"
        assert result["email"] == "a@a.com"

    def test_updates_email_only(self, monkeypatch):
        import core.security as core_security

        fake_db = FakeFirestore(users={"u1": {"email": "old@a.com", "display_name": "Name"}})
        monkeypatch.setattr(core_security, "get_firestore_client", lambda: fake_db)

        result = update_profile_fields("u1", email="new@a.com")

        assert result["email"] == "new@a.com"
        assert result["display_name"] == "Name"

    def test_updates_both_fields_together(self, monkeypatch):
        import core.security as core_security

        fake_db = FakeFirestore(users={"u1": {"email": "old@a.com", "display_name": "Old"}})
        monkeypatch.setattr(core_security, "get_firestore_client", lambda: fake_db)

        result = update_profile_fields("u1", display_name="New", email="new@a.com")

        assert result["display_name"] == "New"
        assert result["email"] == "new@a.com"

    def test_leaves_other_fields_untouched(self, monkeypatch):
        import core.security as core_security

        fake_db = FakeFirestore(users={"u1": {"email": "a@a.com", "role": "ADMIN"}})
        monkeypatch.setattr(core_security, "get_firestore_client", lambda: fake_db)

        result = update_profile_fields("u1", display_name="New Name")

        assert result["role"] == "ADMIN"

    def test_no_fields_given_is_a_no_op_read(self, monkeypatch):
        import core.security as core_security

        fake_db = FakeFirestore(users={"u1": {"email": "a@a.com", "display_name": "Name"}})
        monkeypatch.setattr(core_security, "get_firestore_client", lambda: fake_db)

        result = update_profile_fields("u1")

        assert result == {"uid": "u1", "email": "a@a.com", "display_name": "Name"}
