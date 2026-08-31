from fastapi import APIRouter, Depends

from core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/me")
async def read_current_user(current_user: dict = Depends(get_current_user)):
    """Returns the caller's profile, creating it on their very first sign-in.

    The frontend calls this right after a successful Firebase login so it
    knows the caller's role before routing them anywhere.
    """
    return current_user
