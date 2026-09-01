from google.cloud.firestore_v1 import SERVER_TIMESTAMP, Increment

from config.firebase import get_firestore_client

LOGIN_EVENTS_COLLECTION = "login_events"
USAGE_TOTALS_COLLECTION = "usage_totals"
USERS_COLLECTION = "users"
RECENT_LOGINS_LIMIT = 200


def client_ip_from_request(request) -> str | None:
    """Best-effort caller IP: the first hop in X-Forwarded-For when the app
    is behind a proxy or load balancer, otherwise the direct socket peer."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


def record_login(uid: str, email: str | None, ip: str | None, user_agent: str | None) -> None:
    """Appends a login event and stamps the user's profile with their most
    recent sign-in, so the admin dashboard can show "who logged in, from
    what IP" without scanning every event for a quick per-user summary."""
    db = get_firestore_client()
    db.collection(LOGIN_EVENTS_COLLECTION).document().set(
        {
            "uid": uid,
            "email": email,
            "ip": ip,
            "user_agent": user_agent,
            "created_at": SERVER_TIMESTAMP,
        }
    )
    db.collection(USERS_COLLECTION).document(uid).update(
        {"last_login_at": SERVER_TIMESTAMP, "last_login_ip": ip}
    )


def list_recent_logins(limit: int = RECENT_LOGINS_LIMIT) -> list[dict]:
    """Returns the most recent login events, newest first."""
    db = get_firestore_client()
    query = (
        db.collection(LOGIN_EVENTS_COLLECTION)
        .order_by("created_at", direction="DESCENDING")
        .limit(limit)
    )
    return [{"id": doc.id, **doc.to_dict()} for doc in query.stream()]


def record_usage(uid: str, token_usage: dict) -> None:
    """Rolls one reply's token cost into a per-user running total, so the
    admin dashboard can read one small doc per user instead of summing every
    message they have ever sent."""
    db = get_firestore_client()
    db.collection(USAGE_TOTALS_COLLECTION).document(uid).set(
        {
            "prompt_tokens": Increment(token_usage.get("prompt_tokens", 0)),
            "completion_tokens": Increment(token_usage.get("completion_tokens", 0)),
            "total_tokens": Increment(token_usage.get("total_tokens", 0)),
            "message_count": Increment(1),
            "updated_at": SERVER_TIMESTAMP,
        },
        merge=True,
    )


def list_usage_totals() -> list[dict]:
    """Returns every user's running token usage total."""
    db = get_firestore_client()
    return [
        {"uid": doc.id, **doc.to_dict()} for doc in db.collection(USAGE_TOTALS_COLLECTION).stream()
    ]
