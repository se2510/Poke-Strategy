import time
from fastapi import HTTPException, Request
from typing import Dict

# Simple global in-memory rate limiter (not for production scale)
# Keyed by client IP; window in seconds.

_WINDOW = 60  # 1 minute window
_LIMIT = 120  # max requests per window
_STORE: Dict[str, tuple[int, float]] = {}  # ip -> (count, window_start)


def rate_limit(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    count, start = _STORE.get(ip, (0, now))
    if now - start > _WINDOW:
        # reset window
        count, start = 0, now
    count += 1
    _STORE[ip] = (count, start)
    if count > _LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


def rate_status(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    count, start = _STORE.get(ip, (0, now))
    remaining = max(_LIMIT - count, 0)
    reset_in = max(int(_WINDOW - (now - start)), 0)
    return {
        "ip": ip,
        "limit": _LIMIT,
        "used": count,
        "remaining": remaining,
        "window_seconds": _WINDOW,
        "reset_in_seconds": reset_in,
    }
