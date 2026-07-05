# d:\DataPlatformAI\DataPlatformAI\jpmc-data-platform\shared\audit\sinks\stdout.py
"""Local development sink that writes structured audit events to stdout."""
from __future__ import annotations

import json
import logging
import sys
from typing import Any

from ..models import AuditEvent

logger = logging.getLogger("shared.audit.stdout")


class StdoutSink:
    """Emit audit events as structured JSON to stdout using the logging module."""

    def __init__(self) -> None:
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter("%(message)s"))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            logger.propagate = False

    async def write(self, event: AuditEvent) -> None:
        payload = event.model_dump(mode="json")
        logger.info(json.dumps(payload, default=str))

    async def log(self, event: Any) -> None:
        await self.write(event)
