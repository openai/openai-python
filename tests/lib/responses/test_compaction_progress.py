from __future__ import annotations

import json
from unittest.mock import Mock, AsyncMock

import pytest

from openai._types import omit
from openai._models import construct_type_unchecked
from openai.types.beta import BetaResponseCompactionCompactingEvent
from openai.types.responses import ResponseCreatedEvent, ResponseCompactionCompactingEvent
from openai.resources.responses import responses
from openai.resources.beta.responses import responses as beta_responses
from openai.lib.streaming.responses._responses import ResponseStreamState

from .test_null_output_items import _consume


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("progress_count", [0, 2], ids=["absent", "repeated"])
async def test_compaction_stream_preserves_progress_and_final_output(sync: bool, progress_count: int) -> None:
    item = {"id": "cmp_test", "type": "compaction", "encrypted_content": ""}
    final_item = {**item, "encrypted_content": "fake-encrypted-summary"}
    events: list[dict[str, object]] = [
        {"type": "response.created", "response": {"id": "resp_test", "output": []}},
        {"type": "response.output_item.added", "output_index": 0, "item": item},
        *[
            {"type": "response.compaction.compacting", "item_id": "cmp_test", "output_index": 0}
            for _ in range(progress_count)
        ],
        {"type": "response.output_item.done", "output_index": 0, "item": final_item},
        # Recover the completed item from its lifecycle event, not a duplicate final payload.
        {"type": "response.completed", "response": {"id": "resp_test", "status": "completed"}},
    ]

    emitted, final = await _consume(sync, events)

    assert [event.type for event in emitted] == [event["type"] for event in events]
    progress = [event for event in emitted if event.type == "response.compaction.compacting"]
    assert len(progress) == progress_count
    for index, event in enumerate(progress, start=2):
        assert isinstance(event, ResponseCompactionCompactingEvent)
        assert (event.item_id, event.output_index, event.sequence_number) == ("cmp_test", 0, index)
    assert len(final.output) == 1
    assert final.output[0].to_dict() == final_item


def test_compaction_progress_leaves_accumulated_snapshot_unchanged() -> None:
    state: ResponseStreamState[None] = ResponseStreamState(text_format=omit, input_tools=[])
    created = construct_type_unchecked(
        type_=ResponseCreatedEvent,
        value={
            "type": "response.created",
            "sequence_number": 0,
            "response": {
                "id": "resp_test",
                "output": [{"id": "cmp_test", "type": "compaction", "encrypted_content": ""}],
            },
        },
    )
    state.handle_event(created)
    snapshot = state.accumulate_event(created)
    before = snapshot.to_dict()
    for sequence_number in (1, 2):
        progress = ResponseCompactionCompactingEvent(
            type="response.compaction.compacting", item_id="cmp_test", output_index=0, sequence_number=sequence_number
        )
        assert state.handle_event(progress) == [progress]
        assert state.accumulate_event(progress) is snapshot
        assert snapshot.to_dict() == before


@pytest.mark.parametrize("beta", [False, True], ids=["stable", "beta"])
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_websocket_receives_typed_compaction_progress(beta: bool, sync: bool) -> None:
    api = beta_responses if beta else responses
    frames: list[dict[str, object]] = [
        {"type": "response.compaction.compacting", "item_id": "cmp_test", "output_index": 0, "sequence_number": index}
        for index in (1, 2)
    ]
    if beta:
        frames[1]["agent"] = {"agent_name": "test-agent"}
    socket = Mock()
    socket.recv = (Mock if sync else AsyncMock)(side_effect=[json.dumps(frame).encode() for frame in frames])
    if sync:
        connection = api.ResponsesConnection(socket)
        received = [connection.recv(), connection.recv()]
    else:
        async_connection = api.AsyncResponsesConnection(socket)
        received = [await async_connection.recv(), await async_connection.recv()]

    for event, frame in zip(received, frames, strict=True):
        assert isinstance(event, BetaResponseCompactionCompactingEvent if beta else ResponseCompactionCompactingEvent)
        assert event.type == "response.compaction.compacting"
        assert (event.item_id, event.output_index, event.sequence_number) == ("cmp_test", 0, frame["sequence_number"])
        assert event.to_dict() == frame
