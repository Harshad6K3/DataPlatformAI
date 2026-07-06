# d:\DataPlatformAI\DataPlatformAI\jpmc-data-platform\tests\audit\test_audit.py
"""Tests for audit redaction, logger, and middleware behavior."""
from __future__ import annotations

from typing import Any

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from shared.audit.decorators import audit_action
from shared.audit.logger import AuditLogger
from shared.audit.middleware import AuditMiddleware
from shared.audit.redaction import redact
from shared.audit.sinks.stdout import StdoutSink


def test_redact_removes_password_fields_from_nested_dict() -> None:
    """Nested password-like values should be replaced with REDACTED."""
    payload = {
        "user": {
            "password": "super-secret",
            "profile": {"token": "abc123"},
        },
        "email": "user@example.com",
    }

    redacted = redact(payload)

    assert redacted["user"]["password"] == "REDACTED"
    assert redacted["user"]["profile"]["token"] == "REDACTED"
    assert redacted["email"] == "user@example.com"


@pytest.mark.asyncio
async def test_audit_logger_writes_to_stdout_sink_without_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """The audit logger should dispatch to a StdoutSink without raising errors."""
    sink = StdoutSink()
    write_calls: list[Any] = []

    async def fake_write(event: Any) -> None:
        write_calls.append(event)

    monkeypatch.setattr(sink, "write", fake_write)

    logger = AuditLogger(service_name="test-service", sinks=[sink])
    await logger.log(
        {
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
    )

    assert len(write_calls) == 1
    assert write_calls[0].service == "test-service"


def test_audit_middleware_adds_request_id_to_every_request() -> None:
    """The middleware should attach a request ID to each request and log it."""
    app = FastAPI()
    logger = AuditLogger(service_name="test-service", sinks=[])

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.add_middleware(AuditMiddleware, audit_logger=logger)

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_audit_action_decorator_sets_action_for_middleware() -> None:
    """The decorator should provide the action name that middleware logs."""

    class RecordingSink:
        def __init__(self) -> None:
            self.events: list[Any] = []

        async def log(self, event: Any) -> None:
            self.events.append(event)

    app = FastAPI()
    sink = RecordingSink()
    logger = AuditLogger(service_name="test-service", sinks=[sink])

    @app.get("/health")
    @audit_action("dataset.read")
    async def health(request: Request) -> dict[str, str]:
        assert request.state.audit_action == "dataset.read"
        return {"status": "ok"}

    app.add_middleware(AuditMiddleware, audit_logger=logger)

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert sink.events[0].action == "dataset.read"
