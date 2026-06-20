"""Structured audit logging package for the data platform."""

from .decorators import audit_action
from .logger import AuditLogger
from .middleware import AuditMiddleware
from .models import AuditEvent
from .redaction import redact_dict
from .sinks.cloudwatch import CloudWatchSink
from .sinks.s3 import S3Sink
from .sinks.stdout import StdoutSink

__all__ = [
    "AuditLogger",
    "AuditMiddleware",
    "AuditEvent",
    "audit_action",
    "redact_dict",
    "CloudWatchSink",
    "S3Sink",
    "StdoutSink",
]
