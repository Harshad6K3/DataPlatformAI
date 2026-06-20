"""Typed exceptions for the Claude client."""
from __future__ import annotations

from typing import Optional


class ClaudeClientError(Exception):
    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.cause = cause


class BudgetExceededError(ClaudeClientError):
    pass


class CircuitOpenError(ClaudeClientError):
    pass


class StructuredOutputError(ClaudeClientError):
    pass


class AgentMaxIterationsError(ClaudeClientError):
    pass
