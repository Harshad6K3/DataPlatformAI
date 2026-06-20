"""Mock auth helpers for local development mode.

When `AUTH_MODE=mock`, the middleware will accept `X-Mock-User`
header with a JSON-serialized user object and skip JWT validation.
"""
from __future__ import annotations

from typing import Any, Dict
import json

from fastapi import Request


def parse_mock_user(header_value: str) -> Dict[str, Any]:
    """Parse the `X-Mock-User` header value (JSON) into a dict.

    Raises ValueError if parsing fails.
    """
    return json.loads(header_value)

async def get_mock_user_from_request(request: Request) -> Dict[str, Any]:
    val = request.headers.get("X-Mock-User")
    if not val:
        raise ValueError("X-Mock-User header missing in mock mode")
    return parse_mock_user(val)
