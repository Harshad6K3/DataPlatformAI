"""Async SQLAlchemy engine setup."""
from __future__ import annotations

import os
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost/db")

async_engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=0,
    pool_timeout=30,
    pool_recycle=1800,
    future=True,
)


def init_db() -> AsyncEngine:
    return async_engine
