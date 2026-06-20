"""Tests for audit logger build and sink invocation."""
import asyncio
from datetime import datetime
from uuid import UUID

import pytest

from shared.audit.logger import AuditLogger
from shared.audit.models import AuditEvent


class DummySink:
    def __init__(self):
        self.events = []

    async def log(self, event: AuditEvent) -> None:
        self.events.append(event.json())


@pytest.mark.asyncio
async def test_audit_logger_uses_stdout_by_default(monkeypatch):
    sink = DummySink()
    logger = AuditLogger(service_name="test", sinks=[sink])
    data = {
        "action": "dataset.read",
        "resource_type": "dataset",
        "resource_id": "123",
        "http_method": "GET",
        "path": "/datasets/123",
        "status_code": 200,
        "duration_ms": 15,
        "user_id": "u1",
        "email": "user@example.com",
        "ip_address": "127.0.0.1",
    }
    await logger.log(data)
    assert sink.events
    event = sink.events[0]
    assert "dataset.read" in event
    assert "user@example.com" in event
    assert "service" in event
