from __future__ import annotations

import json
from typing import Any, cast

import pytest

from openai.types.responses import ResponseCustomToolCall, ResponseFunctionToolCall, ResponseOutputItemDoneEvent
from openai.resources.responses.responses import ResponsesConnection, AsyncResponsesConnection


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("status", ["completed", "future_status"])
@pytest.mark.parametrize("collision", [False, True])
@pytest.mark.parametrize("kind", ["function_call", "custom_tool_call"])
def test_validated_and_future_output_items_keep_wire_alias(mode: str, status: str, collision: bool, kind: str) -> None:
    item: dict[str, Any] = {
        "type": kind,
        "id": "call_1",
        "name": "lookup",
        "call_id": "tool_1",
        "status": status,
        "async": True,
        "unknown_future": {"nested": [1, 2]},
    }
    item["arguments" if kind == "function_call" else "input"] = "{}"
    if collision:
        item["async_"] = "unrelated future spelling"
    payload = json.dumps({"type": "response.output_item.done", "sequence_number": 1, "output_index": 0, "item": item})
    if mode == "sync":
        connection = object.__new__(ResponsesConnection)
    else:
        connection = object.__new__(AsyncResponsesConnection)
    event = connection.parse_event(payload)
    assert isinstance(event, ResponseOutputItemDoneEvent)
    assert isinstance(event.item, (ResponseCustomToolCall, ResponseFunctionToolCall))
    assert event.item.async_ is True
    assert cast(Any, event.item).unknown_future == {"nested": [1, 2]}
    emitted = event.item.to_dict()
    assert emitted["async"] is True
    assert emitted["unknown_future"] == {"nested": [1, 2]}
