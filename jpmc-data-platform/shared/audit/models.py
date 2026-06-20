"""Pydantic models for audit logging."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    timestamp: datetime
    request_id: UUID
    environment: str
    user_id: Optional[str]
    email: Optional[str]
    action: str
    resource_type: str
    resource_id: str
    http_method: str
    path: str
    status_code: int
    duration_ms: int
    ip_address: Optional[str]
    service: str = Field(..., description="Service name for the audit event")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
