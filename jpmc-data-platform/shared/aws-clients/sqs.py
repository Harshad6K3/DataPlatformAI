"""Async SQS client wrapper."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import BaseAWSClient


class SQSClient(BaseAWSClient):
    def __init__(
        self,
        region_name: Optional[str] = None,
        role_arn: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        mock_client: Optional[Any] = None,
    ):
        if os.getenv("AWS_MODE") == "local":
            endpoint_url = endpoint_url or os.getenv("LOCALSTACK_URL")
        super().__init__("sqs", region_name, role_arn, endpoint_url, mock_client=mock_client)

    async def send_message(self, queue_url: str, message_body: str, **kwargs: Any) -> Dict[str, Any]:
        async with await self._get_client("sqs") as client:
            return await self._retry(client.send_message, "send_message", QueueUrl=queue_url, MessageBody=message_body, **kwargs)

    async def receive_messages(self, queue_url: str, max_number_of_messages: int = 1, **kwargs: Any) -> Dict[str, Any]:
        async with await self._get_client("sqs") as client:
            return await self._retry(client.receive_message, "receive_messages", QueueUrl=queue_url, MaxNumberOfMessages=max_number_of_messages, **kwargs)

    async def delete_message(self, queue_url: str, receipt_handle: str) -> Dict[str, Any]:
        async with await self._get_client("sqs") as client:
            return await self._retry(client.delete_message, "delete_message", QueueUrl=queue_url, ReceiptHandle=receipt_handle)

    async def send_message_batch(self, queue_url: str, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        async with await self._get_client("sqs") as client:
            return await self._retry(client.send_message_batch, "send_message_batch", QueueUrl=queue_url, Entries=entries)
