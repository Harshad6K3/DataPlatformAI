"""Async CloudWatch Logs client wrapper."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import BaseAWSClient


class CloudWatchLogsClient(BaseAWSClient):
    def __init__(
        self,
        region_name: Optional[str] = None,
        role_arn: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        mock_client: Optional[Any] = None,
    ):
        super().__init__("logs", region_name, role_arn, endpoint_url, mock_client=mock_client)

    async def get_log_events(self, log_group_name: str, log_stream_name: str, **kwargs: Any) -> Dict[str, Any]:
        async with await self._get_client("logs") as client:
            return await self._retry(client.get_log_events, "get_log_events", logGroupName=log_group_name, logStreamName=log_stream_name, **kwargs)

    async def start_query(self, log_group_name: str, query_string: str, start_time: int, end_time: int, **kwargs: Any) -> Dict[str, Any]:
        async with await self._get_client("logs") as client:
            return await self._retry(client.start_query, "start_query", logGroupName=log_group_name, queryString=query_string, startTime=start_time, endTime=end_time, **kwargs)

    async def get_query_results(self, query_id: str) -> Dict[str, Any]:
        async with await self._get_client("logs") as client:
            return await self._retry(client.get_query_results, "get_query_results", queryId=query_id)

    async def put_log_events(self, log_group_name: str, log_stream_name: str, log_events: List[Dict[str, Any]], sequence_token: Optional[str] = None) -> Dict[str, Any]:
        params = {"logGroupName": log_group_name, "logStreamName": log_stream_name, "logEvents": log_events}
        if sequence_token:
            params["sequenceToken"] = sequence_token
        async with await self._get_client("logs") as client:
            return await self._retry(client.put_log_events, "put_log_events", **params)
