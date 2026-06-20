"""Basic S3 client tests."""
import pytest

from shared.aws_clients.s3 import S3Client


def test_s3_client_initializes_local_url(monkeypatch):
    monkeypatch.setenv("AWS_MODE", "local")
    monkeypatch.setenv("LOCALSTACK_URL", "http://localhost:4566")

    client = S3Client()
    assert client.endpoint_url == "http://localhost:4566"
