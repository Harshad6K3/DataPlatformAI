"""Prompt cache implementation for Claude system prompts."""
from __future__ import annotations

from typing import Any, Dict


class PromptCache:
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}

    def get(self, prompt_id: str) -> Dict[str, Any]:
        return self.cache.get(prompt_id, {})

    def set(self, prompt_id: str, payload: Dict[str, Any]) -> None:
        self.cache[prompt_id] = payload

    def add_cache_control(self, message: Dict[str, Any]) -> None:
        if message.get("type") == "system" and message.get("tokens", 0) >= 1024:
            message["cache_control"] = {"type": "ephemeral"}
