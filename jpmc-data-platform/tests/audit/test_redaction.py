"""Tests for audit redaction logic."""
from shared.audit.redaction import redact_dict, REDACTED_VALUE


def test_redacts_sensitive_fields():
    data = {
        "password": "supersecret",
        "token": "abc123",
        "email": "user@example.com",
        "details": {
            "secret_key": "value",
            "passport": "12345",
            "nested": {"credential": "xyz"},
        },
    }

    redacted = redact_dict(data)

    assert redacted["password"] == REDACTED_VALUE
    assert redacted["token"] == REDACTED_VALUE
    assert redacted["details"]["secret_key"] == REDACTED_VALUE
    assert redacted["details"]["passport"] == REDACTED_VALUE
    assert redacted["details"]["nested"]["credential"] == REDACTED_VALUE
    assert redacted["email"] == "user@example.com"
