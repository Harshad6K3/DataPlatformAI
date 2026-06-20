"""Tests for structured output helper."""
from pydantic import BaseModel

from shared.claude_client.structured_output import StructuredOutputHelper


class SampleModel(BaseModel):
    foo: str
    bar: int


class DummyClient:
    def __init__(self, response):
        self.response = response

    async def complete(self, prompt, **kwargs):
        return self.response


import pytest

@pytest.mark.asyncio
async def test_complete_structured_success():
    client = DummyClient({"completion": '{"foo": "hello", "bar": 1}'})
    helper = StructuredOutputHelper(client)
    result = await helper.complete_structured("prompt", SampleModel)
    assert result.foo == "hello"
    assert result.bar == 1
