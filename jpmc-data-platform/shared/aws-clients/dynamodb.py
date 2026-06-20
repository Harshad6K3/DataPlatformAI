"""Async DynamoDB client wrapper."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import BaseAWSClient


class DynamoDBClient(BaseAWSClient):
    def __init__(
        self,
        region_name: Optional[str] = None,
        role_arn: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        mock_client: Optional[Any] = None,
    ):
        if os.getenv("AWS_MODE") == "local":
            endpoint_url = endpoint_url or os.getenv("DYNAMODB_LOCAL_URL")
        super().__init__("dynamodb", region_name, role_arn, endpoint_url, mock_client=mock_client)

    async def put_item(self, table_name: str, item: Dict[str, Any]) -> Dict[str, Any]:
        async with await self._get_client("dynamodb") as client:
            return await self._retry(client.put_item, "put_item", TableName=table_name, Item=item)

    async def get_item(self, table_name: str, key: Dict[str, Any]) -> Dict[str, Any]:
        async with await self._get_client("dynamodb") as client:
            return await self._retry(client.get_item, "get_item", TableName=table_name, Key=key)

    async def query(self, table_name: str, key_condition_expression: Any, expression_attribute_values: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        async with await self._get_client("dynamodb") as client:
            return await self._retry(
                client.query,
                "query",
                TableName=table_name,
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values,
                **kwargs,
            )

    async def batch_write(self, table_name: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        async with await self._get_client("dynamodb") as client:
            chunks = [items[i : i + 25] for i in range(0, len(items), 25)]
            unprocessed: List[Dict[str, Any]] = []
            for chunk in chunks:
                request_items = {table_name: [{"PutRequest": {"Item": item}} for item in chunk]}
                response = await self._retry(client.batch_write_item, "batch_write", RequestItems=request_items)
                unprocessed.extend(response.get("UnprocessedItems", {}).get(table_name, []))
            return {"UnprocessedItems": unprocessed}
