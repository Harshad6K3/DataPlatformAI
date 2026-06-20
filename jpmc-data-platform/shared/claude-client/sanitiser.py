"""Sanitiser for Claude prompts and messages."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .models import SanitisationRecord


DEFAULT_TRADE_ID_REGEX = r"[A-Z]{2}[0-9]{6,10}"


class Sanitiser:
    aws_account_pattern = re.compile(r"\b\d{12}\b")
    ip_pattern = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
    secret_pattern = re.compile(r"(?i)(secret|password|token|key|credential)\s*=\s*\".*?\"")
    isin_pattern = re.compile(r"\b[A-Z]{2}[A-Z0-9]{10}\b")

    def __init__(self, trade_id_regex: Optional[str] = None):
        self.trade_id_pattern = re.compile(trade_id_regex or DEFAULT_TRADE_ID_REGEX)

    def sanitise(self, text: str, caller_service: str, use_case: str, sanitise: bool = True) -> Tuple[str, SanitisationRecord]:
        record = SanitisationRecord(timestamp=datetime.utcnow(), caller_service=caller_service, use_case=use_case, rules_applied={})
        if not sanitise:
            record.bypassed = True
            return text, record

        sanitized = text
        sanitized, rule_counts = self._apply_rule(self.aws_account_pattern, sanitized, "aws_account")
        record.rules_applied["aws_account"] = rule_counts
        sanitized, rule_counts = self._apply_rule(self.ip_pattern, sanitized, "ip_address")
        record.rules_applied["ip_address"] = rule_counts
        sanitized, rule_counts = self._apply_rule(self.secret_pattern, sanitized, "credentials")
        record.rules_applied["credentials"] = rule_counts
        sanitized, rule_counts = self._apply_rule(self.isin_pattern, sanitized, "isin")
        record.rules_applied["isin"] = rule_counts
        sanitized, rule_counts = self._apply_rule(self.trade_id_pattern, sanitized, "trade_id")
        record.rules_applied["trade_id"] = rule_counts
        return sanitized, record

    def _apply_rule(self, pattern: re.Pattern, text: str, label: str) -> Tuple[str, int]:
        replaced = pattern.sub(self._replacement(label), text)
        count = len(pattern.findall(text))
        return replaced, count

    @staticmethod
    def _replacement(label: str) -> str:
        mapping = {
            "aws_account": "[AWS-ACCOUNT]",
            "ip_address": "[IP-ADDRESS]",
            "credentials": "[REDACTED]",
            "isin": "[ISIN]",
            "trade_id": "[TRADE-ID]",
        }
        return mapping.get(label, "[REDACTED]")
