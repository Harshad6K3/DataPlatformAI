"""Main Anthropic Claude client wrapper."""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Type

import httpx
from pydantic import BaseModel

from .agent_loop import AgentLoop
from .cache import PromptCache
from .cost_tracker import CostTracker
from .exceptions import BudgetExceededError, CircuitOpenError, ClaudeClientError
from .models import ClaudeCostRecord, SanitisationRecord
from .sanitiser import Sanitiser
from .structured_output import StructuredOutputHelper

logger = logging.getLogger("shared.claude_client.client")

RATE_LIMIT_STATUS = {429, 529}
SERVER_ERRORS = {500, 502, 503}


class ClaudeClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        caller_service: str = "unknown",
        use_case: str = "general",
        timeout: int = 30,
        cost_tracker: Optional[CostTracker] = None,
        sanitiser: Optional[Sanitiser] = None,
        prompt_cache: Optional[PromptCache] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY")
        self.base_url = os.getenv("CLAUDE_API_URL", "https://api.anthropic.com")
        self.caller_service = caller_service
        self.use_case = use_case
        self.timeout = min(timeout, 120)
        self.cost_tracker = cost_tracker or CostTracker()
        self.sanitiser = sanitiser or Sanitiser()
        self.prompt_cache = prompt_cache or PromptCache()
        self.structured_output_helper = StructuredOutputHelper(self)
        self.agent_loop = AgentLoop(self)
        self.http_client = http_client or httpx.AsyncClient(timeout=self.timeout)
        self.failure_count = 0
        self.circuit_open_until: Optional[datetime] = None

    async def complete(self, prompt: str, model: str = "claude-sonnet-4-6", sanitise: bool = True, **kwargs: Any) -> Dict[str, Any]:
        if self.circuit_open_until and datetime.utcnow() < self.circuit_open_until:
            raise CircuitOpenError("Circuit is open, skipping Claude call")

        text, sanitisation_record = self.sanitiser.sanitise(prompt, self.caller_service, self.use_case, sanitise)
        if sanitisation_record.rules_applied and not sanitisation_record.bypassed:
            logger.info({"event": "sanitisation", "rules_applied": sanitisation_record.rules_applied})

        system_message = {"type": "system", "content": text, "tokens": len(text.split())}
        self.prompt_cache.add_cache_control(system_message)

        request_payload = {
            "model": model,
            "messages": [system_message],
            **kwargs,
        }

        response = await self._execute_with_retries(request_payload)
        record = self._track_cost(model, response)
        self.cost_tracker.track(record)
        return response

    async def complete_structured(self, prompt: str, output_model: Type[BaseModel], retries: int = 2, sanitise: bool = True, **kwargs: Any) -> BaseModel:
        return await self.structured_output_helper.complete_structured(prompt, output_model, retries=retries, sanitise=sanitise, **kwargs)

    async def run_agent(self, system: str, messages: List[Dict[str, Any]], tools: Dict[str, Callable[..., Any]], tool_executor: Dict[str, Callable[..., Any]], max_iterations: int = 10, **kwargs: Any) -> Any:
        self.agent_loop.max_iterations = max_iterations
        return await self.agent_loop.run_agent(system, messages, tools, tool_executor, **kwargs)

    async def _execute_with_retries(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        attempt = 0
        while True:
            attempt += 1
            try:
                start = time.monotonic()
                response = await self.http_client.post(
                    f"{self.base_url}/v1/complete",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json=payload,
                )
                duration_ms = int((time.monotonic() - start) * 1000)
                status_code = response.status_code
                logger.info({"event": "claude_call", "status_code": status_code, "duration_ms": duration_ms, "attempt": attempt})
                if status_code < 300:
                    self.failure_count = 0
                    return response.json()
                if status_code in RATE_LIMIT_STATUS or status_code in SERVER_ERRORS:
                    raise ClaudeClientError(f"Retryable error {status_code}")
                raise ClaudeClientError(f"Non-retryable status {status_code}")
            except ClaudeClientError as exc:
                self.failure_count += 1
                if self.failure_count >= 5:
                    self.circuit_open_until = datetime.utcnow() + timedelta(seconds=60)
                    logger.warning("Circuit opened due to consecutive failures")
                if attempt >= 4 or status_code not in RATE_LIMIT_STATUS.union(SERVER_ERRORS):
                    raise
                await asyncio.sleep(2 ** (attempt - 1))
            except httpx.RequestError as exc:
                self.failure_count += 1
                if self.failure_count >= 5:
                    self.circuit_open_until = datetime.utcnow() + timedelta(seconds=60)
                if attempt >= 4:
                    raise ClaudeClientError("Request failed", exc)
                await asyncio.sleep(2 ** (attempt - 1))

    def _track_cost(self, model: str, response: Dict[str, Any]) -> ClaudeCostRecord:
        usage = response.get("usage", {})
        input_tokens = int(usage.get("input_tokens", 0))
        output_tokens = int(usage.get("output_tokens", 0))
        cost_usd = self.cost_tracker.compute_cost(model, input_tokens, output_tokens)
        cache_hit = response.get("usage", {}).get("cache_read_input_tokens", 0) > 0
        tokens_saved = int(response.get("usage", {}).get("cache_read_input_tokens", 0))
        cost_saved = self.cost_tracker.compute_cost(model, tokens_saved, 0)
        record = ClaudeCostRecord(
            timestamp=datetime.utcnow(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            caller_service=self.caller_service,
            use_case=self.use_case,
            cache_hit=cache_hit,
            tokens_saved=tokens_saved,
            cost_saved=cost_saved,
        )
        return record

    async def close(self) -> None:
        await self.http_client.aclose()
