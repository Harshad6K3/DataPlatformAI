"""Audit action decorator for fine-grained request logging."""
from __future__ import annotations

import functools
from typing import Any, Callable

from fastapi import Request


def audit_action(action: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Attach an audit action name to the current request state."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            request: Request | None = kwargs.get("request") or next((a for a in args if isinstance(a, Request)), None)
            if request is None:
                return await func(*args, **kwargs)

            request.state.audit_action = action
            audit_request: dict[str, Any] = getattr(request.state, "audit_request", None) or {}
            audit_request["action"] = action
            request.state.audit_request = audit_request
            return await func(*args, **kwargs)

        return wrapper

    return decorator
