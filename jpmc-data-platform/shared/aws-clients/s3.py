"""Async S3 client wrapper."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from .base import BaseAWSClient


class S3Client(BaseAWSClient):
    def __init__(
        self,
        region_name: Optional[str] = None,
        role_arn: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        mock_client: Optional[Any] = None,
    ):
        if os.getenv("AWS_MODE") == "local":
            endpoint_url = endpoint_url or os.getenv("LOCALSTACK_URL")
        super().__init__("s3", region_name, role_arn, endpoint_url, mock_client=mock_client)

    async def get_object(self, bucket: str, key: str) -> Dict[str, Any]:
        async with await self._get_client("s3") as client:
            return await self._retry(client.get_object, "get_object", Bucket=bucket, Key=key)

    async def put_object(self, bucket: str, key: str, body: Any, **kwargs: Any) -> Dict[str, Any]:
        async with await self._get_client("s3") as client:
            return await self._retry(client.put_object, "put_object", Bucket=bucket, Key=key, Body=body, **kwargs)

    async def list_objects_paginated(self, bucket: str, prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        async with await self._get_client("s3") as client:
            paginator = client.get_paginator("list_objects_v2")
            result = []
            async for page in paginator.paginate(Bucket=bucket, Prefix=prefix or ""):
                result.extend(page.get("Contents", []))
            return result

    async def generate_presigned_url(self, bucket: str, key: str, expires_in: int = 3600) -> str:
        async with await self._get_client("s3") as client:
            return await self._retry(client.generate_presigned_url, "generate_presigned_url", "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=expires_in)

    async def copy_object(self, source_bucket: str, source_key: str, dest_bucket: str, dest_key: str, **kwargs: Any) -> Dict[str, Any]:
        copy_source = {"Bucket": source_bucket, "Key": source_key}
        async with await self._get_client("s3") as client:
            return await self._retry(client.copy_object, "copy_object", CopySource=copy_source, Bucket=dest_bucket, Key=dest_key, **kwargs)
