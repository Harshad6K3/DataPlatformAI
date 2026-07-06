"""Compatibility wrapper exposing the shared AWS client exceptions."""

from __future__ import annotations

from shared.aws_clients.exceptions import AWSClientError

__all__ = ["AWSClientError"]
