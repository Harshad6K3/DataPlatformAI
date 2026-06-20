"""Audit logger implementation."""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from .models import AuditEvent
from .redaction import redact_dict
from .sinks.stdout import StdoutSink
from .sinks.cloudwatch import CloudWatchSink
from .sinks.s3 import S3Sink

logger = logging.getLogger("shared.audit.logger")


class AuditLogger:
    def __init__(
        self,
        service_name: str,
        environment: Optional[str] = None,
        cloudwatch_group: Optional[str] = None,
        s3_bucket: Optional[str] = None,
        sinks: Optional[List[Any]] = None,
    ):
        self.service_name = service_name
        self.environment = environment or os.getenv("ENVIRONMENT", "local")
        self.request_id_header = "X-Request-ID"
        self.sinks = sinks or []
        if not self.sinks:
            if self.environment == "local":
                self.sinks.append(StdoutSink())
            if cloudwatch_group:
                self.sinks.append(CloudWatchSink(cloudwatch_group, service_name))
            if s3_bucket:
                self.sinks.append(S3Sink(s3_bucket, service_name))

    async def log(self, data: Dict[str, Any]) -> None:
        event = self._build_event(data)
        tasks = [sink.log(event) for sink in self.sinks]
        await asyncio.gather(*tasks)

    def _build_event(self, data: Dict[str, Any]) -> AuditEvent:
        sanitized = redact_dict(data)
        event = AuditEvent(
            timestamp=sanitized.get("timestamp", datetime.utcnow()),
            request_id=sanitized.get("request_id", uuid4()),
            environment=self.environment,
            user_id=sanitized.get("user_id"),
            email=sanitized.get("email"),
            action=sanitized["action"],
            resource_type=sanitized["resource_type"],
            resource_id=sanitized["resource_id"],
            http_method=sanitized["http_method"],
            path=sanitized["path"],
            status_code=sanitized["status_code"],
            duration_ms=sanitized["duration_ms"],
            ip_address=sanitized.get("ip_address"),
            service=self.service_name,
        )
        return event
