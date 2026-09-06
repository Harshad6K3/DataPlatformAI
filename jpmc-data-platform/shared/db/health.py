"""Database health checks."""
from __future__ import annotations

from time import perf_counter

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def db_health_check(session: AsyncSession) -> dict[str, object]:
    started = perf_counter()
    try:
        await session.execute(text("SELECT 1"))
        return {"ok": True, "latency_ms": (perf_counter() - started) * 1000}
    except Exception as exc:
        return {
            "ok": False,
            "latency_ms": (perf_counter() - started) * 1000,
            "error": str(exc),
        }