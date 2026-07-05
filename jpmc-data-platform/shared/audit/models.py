# d:\DataPlatformAI\DataPlatformAI\jpmc-data-platform\shared\audit\models.py
"""Pydantic models for audit logging."""
from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    """Structured event emitted by the audit logging pipeline."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    request_id: str = Field(default="")
    user_id: str = Field(default="")
    email: str = Field(default="")
    action: str = Field(default="")
    resource_type: str = Field(default="")
    resource_id: str = Field(default="")
    http_method: str = Field(default="")
    path: str = Field(default="")
    status_code: int = Field(default=0)
    duration_ms: float = Field(default=0.0)
    ip_address: str = Field(default="")
    environment: str = Field(default="")
    service: str = Field(default="")
