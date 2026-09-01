from fastapi import APIRouter, Depends, Request

from core.security import get_current_user
from core.stats import client_ip_from_request, record_login

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/me")
async def read_current_user(request: Request, current_user: dict = Depends(get_current_user)):
    """Returns the caller's profile, creating it on their very first sign-in.

    The frontend calls this right after a successful Firebase login so it
    knows the caller's role before routing them anywhere. Each call is also
    logged as a login event (IP, user agent) for the admin dashboard.
    """
    record_login(
        uid=current_user["uid"],
        email=current_user.get("email"),
        ip=client_ip_from_request(request),
        user_agent=request.headers.get("User-Agent"),
    )
    return current_user