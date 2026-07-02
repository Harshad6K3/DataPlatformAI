# d:\DataPlatformAI\DataPlatformAI\jpmc-data-platform\shared\auth\dependencies.py
"""FastAPI dependency helpers for authentication."""
from __future__ import annotations

from fastapi import Depends, HTTPException, Request

from .models import AuthenticatedUser


async def get_current_user(request: Request) -> AuthenticatedUser:
    """Return the authenticated user from request state.

    Raises 401 if no authenticated user is attached to request.state.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthenticated")

    if isinstance(user, AuthenticatedUser):
        return user

    return AuthenticatedUser(**user)
