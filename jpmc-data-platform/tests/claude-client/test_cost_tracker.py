"""Tests for Claude cost tracker."""
from datetime import datetime

import pytest

from shared.claude_client.cost_tracker import CostTracker
from shared.claude_client.models import ClaudeCostRecord


class DummyCloudWatch:
    def put_metric_data(self, Namespace, MetricData):
        self.namespace = Namespace
        self.metric_data = MetricData


def test_compute_cost():
    tracker = CostTracker(cloudwatch_client=DummyCloudWatch())
    assert tracker.compute_cost("claude-haiku-4-5", 1000, 1000) == pytest.approx(0.0048)
    assert tracker.compute_cost("claude-sonnet-4-6", 1000, 1000) == pytest.approx(0.018)


def test_track_raises_budget_exceeded(monkeypatch):
    client = DummyCloudWatch()
    tracker = CostTracker(cloudwatch_client=client)
    monkeypatch.setenv("CLAUDE_DAILY_COST_CAP_USD", "0.000001")
    record = ClaudeCostRecord(
        timestamp=datetime.utcnow(),
        model="claude-sonnet-4-6",
        input_tokens=1000,
        output_tokens=1000,
        cost_usd=0.018,
        caller_service="svc",
        use_case="test",
    )
    with pytest.raises(Exception):
        tracker.track(record)
