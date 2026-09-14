import os

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from services.stats_service import client_ip_from_request

RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").strip().lower() != "false"
DEFAULT_RATE_LIMIT = os.getenv("DEFAULT_RATE_LIMIT", "100/minute")
AUTH_RATE_LIMIT = os.getenv("AUTH_RATE_LIMIT", "30/minute")
CHAT_RATE_LIMIT = os.getenv("CHAT_RATE_LIMIT", "60/minute")
CHAT_MESSAGE_RATE_LIMIT = os.getenv("CHAT_MESSAGE_RATE_LIMIT", "20/minute")
ADMIN_RATE_LIMIT = os.getenv("ADMIN_RATE_LIMIT", "60/minute")


def rate_limit_key(request: Request) -> str:
    """Keys every rate limit bucket by the caller's IP address, honoring
    X-Forwarded-For behind a proxy or load balancer exactly like the
    login-activity dashboard does (see `client_ip_from_request`), so limits
    apply per client regardless of whether the caller holds a valid Firebase
    token yet. Falls back to slowapi's own socket-based lookup on the rare
    request where neither header nor client peer is available.
    """
    return client_ip_from_request(request) or get_remote_address(request)


limiter = Limiter(
    key_func=rate_limit_key,
    default_limits=[DEFAULT_RATE_LIMIT],
    enabled=RATE_LIMIT_ENABLED,
)
