"""Base async AWS client wrapper with retry handling."""

from __future__ import annotations

import asyncio
import inspect
import logging
import os
import time
from typing import Any, Callable, Optional

import aioboto3
from botocore.exceptions import ClientError

from shared.aws_clients.exceptions import AWSClientError

logger = logging.getLogger("shared.aws_clients")


class BaseAWSClient:
    """Base class for async AWS service clients."""

    def __init__(
        self,
        service_name: str,
        region_name: Optional[str] = None,
        role_arn: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        client_params: Optional[dict[str, Any]] = None,
        mock_client: Optional[Any] = None,
    ) -> None:
        self.service_name = service_name
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        self.role_arn = role_arn or os.getenv("AWS_ROLE_ARN")
        self.endpoint_url = endpoint_url
        self.client_params = client_params or {}
        self.mock_client = mock_client

        if os.getenv("AWS_MODE") == "local":
            self.endpoint_url = self.endpoint_url or os.getenv("LOCALSTACK_URL", "http://localhost:4566")

    async def _get_session(self) -> aioboto3.Session:
        return aioboto3.Session()

    async def get_client(self, service_name: str) -> Any:
        """Return an async aioboto3 client for the requested AWS service."""
        if self.mock_client is not None:
            return self.mock_client

        params: dict[str, Any] = {"region_name": self.region_name}
        if self.endpoint_url:
            params["endpoint_url"] = self.endpoint_url
        params.update(self.client_params)

        session = await self._get_session()
        client = session.client(service_name, **params)
        return client

    async def _get_client(self, client_type: str) -> Any:
        return await self.get_client(client_type)

    async def execute(self, operation_func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Run an async client operation with exponential backoff retry."""
        retries = 3
        delays = (0.5, 1.0, 2.0)
        last_error: Exception | None = None

        for attempt in range(retries):
            try:
                result = operation_func(*args, **kwargs)
                if inspect.isawaitable(result):
                    result = await result
                return result
            except ClientError as exc:
                last_error = exc
                error_code = exc.response.get("Error", {}).get("Code")
                status_code = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
                if error_code in {
                    "Throttling",
                    "ThrottlingException",
                    "ServiceUnavailable",
                    "ProvisionedThroughputExceededException",
                    "RequestLimitExceeded",
                } and attempt < retries - 1:
                    await asyncio.sleep(delays[attempt])
                    continue
                raise AWSClientError(
                    self.service_name,
                    getattr(operation_func, "__name__", "operation"),
                    str(exc),
                    status_code,
                ) from exc
            except Exception as exc:  # pragma: no cover - defensive path
                last_error = exc
                raise AWSClientError(
                    self.service_name,
                    getattr(operation_func, "__name__", "operation"),
                    str(exc),
                ) from exc

        if last_error is not None:
            raise AWSClientError(
                self.service_name,
                getattr(operation_func, "__name__", "operation"),
                str(last_error),
            ) from last_error

        raise AWSClientError(self.service_name, "execute", "operation failed")
