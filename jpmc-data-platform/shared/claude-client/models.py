"""Pydantic schemas for Claude client tracking."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class ClaudeCostRecord(BaseModel):
    timestamp: datetime
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    caller_service: str
    use_case: str
    cache_hit: bool = False
    tokens_saved: int = 0
    cost_saved: float = 0.0


class SanitisationRecord(BaseModel):
    timestamp: datetime
    caller_service: str
    use_case: str
    rules_applied: Dict[str, int]
    bypassed: bool = False
