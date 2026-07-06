# d:\DataPlatformAI\DataPlatformAI\jpmc-data-platform\shared\audit\middleware.py
"""FastAPI middleware for audit logging."""
from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from .logger import AuditLogger
from .models import AuditEvent

logger = logging.getLogger("shared.audit.middleware")


class AuditMiddleware(BaseHTTPMiddleware):
    """Wrap each request and emit an audit event after the response is produced."""

    def __init__(self, app, audit_logger: AuditLogger) -> None:
        super().__init__(app)
        self.audit_logger = audit_logger

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        request.state.audit_started_at = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - request.state.audit_started_at) * 1000, 2)
        user = getattr(request.state, "user", None)
        user_id = getattr(user, "user_id", None) or getattr(user, "id", None) or ""
        email = getattr(user, "email", None) or ""

        audit_request = getattr(request.state, "audit_request", None) or {}
        action = getattr(request.state, "audit_action", None) or audit_request.get("action", "request")

        event = AuditEvent(
            timestamp=datetime.now(timezone.utc),
            request_id=request_id,
            user_id=str(user_id),
            email=str(email),
            action=str(action),
            resource_type="http",
            resource_id=request.url.path,
            http_method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            ip_address=request.client.host if request.client else "",
            environment=self.audit_logger.environment,
            service=self.audit_logger.service_name,
        )
        await self.audit_logger.log(event)
        return response
