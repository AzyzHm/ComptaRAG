from fastapi import Depends, HTTPException, Request
from firebase_admin import auth as firebase_auth
from google.cloud.firestore_v1 import SERVER_TIMESTAMP

from config.firebase import get_firestore_client
from models.roles import Role

USERS_COLLECTION = "users"


def _extract_bearer_token(request: Request) -> str:
    header = request.headers.get("Authorization")
    if not header or not header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    return header.removeprefix("Bearer ").strip()


def _get_or_create_profile(decoded_token: dict) -> dict:
    """Fetches the Firestore profile for this uid, creating it on first sign-in.

    The very first account ever created becomes SUPER_ADMIN so there is
    always at least one admin able to promote everyone else. Every
    subsequent account defaults to USER.
    """
    db = get_firestore_client()
    uid = decoded_token["uid"]
    doc_ref = db.collection(USERS_COLLECTION).document(uid)
    doc = doc_ref.get()

    if doc.exists:
        return {"uid": uid, **doc.to_dict()}

    is_first_user = len(list(db.collection(USERS_COLLECTION).limit(1).stream())) == 0
    profile = {
        "email": decoded_token.get("email"),
        "display_name": decoded_token.get("name"),
        "role": Role.SUPER_ADMIN.value if is_first_user else Role.USER.value,
        "created_at": SERVER_TIMESTAMP,
    }
    doc_ref.set(profile)
    return {"uid": uid, **profile}


def get_current_user(request: Request) -> dict:
    """Verifies the Firebase ID token on the request and returns the caller's
    Firestore profile (uid, email, display_name, role). Raises 401 if the
    token is missing, malformed, expired, or revoked.
    """
    token = _extract_bearer_token(request)
    try:
        decoded_token = firebase_auth.verify_id_token(token)
    except (
        firebase_auth.InvalidIdTokenError,
        firebase_auth.ExpiredIdTokenError,
        firebase_auth.RevokedIdTokenError,
        ValueError,
    ) as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

    return _get_or_create_profile(decoded_token)


def require_roles(*roles: Role):
    """FastAPI dependency factory, raises 403 unless the caller's role is
    one of `roles`. Use as `Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN))`.
    """
    allowed = {role.value for role in roles}

    def _dependency(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in allowed:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return current_user

    return _dependency
