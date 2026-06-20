"""Basic Glue client tests using local mock fixtures."""
import asyncio

import pytest

from shared.aws_clients.glue import GlueClient


@pytest.mark.asyncio
async def test_get_job_local_mode(tmp_path, monkeypatch):
    monkeypatch.setenv("AWS_MODE", "local")
    monkeypatch.setenv("LOCALSTACK_URL", "http://localhost:4566")

    client = GlueClient()
    response = await client.get_job("example")
    assert isinstance(response, dict)
