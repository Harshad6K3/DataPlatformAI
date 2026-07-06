"""Compatibility wrapper exposing the shared Secrets Manager client."""

from __future__ import annotations

from shared.aws_clients.secrets_manager import SecretsManagerClient

__all__ = ["SecretsManagerClient"]
