"""Pydantic models for authentication."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    """Represents an authenticated user or service account.

    Attributes
    - user_id: stable identifier (sub or client_id)
    - email: optional user email
    - roles: list of role strings
    - domains: list of domains or groups
    - is_service_account: true for client-credentials tokens
    """

    user_id: str
    email: Optional[str] = None
    roles: List[str] = []
    domains: List[str] = []
    is_service_account: bool = False
