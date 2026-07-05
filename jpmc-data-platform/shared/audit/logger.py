# d:\DataPlatformAI\DataPlatformAI\jpmc-data-platform\shared\audit\logger.py
"""Audit logger implementation."""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .models import AuditEvent
from .redaction import redact
from .sinks.stdout import StdoutSink

logger = logging.getLogger("shared.audit.logger")


class AuditLogger:
    """Collect and emit audit events through one or more sinks."""

    def __init__(
        self,
        service_name: str | None = None,
        sinks: list[Any] | None = None,
        environment: str | None = None,
    ) -> None:
        self.service_name = service_name or os.getenv("SERVICE_NAME", "shared-service")
        self.environment = environment or os.getenv("ENVIRONMENT", "local")
        self.sinks = list(sinks or [])
        if not self.sinks:
            self.sinks.append(StdoutSink())

    async def log(self, event: AuditEvent | dict[str, Any]) -> None:
        """Sanitize and write an event to each configured sink."""
        audit_event = self._build_event(event)
        await asyncio.gather(*(self._emit_to_sink(sink, audit_event) for sink in self.sinks))

    def _build_event(self, event: AuditEvent | dict[str, Any]) -> AuditEvent:
        if isinstance(event, AuditEvent):
            return event

        data = dict(event)
        sanitized = redact(data)
        return AuditEvent(
            timestamp=sanitized.get("timestamp", datetime.now(timezone.utc)),
            request_id=str(sanitized.get("request_id", uuid4())),
            user_id=str(sanitized.get("user_id", "")),
            email=str(sanitized.get("email", "")),
            action=str(sanitized.get("action", "")),
            resource_type=str(sanitized.get("resource_type", "")),
            resource_id=str(sanitized.get("resource_id", "")),
            http_method=str(sanitized.get("http_method", "")),
            path=str(sanitized.get("path", "")),
            status_code=int(sanitized.get("status_code", 0)),
            duration_ms=float(sanitized.get("duration_ms", 0.0)),
            ip_address=str(sanitized.get("ip_address", "")),
            environment=str(sanitized.get("environment", self.environment)),
            service=self.service_name,
        )

    async def _emit_to_sink(self, sink: Any, event: AuditEvent) -> None:
        if hasattr(sink, "write"):
            await sink.write(event)
        elif hasattr(sink, "log"):
            await sink.log(event)
