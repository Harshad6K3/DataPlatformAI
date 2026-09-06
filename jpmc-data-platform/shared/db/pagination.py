"""Async pagination helpers for SQLAlchemy select statements."""
from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class PaginatedResult(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int


async def paginate(
    session: AsyncSession,
    query: Any,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResult[Any]:
    """Execute a select statement with a count query and limit/offset."""
    if page < 1:
        raise ValueError("page must be at least 1")
    if page_size < 1:
        raise ValueError("page_size must be at least 1")

    count_query = select(func.count()).select_from(query.order_by(None).subquery())
    total = int((await session.execute(count_query)).scalar_one())
    result = await session.execute(query.limit(page_size).offset((page - 1) * page_size))
    items = list(result.scalars().all())
    pages = (total + page_size - 1) // page_size

    return PaginatedResult(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )