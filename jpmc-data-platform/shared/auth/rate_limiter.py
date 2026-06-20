"""Redis-backed sliding-window rate limiter.

Implements a per-user sliding window limiter using Redis sorted sets.
"""
from __future__ import annotations

from typing import Optional
import time
import logging

import redis.asyncio as aioredis

logger = logging.getLogger("shared.auth.rate_limiter")


class RedisRateLimiter:
    """Simple sliding window rate limiter using Redis sorted sets.

    Key design: per user key `rate:{user_id}` stores timestamps.
    On each request we remove timestamps older than window, add current,
    and count. We set TTL on the key to window seconds.
    """

    def __init__(self, redis_url: str, max_requests: int = 100, window_seconds: int = 60):
        self.redis = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def allow(self, user_id: str) -> bool:
        """Return True if the request is allowed, False if rate limit exceeded."""
        key = f"rate:{user_id}"
        now = int(time.time() * 1000)
        window_start = now - (self.window_seconds * 1000)

        async with self.redis.client() as conn:
            # Remove old entries
            await conn.zremrangebyscore(key, 0, window_start)
            # Add current timestamp
            await conn.zadd(key, {str(now): now})
            # Set expiration
            await conn.expire(key, self.window_seconds + 5)
            count = await conn.zcard(key)

        allowed = count <= self.max_requests
        if not allowed:
            logger.info({"event": "rate_limited", "user_id": user_id, "count": count})
        return allowed
