"""Agent loop helper for Claude tool use."""
from __future__ import annotations

import logging
import time
from typing import Any, Callable, Dict, List, Optional

from .exceptions import AgentMaxIterationsError

logger = logging.getLogger("shared.claude_client.agent_loop")


class AgentLoop:
    def __init__(self, client: Any, max_iterations: int = 10):
        self.client = client
        self.max_iterations = max_iterations

    async def run_agent(self, system: str, messages: List[Dict[str, Any]], tools: Dict[str, Callable[..., Any]], tool_executor: Dict[str, Callable[..., Any]], **kwargs: Any) -> Any:
        history = messages.copy()
        for iteration in range(1, self.max_iterations + 1):
            start = time.monotonic()
            response = await self.client.complete(system, history=history, **kwargs)
            duration_ms = int((time.monotonic() - start) * 1000)
            tool_name = self._extract_tool_name(response)
            logger.info({"iteration": iteration, "tool_name": tool_name, "duration_ms": duration_ms})
            if not tool_name or tool_name not in tool_executor:
                return response
            result = await tool_executor[tool_name](response)
            history.append({"role": "tool", "name": tool_name, "content": result})
        raise AgentMaxIterationsError("Max agent iterations reached")

    @staticmethod
    def _extract_tool_name(response: Any) -> Optional[str]:
        if isinstance(response, dict):
            return response.get("tool_name")
        return None
