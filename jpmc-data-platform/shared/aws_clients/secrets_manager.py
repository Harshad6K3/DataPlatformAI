"""Async Secrets Manager client wrapper with local cache support."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Optional

from dotenv import dotenv_values

from shared.aws_clients.base import BaseAWSClient
from shared.aws_clients.exceptions import AWSClientError


class SecretsManagerClient(BaseAWSClient):
    """Read secrets from AWS Secrets Manager or a local .env file."""

    def __init__(
        self,
        region_name: Optional[str] = None,
        role_arn: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        mock_client: Optional[Any] = None,
        cache_ttl: int = 300,
    ) -> None:
        if os.getenv("AWS_MODE") == "local":
            endpoint_url = endpoint_url or os.getenv("LOCALSTACK_URL", "http://localhost:4566")
        super().__init__("secretsmanager", region_name, role_arn, endpoint_url, mock_client=mock_client)
        self.cache_ttl = cache_ttl
        self._cache: dict[str, dict[str, Any]] = {}

    async def get_secret(self, secret_name: str) -> str:
        """Return a secret from cache, local .env, or Secrets Manager."""
        if os.getenv("AWS_MODE") == "local":
            return self._get_local_secret(secret_name)

        cached = self._cache.get(secret_name)
        if cached and time.time() < cached["expires_at"]:
            return cached["value"]

        async with await self._get_client("secretsmanager") as client:
            response = await self.execute(client.get_secret_value, SecretId=secret_name)
            value = response.get("SecretString") or response.get("SecretBinary")
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            self._cache[secret_name] = {"value": value, "expires_at": time.time() + self.cache_ttl}
            return value

    def _get_local_secret(self, secret_name: str) -> str:
        env_path = Path(".env")
        values = dotenv_values(env_path)
        value = values.get(secret_name)
        if value is None:
            raise AWSClientError("secretsmanager", "get_secret", f"Secret {secret_name} not found in .env")
        return value
