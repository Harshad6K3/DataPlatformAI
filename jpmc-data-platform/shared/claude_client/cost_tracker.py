"""Track Claude API costs and emit CloudWatch metrics."""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import boto3

from .exceptions import BudgetExceededError
from .models import ClaudeCostRecord

logger = logging.getLogger("shared.claude_client.cost_tracker")

MODEL_PRICING = {
    "claude-haiku-4-5": {"input": 0.80 / 1_000_000, "output": 4.00 / 1_000_000},
    "claude-sonnet-4-6": {"input": 3.00 / 1_000_000, "output": 15.00 / 1_000_000},
}

# Sentinel — means no cap configured
_NO_CAP = float("inf")


class CostTracker:
    """Tracks Claude API costs per service per day and enforces a daily cap."""

    def __init__(
        self,
        namespace: Optional[str] = None,
        cloudwatch_client: Optional[Any] = None,
    ):
        self.namespace = namespace or "DataPlatform/ClaudeCosts"
        self.cloudwatch = cloudwatch_client or boto3.client("cloudwatch")
        self.daily_costs: Dict[str, float] = {}
        self.daily_reset = datetime.now(timezone.utc).date()
        self.daily_cap = self._read_cap()

    @staticmethod
    def _read_cap() -> float:
        """Read daily cap from env. Returns inf if not set or zero."""
        raw = os.getenv("CLAUDE_DAILY_COST_CAP_USD", "").strip()
        if not raw:
            return _NO_CAP
        try:
            val = float(raw)
            return val if val > 0 else _NO_CAP
        except ValueError:
            return _NO_CAP

    def _reset_if_needed(self) -> None:
        """Reset daily totals if the calendar date has changed."""
        today = datetime.now(timezone.utc).date()
        if today != self.daily_reset:
            self.daily_costs = {}
            self.daily_reset = today

    def track(self, record: ClaudeCostRecord) -> None:
        """Record a cost entry. Raises BudgetExceededError if cap is breached."""
        self._reset_if_needed()
        # Re-read cap each call so tests can set env var after construction
        self.daily_cap = self._read_cap()
        service_key = record.caller_service
        total = self.daily_costs.get(service_key, 0.0) + record.cost_usd
        self.daily_costs[service_key] = total

        if total > self.daily_cap:
            logger.error(
                "Claude daily cost cap exceeded",
                extra={
                    "caller_service": record.caller_service,
                    "total_cost": total,
                    "cap": self.daily_cap,
                },
            )
            raise BudgetExceededError(
                f"Daily cost cap of ${self.daily_cap} exceeded for "
                f"{record.caller_service} (current: ${total:.6f})"
            )

        self._emit_metric(record)

    def _emit_metric(self, record: ClaudeCostRecord) -> None:
        """Push cost metrics to CloudWatch. Failures are logged, not raised."""
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        "MetricName": "CostUsd",
                        "Value": record.cost_usd,
                        "Unit": "None",
                        "Dimensions": [
                            {"Name": "CallerService", "Value": record.caller_service},
                            {"Name": "Model", "Value": record.model},
                            {"Name": "UseCase", "Value": record.use_case},
                        ],
                    },
                    {
                        "MetricName": "InputTokens",
                        "Value": record.input_tokens,
                        "Unit": "Count",
                        "Dimensions": [
                            {"Name": "CallerService", "Value": record.caller_service},
                        ],
                    },
                    {
                        "MetricName": "OutputTokens",
                        "Value": record.output_tokens,
                        "Unit": "Count",
                        "Dimensions": [
                            {"Name": "CallerService", "Value": record.caller_service},
                        ],
                    },
                ],
            )
        except Exception as exc:
            logger.warning("Failed to publish cost metric", extra={"error": str(exc)})

    @staticmethod
    def pricing_for(model: str) -> Dict[str, float]:
        """Return per-token pricing for a given model."""
        return MODEL_PRICING.get(model, MODEL_PRICING["claude-sonnet-4-6"])

    def compute_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD for a given model and token counts."""
        pricing = self.pricing_for(model)
        return round(
            input_tokens * pricing["input"] + output_tokens * pricing["output"],
            8,
        )