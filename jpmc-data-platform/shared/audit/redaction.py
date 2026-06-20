"""Redaction utilities for audit logging."""
from __future__ import annotations

from typing import Any, Dict

REDACTED_FIELDS = {
    "password",
    "token",
    "secret",
    "key",
    "credential",
    "ssn",
    "national_id",
    "passport",
}

REDACTED_VALUE = "REDACTED"


def redact_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively redact sensitive fields from a dictionary."""
    redacted: Dict[str, Any] = {}
    for key, value in data.items():
        normalized = key.lower()
        if any(field in normalized for field in REDACTED_FIELDS):
            redacted[key] = REDACTED_VALUE
        elif isinstance(value, dict):
            redacted[key] = redact_dict(value)
        elif isinstance(value, list):
            redacted[key] = [_redact_value(item) for item in value]
        else:
            redacted[key] = value
    return redacted


def _redact_value(value: Any) -> Any:
    if isinstance(value, dict):
        return redact_dict(value)
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    return value
