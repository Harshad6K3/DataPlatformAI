"""Base AWS client wrapper with retry, logging, and credential handling."""
from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any, Callable, Dict, Optional, Type

import aioboto3
import botocore
from botocore.exceptions import ClientError

from .exceptions import AWSClientError

logger = logging.getLogger("shared.aws_clients")


class BaseAWSClient:
    def __init__(
        self,
        service_name: str,
        region_name: Optional[str] = None,
        role_arn: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        client_params: Optional[Dict[str, Any]] = None,
        mock_client: Optional[Any] = None,
    ):
        self.service_name = service_name
        self.region_name = region_name or os.getenv("AWS_REGION")
        self.role_arn = role_arn or os.getenv("AWS_ROLE_ARN")
        self.endpoint_url = endpoint_url
        self.client_params = client_params or {}
        self.mock_client = mock_client

    async def _get_session(self) -> aioboto3.Session:
        return aioboto3.Session()

    async def _get_client(self, client_type: str) -> Any:
        if self.mock_client is not None:
            return self.mock_client

        params: Dict[str, Any] = {"region_name": self.region_name}
        if self.endpoint_url:
            params["endpoint_url"] = self.endpoint_url
        params.update(self.client_params)

        session = await self._get_session()
        return await session.client(client_type, **params).__aenter__()

    async def _retry(self, func: Callable[..., Any], operation: str, *args: Any, **kwargs: Any) -> Any:
        retries = 3
        base_delay = 0.5
        for attempt in range(retries):
            start = time.monotonic()
            try:
                result = await func(*args, **kwargs)
                duration_ms = int((time.monotonic() - start) * 1000)
                logger.info({"service": self.service_name, "operation": operation, "duration_ms": duration_ms, "success": True})
                return result
            except ClientError as exc:
                code = exc.response.get("Error", {}).get("Code")
                status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
                logger.error({"service": self.service_name, "operation": operation, "duration_ms": int((time.monotonic() - start) * 1000), "success": False, "error": str(exc), "status_code": status})
                if code in {"Throttling", "ThrottlingException", "ProvisionedThroughputExceededException", "RequestLimitExceeded"} and attempt < retries - 1:
                    await asyncio.sleep(base_delay * (2 ** attempt))
                    continue
                raise AWSClientError(self.service_name, operation, str(exc), status)
            except Exception as exc:
                duration_ms = int((time.monotonic() - start) * 1000)
                logger.error({"service": self.service_name, "operation": operation, "duration_ms": duration_ms, "success": False, "error": str(exc)})
                raise AWSClientError(self.service_name, operation, str(exc))
