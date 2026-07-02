# d:\DataPlatformAI\DataPlatformAI\jpmc-data-platform\shared\auth\models.py
"""Pydantic models for authentication."""
from __future__ import annotations

from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    """Represents an authenticated user or service account."""

    user_id: str
    email: str
    roles: list[str]
    domains: list[str]
    is_service_account: bool
