"""Audit action decorator for fine-grained request logging."""
from __future__ import annotations

import functools
from typing import Any, Callable

from fastapi import Request


def audit_action(action: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            request: Request = kwargs.get("request") or next((a for a in args if isinstance(a, Request)), None)
            if request is None:
                return await func(*args, **kwargs)

            request.state.audit_request = request.state.audit_request or {}
            request.state.audit_request["action"] = action
            return await func(*args, **kwargs)

        return wrapper

    return decorator
