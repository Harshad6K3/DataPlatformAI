"""Tests for Claude cost tracker."""
import os
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from shared.claude_client.cost_tracker import CostTracker
from shared.claude_client.exceptions import BudgetExceededError
from shared.claude_client.models import ClaudeCostRecord


class DummyCloudWatch:
    def put_metric_data(self, Namespace, MetricData):
        self.namespace = Namespace
        self.metric_data = MetricData


def test_compute_cost():
    tracker = CostTracker(cloudwatch_client=DummyCloudWatch())
    assert tracker.compute_cost("claude-haiku-4-5", 1000, 1000) == pytest.approx(0.0048)
    assert tracker.compute_cost("claude-sonnet-4-6", 1000, 1000) == pytest.approx(0.018)


def test_track_raises_budget_exceeded():
    os.environ["CLAUDE_DAILY_COST_CAP_USD"] = "0.00001"  # tiny cap
    try:
        tracker = CostTracker(cloudwatch_client=MagicMock())
        record = ClaudeCostRecord(
            model="claude-sonnet-4-6",
            input_tokens=10000,
            output_tokens=5000,
            cost_usd=0.10,  # way over cap
            timestamp=datetime.now(timezone.utc),
            caller_service="test-service",
            use_case="test",
            cached_tokens=0,
        )
        with pytest.raises(BudgetExceededError):
            tracker.track(record)
    finally:
        del os.environ["CLAUDE_DAILY_COST_CAP_USD"]  # always clean up