"""Structured output helper for Claude responses."""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Callable, Type

from pydantic import BaseModel, ValidationError

from .exceptions import StructuredOutputError

logger = logging.getLogger("shared.claude_client.structured_output")


class StructuredOutputHelper:
    def __init__(self, client: Any):
        self.client = client

    async def complete_structured(self, prompt: str, output_model: Type[BaseModel], retries: int = 2, **kwargs: Any) -> BaseModel:
        attempt = 0
        last_error: Exception | None = None
        while attempt <= retries:
            attempt += 1
            try:
                response = await self.client.complete(prompt, **kwargs)
                payload = self._extract_json(response)
                return output_model.parse_obj(payload)
            except (json.JSONDecodeError, ValidationError) as exc:
                logger.warning("Structured output parse/validation failed", extra={"attempt": attempt, "error": str(exc)})
                last_error = exc
        raise StructuredOutputError("Structured output failed after retries", last_error)

    @staticmethod
    def _extract_json(response: Any) -> Any:
        text = response["completion"] if isinstance(response, dict) else str(response)
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise json.JSONDecodeError("No JSON object", text, 0)
        return json.loads(text[start : end + 1])
