"""Basic S3 client tests."""
import asyncio
from contextlib import asynccontextmanager
from typing import Any

import boto3
import pytest
from moto import mock_aws

from shared.aws_clients.exceptions import AWSClientError
from shared.aws_clients.s3 import S3Client


def test_s3_client_initializes_local_url(monkeypatch):
    monkeypatch.setenv("AWS_MODE", "local")
    monkeypatch.setenv("LOCALSTACK_URL", "http://localhost:4566")

    client = S3Client()
    assert client.endpoint_url == "http://localhost:4566"


class _MotoS3Client:
    def __init__(self, client: Any) -> None:
        self._client = client

    async def __aenter__(self) -> "_MotoS3Client":
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        return None

    def put_object(self, **kwargs: Any) -> Any:
        return self._client.put_object(**kwargs)

    def get_object(self, **kwargs: Any) -> Any:
        response = self._client.get_object(**kwargs)
        return {"Body": response["Body"]}


@mock_aws
def test_s3_client_put_and_get_object_round_trip() -> None:
    """Putting an object should make it retrievable through the async client."""

    async def run_test() -> None:
        boto3_client = boto3.client("s3", region_name="us-east-1")
        boto3_client.create_bucket(Bucket="test-bucket")
        mock_client = _MotoS3Client(boto3_client)

        client = S3Client(region_name="us-east-1", mock_client=mock_client)
        await client.put_object("test-bucket", "demo.txt", b"hello moto", content_type="text/plain")
        retrieved = await client.get_object("test-bucket", "demo.txt")

        assert retrieved == b"hello moto"

    asyncio.run(run_test())


@mock_aws
def test_s3_client_raises_error_for_missing_object() -> None:
    """Missing objects should surface as AWSClientError from the wrapper."""

    async def run_test() -> None:
        boto3_client = boto3.client("s3", region_name="us-east-1")
        mock_client = _MotoS3Client(boto3_client)
        client = S3Client(region_name="us-east-1", mock_client=mock_client)

        with pytest.raises(AWSClientError):
            await client.get_object("missing-bucket", "missing-key")

    asyncio.run(run_test())
