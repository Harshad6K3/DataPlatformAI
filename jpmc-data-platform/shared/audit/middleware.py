"""FastAPI middleware for audit logging."""
from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from .logger import AuditLogger

logger = logging.getLogger("shared.audit.middleware")

PUBLIC_PATHS = {"/health", "/ready", "/docs", "/openapi.json"}


class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, audit_logger: AuditLogger):
        super().__init__(app)
        self.audit_logger = audit_logger

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        request.state.start_time = time.perf_counter()
        request.state.audit_request = {
            "request_id": request_id,
            "environment": self.audit_logger.environment,
            "user_id": None,
            "email": None,
            "action": "request",
            "resource_type": "http",
            "resource_id": "",
            "http_method": request.method,
            "path": request.url.path,
            "status_code": 0,
            "duration_ms": 0,
            "ip_address": request.client.host if request.client else None,
        }

        headers = dict(request.headers)
        headers["x-request-id"] = request_id
        request.scope["headers"] = [(k.encode(), v.encode()) for k, v in headers.items()]

        if request.url.path in PUBLIC_PATHS:
            response = await call_next(request)
            return response

        response = await call_next(request)
        request.state.audit_request["status_code"] = response.status_code
        request.state.audit_request["duration_ms"] = int((time.perf_counter() - request.state.start_time) * 1000)
        await self.audit_logger.log(request.state.audit_request)
        return response
