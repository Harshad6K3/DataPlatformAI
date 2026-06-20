"""Tests for the Claude sanitiser."""
from shared.claude_client.sanitiser import Sanitiser


def test_sanitiser_replaces_aws_account_and_ip():
    text = "Account 123456789012 accessed from 10.0.0.1"
    sanitiser = Sanitiser()
    sanitized, record = sanitiser.sanitise(text, "svc", "test")

    assert "[AWS-ACCOUNT]" in sanitized
    assert "[IP-ADDRESS]" in sanitized
    assert record.rules_applied["aws_account"] == 1
    assert record.rules_applied["ip_address"] == 1


def test_sanitiser_bypassed_when_disabled():
    text = "secret = \"super\""
    sanitiser = Sanitiser()
    sanitized, record = sanitiser.sanitise(text, "svc", "test", sanitise=False)

    assert sanitized == text
    assert record.bypassed is True
