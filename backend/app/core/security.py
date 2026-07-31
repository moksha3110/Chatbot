"""
Security: API-key authentication and rate limiting.

These are FastAPI DEPENDENCIES — small functions we attach to routes. FastAPI
runs them before the route handler; if they raise, the request is rejected.

  - require_api_key: checks the X-API-Key header against the configured key.
        If no API_KEY is configured, auth is DISABLED (convenient for local dev).
  - rate_limit: caps how many requests a client (by IP) may make per minute,
        using a simple in-memory sliding window. Protects against abuse/runaway
        clients. (A multi-server deployment would use Redis instead of memory.)
"""

import time
from collections import defaultdict, deque

from fastapi import Header, HTTPException, Request

from app.core.config import settings


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    # If no key is configured, authentication is turned off (dev mode).
    if not settings.API_KEY:
        return
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")


# Per-client request timestamps, for the sliding-window rate limiter.
_hits: dict[str, deque] = defaultdict(deque)


def _check_rate(client_id: str) -> bool:
    """Return True if the client is under the limit, False if over it."""
    limit = settings.RATE_LIMIT_PER_MINUTE
    if limit <= 0:  # 0 or negative disables rate limiting
        return True
    now = time.time()
    window = _hits[client_id]
    # Drop timestamps older than 60 seconds.
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= limit:
        return False
    window.append(now)
    return True


def rate_limit(request: Request) -> None:
    client_id = request.client.host if request.client else "unknown"
    if not _check_rate(client_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please slow down and try again shortly.",
        )
