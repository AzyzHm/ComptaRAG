from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from config.firebase import get_firestore_client
from core.security import USERS_COLLECTION, require_roles
from core.stats import list_recent_logins, list_usage_totals
from models.roles import Role

router = APIRouter(prefix="/admin", tags=["Admin"])


class RoleUpdateRequest(BaseModel):
    role: Role


@router.get("/users")
async def list_users(
    current_user: dict = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)),
):
    """Lists every account. Visible to ADMIN and SUPER_ADMIN."""
    db = get_firestore_client()
    docs = db.collection(USERS_COLLECTION).stream()
    return [{"uid": doc.id, **doc.to_dict()} for doc in docs]


@router.patch("/users/{uid}/role")
async def update_user_role(
    uid: str,
    body: RoleUpdateRequest,
    current_user: dict = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)),
):
    """Changes a user's role.

    SUPER_ADMIN can assign any role to anyone else. ADMIN can only move a
    user between USER and ADMIN, and cannot touch an account that is
    currently SUPER_ADMIN. Nobody can change their own role, to avoid
    accidentally locking themselves out.
    """
    if uid == current_user["uid"]:
        raise HTTPException(status_code=400, detail="You cannot change your own role")

    db = get_firestore_client()
    doc_ref = db.collection(USERS_COLLECTION).document(uid)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    target = doc.to_dict()
    is_super_admin = current_user["role"] == Role.SUPER_ADMIN.value

    if not is_super_admin:
        if target["role"] == Role.SUPER_ADMIN.value:
            raise HTTPException(
                status_code=403, detail="Only a SUPER_ADMIN can modify a SUPER_ADMIN account"
            )
        if body.role == Role.SUPER_ADMIN:
            raise HTTPException(
                status_code=403, detail="Only a SUPER_ADMIN can grant the SUPER_ADMIN role"
            )

    doc_ref.update({"role": body.role.value})
    return {"uid": uid, **target, "role": body.role.value}


@router.get("/stats/logins")
async def list_login_events(
    current_user: dict = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)),
):
    """Lists the most recent sign-ins across every account: who logged in,
    from what IP, and when. Visible to ADMIN and SUPER_ADMIN."""
    return list_recent_logins()


@router.get("/stats/usage")
async def list_token_usage(
    current_user: dict = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)),
):
    """Lists every user's running token usage total. Visible to ADMIN and
    SUPER_ADMIN."""
    return list_usage_totals()