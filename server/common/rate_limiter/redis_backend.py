import os
import time

import redis


class RateLimitExceeded(Exception):
    """Raised when the bucket has exceeded max_per_minute for the current window."""


def _redis_client():
    url = os.environ.get("REDIS_URL") or os.environ.get("CELERY_BROKER_URL") or "redis://localhost:6379/0"
    return redis.from_url(url, decode_responses=True)


def _window_key(bucket: str) -> str:
    window = int(time.time() // 60)
    return f"ratelimit:{bucket}:{window}"


def acquire_token(bucket: str, max_per_minute: int) -> None:
    """
    Consume one token for the given bucket in the current minute window.
    Uses Redis fixed-window counter. Raises RateLimitExceeded if limit exceeded.
    """
    if max_per_minute <= 0:
        return
    client = _redis_client()
    key = _window_key(bucket)
    pipe = client.pipeline()
    pipe.incr(key)
    pipe.expire(key, 120)
    count, _ = pipe.execute()
    if count > max_per_minute:
        client.decr(key)
        raise RateLimitExceeded(f"rate_limit_exceeded:{bucket}")
