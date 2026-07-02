# d:\DataPlatformAI\DataPlatformAI\jpmc-data-platform\shared\auth\mock.py
"""Mock auth helpers for local development mode.

When `AUTH_MODE=mock`, the middleware will accept `X-Mock-User`
header with a JSON-serialized user object and skip JWT validation.
"""
from __future__ import annotations

import json
from typing import Any

from fastapi import Request

from .models import AuthenticatedUser


def parse_mock_user(header_value: str) -> dict[str, Any]:
    """Parse the `X-Mock-User` header value (JSON) into a dict.

    Raises ValueError if parsing fails.
    """
    return json.loads(header_value)


async def get_mock_user_from_request(request: Request) -> AuthenticatedUser:
    """Return an AuthenticatedUser from the X-Mock-User header or default dev user."""
    header_value = request.headers.get("X-Mock-User")
    if header_value:
        payload = parse_mock_user(header_value)
        return AuthenticatedUser(
            user_id=str(payload.get("user_id", "dev-user-001")),
            email=str(payload.get("email", "dev@bank.com")),
            roles=payload.get("roles", ["engineer"]),
            domains=payload.get("domains", ["all"]),
            is_service_account=bool(payload.get("is_service_account", False)),
        )

    return AuthenticatedUser(
        user_id="dev-user-001",
        email="dev@bank.com",
        roles=["engineer"],
        domains=["all"],
        is_service_account=False,
    )
