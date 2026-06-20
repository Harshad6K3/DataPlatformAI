"""Local development sink that writes structured audit events to stdout."""
from __future__ import annotations

import sys
from typing import Any


class StdoutSink:
    async def log(self, event: Any) -> None:
        sys.stdout.write(event.json() + "\n")
        sys.stdout.flush()
