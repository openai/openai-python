import asyncio
import pytest
from dataclasses import dataclass

pytestmark = pytest.mark.asyncio

def test_pytest_collection_sanity():
    assert True

@dataclass
class _SSE:
    event: str
    data: dict

class _FakeStream:
    def __init__(self, events):
        self._events = events

    def __aiter__(self):
        self._it = iter(self._events)
        return self

    async def __anext__(self):
        try:
            await asyncio.sleep(0)
            return next(self._it)
        except StopIteration:
            raise StopAsyncIteration

def _mk_events_ok():
    return [
        _SSE("response.created", {"id": "resp_1", "type": "response", "model": "gpt-4o-mini"}),
        _SSE("response.output_text.created", {"index": 0, "id": "txt_1"}),
        _SSE("response.output_text.delta", {"index": 0, "value": "Hello, "}),
        _SSE("response.output_text.delta", {"index": 0, "value": "world!"}),
        _SSE("response.completed", {"id": "resp_1", "status": "ok"}),
    ]

async def _consume(stream):
    seen = []
    buffers = {}
    async for ev in stream:
        seen.append(ev.event)
        if ev.event == "response.output_text.delta":
            idx = ev.data.get("index", 0)
            buffers[idx] = buffers.get(idx, "") + ev.data.get("value", "")
    return seen, buffers.get(0, "")

async def test_unified_happy_path_harness():
    seen, text = await _consume(_FakeStream(_mk_events_ok()))
    assert seen == [
        "response.created",
        "response.output_text.created",
        "response.output_text.delta",
        "response.output_text.delta",
        "response.completed",
    ]
    assert text == "Hello, world!"

@pytest.mark.parametrize("missing", [
    "response.created",
    "response.output_text.created",
    "response.completed",
])
async def test_unified_resilience_harness(missing):
    base = _mk_events_ok()
    filtered = [e for e in base if e.event != missing]
    seen, text = await _consume(_FakeStream(filtered))
    assert missing not in seen
    assert isinstance(text, str)
