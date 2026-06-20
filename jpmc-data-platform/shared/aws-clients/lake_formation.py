"""Async Lake Formation client wrapper."""
from __future__ import annotations

from typing import Any, Dict, Optional

from .base import BaseAWSClient


class LakeFormationClient(BaseAWSClient):
    def __init__(
        self,
        region_name: Optional[str] = None,
        role_arn: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        mock_client: Optional[Any] = None,
    ):
        super().__init__("lakeformation", region_name, role_arn, endpoint_url, mock_client=mock_client)

    async def get_data_access(self, principal: Dict[str, Any], catalog_id: Optional[str] = None) -> Dict[str, Any]:
        async with await self._get_client("lakeformation") as client:
            return await self._retry(client.get_data_access, "get_data_access", CatalogId=catalog_id, Principal=principal)

    async def list_permissions(self, catalog_id: Optional[str] = None, principal: Optional[Dict[str, Any]] = None, resource_type: Optional[str] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if catalog_id:
            params["CatalogId"] = catalog_id
        if principal:
            params["Principal"] = principal
        if resource_type:
            params["ResourceType"] = resource_type
        async with await self._get_client("lakeformation") as client:
            return await self._retry(client.list_permissions, "list_permissions", **params)

    async def get_effective_permissions_for_path(self, catalog_id: str, resource_arn: str) -> Dict[str, Any]:
        async with await self._get_client("lakeformation") as client:
            return await self._retry(client.get_effective_permissions_for_path, "get_effective_permissions_for_path", CatalogId=catalog_id, ResourceArn=resource_arn)
