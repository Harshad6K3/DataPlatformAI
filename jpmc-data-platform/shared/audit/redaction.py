# d:\DataPlatformAI\DataPlatformAI\jpmc-data-platform\shared\audit\redaction.py
"""Redaction utilities for audit logging."""
from __future__ import annotations

import re
from typing import Any

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
AWS_ACCOUNT_ID_PATTERN = re.compile(r"^\d{12}$")


def redact(data: dict[str, Any]) -> dict[str, Any]:
    """Recursively redact sensitive fields or AWS account IDs from a dictionary."""
    if not isinstance(data, dict):
        return data

    redacted: dict[str, Any] = {}
    for key, value in data.items():
        normalized_key = str(key).lower()
        if any(field in normalized_key for field in REDACTED_FIELDS):
            redacted[key] = REDACTED_VALUE
        elif isinstance(value, dict):
            redacted[key] = redact(value)
        elif isinstance(value, list):
            redacted[key] = [_redact_value(item) for item in value]
        else:
            redacted[key] = _redact_value(value)
    return redacted


def redact_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Backward-compatible wrapper for the recursive redaction helper."""
    return redact(data)


def _redact_value(value: Any) -> Any:
    if isinstance(value, str) and AWS_ACCOUNT_ID_PATTERN.fullmatch(value):
        return REDACTED_VALUE
    return value
