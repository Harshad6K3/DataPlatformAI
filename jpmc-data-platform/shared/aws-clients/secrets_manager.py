"""Async Secrets Manager wrapper with in-memory caching."""
from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

import aioboto3
from botocore.exceptions import ClientError

from .base import BaseAWSClient
from .exceptions import AWSClientError


class SecretsManagerClient(BaseAWSClient):
    def __init__(
        self,
        region_name: Optional[str] = None,
        role_arn: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        mock_client: Optional[Any] = None,
        cache_ttl: int = 300,
    ):
        if os.getenv("AWS_MODE") == "local":
            endpoint_url = endpoint_url or os.getenv("LOCALSTACK_URL")
        super().__init__("secretsmanager", region_name, role_arn, endpoint_url, mock_client=mock_client)
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}

    async def get_secret(self, secret_name: str) -> str:
        if os.getenv("AWS_MODE") == "local":
            return self._load_local_secret(secret_name)

        cached = self._cache.get(secret_name)
        if cached and time.time() < cached["expires_at"]:
            return cached["value"]

        async with await self._get_client("secretsmanager") as client:
            response = await self._retry(client.get_secret_value, "get_secret", SecretId=secret_name)
            value = response.get("SecretString") or response.get("SecretBinary")
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            self._cache[secret_name] = {"value": value, "expires_at": time.time() + self.cache_ttl}
            return value

    def _load_local_secret(self, secret_name: str) -> str:
        from dotenv import load_dotenv

        load_dotenv()
        value = os.getenv(secret_name)
        if value is None:
            raise AWSClientError("secretsmanager", "get_secret", f"Secret {secret_name} not found in .env")
        return value
