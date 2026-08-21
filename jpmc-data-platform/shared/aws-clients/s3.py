"""Async S3 client wrapper."""

from __future__ import annotations

import inspect
import os
from typing import Any, Optional

from shared.aws_clients.base import BaseAWSClient


class S3Client(BaseAWSClient):
    """Simple async wrapper around the boto3 S3 API."""

    def __init__(
        self,
        region_name: Optional[str] = None,
        role_arn: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        mock_client: Optional[Any] = None,
    ) -> None:
        if os.getenv("AWS_MODE") == "local":
            endpoint_url = endpoint_url or os.getenv("LOCALSTACK_URL", "http://localhost:4566")
        super().__init__("s3", region_name, role_arn, endpoint_url, mock_client=mock_client)

    async def get_object(self, bucket: str, key: str) -> bytes:
        """Retrieve an object from S3 as bytes."""
        async with await self._get_client("s3") as client:
            response = await self.execute(client.get_object, Bucket=bucket, Key=key)
            body = response.get("Body")
            if body is None:
                return b""
            data = body.read()
            if inspect.isawaitable(data):
                return await data
            return data

    async def put_object(self, bucket: str, key: str, body: bytes, content_type: str) -> None:
        """Upload bytes to S3."""
        async with await self._get_client("s3") as client:
            await self.execute(
                client.put_object,
                Bucket=bucket,
                Key=key,
                Body=body,
                ContentType=content_type,
            )

    async def list_objects(self, bucket: str, prefix: str) -> list[dict[str, Any]]:
        """List objects under a prefix."""
        async with await self._get_client("s3") as client:
            response = await self.execute(client.list_objects_v2, Bucket=bucket, Prefix=prefix)
            return response.get("Contents", [])

    async def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        expiry_seconds: int = 3600,
    ) -> str:
        """Generate a presigned URL for object access."""
        async with await self._get_client("s3") as client:
            return await self.execute(
                client.generate_presigned_url,
                "get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expiry_seconds,
            )
