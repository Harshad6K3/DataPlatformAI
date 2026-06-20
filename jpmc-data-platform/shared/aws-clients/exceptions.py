"""Typed AWS client exceptions."""
from __future__ import annotations

from typing import Optional


class AWSClientError(Exception):
    def __init__(self, service: str, operation: str, message: str, status_code: Optional[int] = None):
        self.service = service
        self.operation = operation
        self.message = message
        self.status_code = status_code
        super().__init__(f"{service}.{operation}: {message}")
