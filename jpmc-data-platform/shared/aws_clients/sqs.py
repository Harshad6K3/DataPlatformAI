"""Async SQS client wrapper."""

from __future__ import annotations

import json
import os
from typing import Any, Optional

from shared.aws_clients.base import BaseAWSClient


class SQSClient(BaseAWSClient):
    """Simple async wrapper around the boto3 SQS API."""

    def __init__(
        self,
        region_name: Optional[str] = None,
        role_arn: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        mock_client: Optional[Any] = None,
    ) -> None:
        if os.getenv("AWS_MODE") == "local":
            endpoint_url = endpoint_url or os.getenv("LOCALSTACK_URL", "http://localhost:4566")
        super().__init__("sqs", region_name, role_arn, endpoint_url, mock_client=mock_client)

    async def send_message(self, queue_url: str, body: dict[str, Any]) -> str:
        """Send a JSON-encoded message to SQS."""
        async with await self._get_client("sqs") as client:
            response = await self.execute(
                client.send_message,
                QueueUrl=queue_url,
                MessageBody=json.dumps(body),
            )
            return str(response.get("MessageId", ""))

    async def receive_messages(self, queue_url: str, max_messages: int = 10) -> list[dict[str, Any]]:
        """Receive up to max_messages from an SQS queue."""
        async with await self._get_client("sqs") as client:
            response = await self.execute(
                client.receive_message,
                QueueUrl=queue_url,
                MaxNumberOfMessages=max_messages,
            )
            return response.get("Messages", [])

    async def delete_message(self, queue_url: str, receipt_handle: str) -> None:
        """Delete a single SQS message."""
        async with await self._get_client("sqs") as client:
            await self.execute(
                client.delete_message,
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle,
            )
