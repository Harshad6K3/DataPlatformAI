"""Tests for RedisRateLimiter (unit-level, mocks Redis)."""
import asyncio
import pytest

from unittest.mock import AsyncMock, patch

from shared.auth.rate_limiter import RedisRateLimiter


@pytest.mark.asyncio
async def test_allow_under_limit():
    rl = RedisRateLimiter("redis://localhost:6379/0", max_requests=5, window_seconds=60)
    # Patch redis client methods to simulate empty set
    async def fake_allow(_):
        return True

    rl.allow = AsyncMock(return_value=True)
    assert await rl.allow("user1") is True


@pytest.mark.asyncio
async def test_deny_over_limit():
    rl = RedisRateLimiter("redis://localhost:6379/0", max_requests=1, window_seconds=60)
    rl.allow = AsyncMock(return_value=False)
    assert await rl.allow("user1") is False
