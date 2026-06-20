"""Database foundation shared across services."""

from .engine import async_engine, init_db
from .session import get_db, AsyncSession
from .base import Base, AuditMixin, SoftDeleteMixin, UUIDMixin
from .pagination import paginate, PaginatedResult
from .helpers import upsert, bulk_insert
from .health import db_health_check
from .testing import TestDatabase

__all__ = [
    "async_engine",
    "init_db",
    "AsyncSession",
    "get_db",
    "Base",
    "AuditMixin",
    "SoftDeleteMixin",
    "UUIDMixin",
    "paginate",
    "PaginatedResult",
    "upsert",
    "bulk_insert",
    "db_health_check",
    "TestDatabase",
]
