"""Async Glue client wrapper."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from .base import BaseAWSClient
from .exceptions import AWSClientError


class GlueClient(BaseAWSClient):
    def __init__(
        self,
        region_name: Optional[str] = None,
        role_arn: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        mock_client: Optional[Any] = None,
    ):
        if os.getenv("AWS_MODE") == "local":
            endpoint_url = endpoint_url or os.getenv("LOCALSTACK_URL")
        super().__init__("glue", region_name, role_arn, endpoint_url, mock_client=mock_client)

    async def _load_fixture(self, name: str) -> Any:
        path = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "glue", f"{name}.json")
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    async def get_job(self, job_name: str) -> Dict[str, Any]:
        if os.getenv("AWS_MODE") == "local":
            return await self._load_fixture("get_job")
        async with await self._get_client("glue") as client:
            return await self._retry(client.get_job, "get_job", JobName=job_name)

    async def get_job_run(self, job_name: str, run_id: str) -> Dict[str, Any]:
        if os.getenv("AWS_MODE") == "local":
            return await self._load_fixture("get_job_run")
        async with await self._get_client("glue") as client:
            return await self._retry(client.get_job_run, "get_job_run", JobName=job_name, RunId=run_id)

    async def list_jobs(self) -> Dict[str, Any]:
        if os.getenv("AWS_MODE") == "local":
            return await self._load_fixture("list_jobs")
        async with await self._get_client("glue") as client:
            return await self._retry(client.get_jobs, "list_jobs")

    async def get_tables(self, database_name: str, catalog_id: Optional[str] = None) -> Dict[str, Any]:
        async with await self._get_client("glue") as client:
            return await self._retry(client.get_tables, "get_tables", DatabaseName=database_name, CatalogId=catalog_id)

    async def get_databases(self, catalog_id: Optional[str] = None) -> Dict[str, Any]:
        async with await self._get_client("glue") as client:
            return await self._retry(client.get_databases, "get_databases", CatalogId=catalog_id)

    async def search_tables(self, search_text: str, catalog_id: Optional[str] = None) -> Dict[str, Any]:
        async with await self._get_client("glue") as client:
            return await self._retry(client.search_tables, "search_tables", SearchText=search_text, CatalogId=catalog_id)
