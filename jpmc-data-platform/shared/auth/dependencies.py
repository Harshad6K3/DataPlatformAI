"""FastAPI dependency helpers for authentication."""
from __future__ import annotations

from typing import Optional
from fastapi import Request, Depends, HTTPException

from .models import AuthenticatedUser


async def get_current_user(request: Request) -> AuthenticatedUser:
    """Dependency that returns the authenticated user attached to request.state.

    Raises 401 if not authenticated.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthenticated")

    # If it's already an AuthenticatedUser return it, else coerce
    if isinstance(user, AuthenticatedUser):
        return user
    return AuthenticatedUser(**user)
