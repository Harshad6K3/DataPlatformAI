"""Small shared SQLAlchemy write helpers."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession


async def bulk_insert(session: AsyncSession, model: Any, values: Iterable[dict[str, Any]]) -> None:
    await session.execute(insert(model), list(values))


async def upsert(session: AsyncSession, model: Any, values: dict[str, Any]) -> Any:
    instance = model(**values)
    session.add(instance)
    await session.flush()
    return instance