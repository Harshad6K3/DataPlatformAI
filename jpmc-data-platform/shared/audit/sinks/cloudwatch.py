"""CloudWatch sink for structured audit events."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import boto3


logger = logging.getLogger("shared.audit.cloudwatch")


class CloudWatchSink:
    def __init__(self, log_group: str, service_name: str):
        self.log_group = log_group
        self.service_name = service_name
        self.client = boto3.client("logs")

    def _stream_name(self) -> str:
        return f"{self.service_name}-{datetime.utcnow().date().isoformat()}"

    async def log(self, event: Any) -> None:
        message = event.json()
        try:
            self.client.create_log_group(logGroupName=self.log_group)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass
        stream_name = self._stream_name()
        try:
            self.client.create_log_stream(logGroupName=self.log_group, logStreamName=stream_name)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass
        sequence_token = None
        try:
            response = self.client.describe_log_streams(logGroupName=self.log_group, logStreamNamePrefix=stream_name)
            streams = response.get("logStreams", [])
            if streams and "uploadSequenceToken" in streams[0]:
                sequence_token = streams[0]["uploadSequenceToken"]
        except Exception as exc:
            logger.warning("Unable to describe log streams: %s", exc)
        put_kwargs = {
            "logGroupName": self.log_group,
            "logStreamName": stream_name,
            "logEvents": [{"timestamp": int(datetime.utcnow().timestamp() * 1000), "message": message}],
        }
        if sequence_token:
            put_kwargs["sequenceToken"] = sequence_token
        self.client.put_log_events(**put_kwargs)
