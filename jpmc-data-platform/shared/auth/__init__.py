# d:\DataPlatformAI\DataPlatformAI\jpmc-data-platform\shared\auth\__init__.py
"""Authentication helpers for shared services."""

from .dependencies import get_current_user
from .middleware import JWTAuthMiddleware
from .models import AuthenticatedUser

__all__ = [
    "AuthenticatedUser",
    "JWTAuthMiddleware",
    "get_current_user",
]
