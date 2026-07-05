"""S3 sink that batches audit events into gzipped NDJSON."""
from __future__ import annotations

import asyncio
import gzip
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import boto3

logger = logging.getLogger("shared.audit.s3")


class S3Sink:
    def __init__(self, bucket: str, service_name: str, batch_interval_seconds: int = 300):
        self.bucket = bucket
        self.service_name = service_name
        self.batch_interval_seconds = batch_interval_seconds
        self.events: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()
        self._upload_task: Optional[asyncio.Task] = None
        self.client = boto3.client("s3")

    async def log(self, event: Any) -> None:
        if self._upload_task is None:
            self._upload_task = asyncio.create_task(self._periodic_flush())
        async with self._lock:
            self.events.append(json.loads(event.model_dump_json()))

    async def _periodic_flush(self) -> None:
        while True:
            await asyncio.sleep(self.batch_interval_seconds)
            await self.flush()

    async def flush(self) -> None:
        async with self._lock:
            if not self.events:
                return
            now = datetime.utcnow()
            key = f"{self._prefix(now)}events-{int(now.timestamp())}.ndjson.gz"
            body = "".join(json.dumps(evt) + "\n" for evt in self.events).encode("utf-8")
            compressed = gzip.compress(body)
            self.client.put_object(Bucket=self.bucket, Key=key, Body=compressed)
            self.events = []

    def _prefix(self, timestamp: datetime) -> str:
        return (
            f"service={self.service_name}/"
            f"year={timestamp.year}/month={timestamp.month:02d}/day={timestamp.day:02d}/"
        )
