"""Compatibility Glue client wrapper for tests and local development."""

from __future__ import annotations

import os
from typing import Any, Optional

from shared.aws_clients.base import BaseAWSClient


class GlueClient(BaseAWSClient):
    """Minimal async wrapper around the Glue API."""

    def __init__(
        self,
        region_name: Optional[str] = None,
        role_arn: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        mock_client: Optional[Any] = None,
    ) -> None:
        if os.getenv("AWS_MODE") == "local":
            endpoint_url = endpoint_url or os.getenv("LOCALSTACK_URL", "http://localhost:4566")
        super().__init__("glue", region_name, role_arn, endpoint_url, mock_client=mock_client)

    async def get_job(self, job_name: str) -> dict[str, Any]:
        """Return a basic job payload for local development."""
        return {"JobName": job_name, "Command": {"Name": "glueetl"}}
