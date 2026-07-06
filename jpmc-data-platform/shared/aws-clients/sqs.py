"""Compatibility wrapper exposing the shared SQS client."""

from __future__ import annotations

from shared.aws_clients.sqs import SQSClient

__all__ = ["SQSClient"]
