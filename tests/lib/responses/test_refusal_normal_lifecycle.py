"""Same enabled refusal bar with a full item lifecycle, before done/terminal."""

import json
from copy import deepcopy

import pytest

from openai.lib.responses_websocket import ResponsesWebSocketAccumulator
from tests.lib.responses.test_websocket_session import session_for, script_server, response_event


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_known_refusal_normal_created_item_part_deltas(mode):
    frames = [
        response_event("created", output=None),
        {
            "type": "response.output_item.added",
            "sequence_number": 1,
            "output_index": 0,
            "item": {
                "type": "message",
                "id": "msg_fixture",
                "role": "assistant",
                "status": "in_progress",
                "content": [],
            },
        },
        {
            "type": "response.content_part.added",
            "sequence_number": 2,
            "output_index": 0,
            "content_index": 0,
            "item_id": "msg_fixture",
            "part": {"type": "refusal", "refusal": ""},
        },
        {
            "type": "response.refusal.delta",
            "sequence_number": 3,
            "output_index": 0,
            "content_index": 0,
            "item_id": "msg_fixture",
            "delta": "Cannot ",
        },
        {
            "type": "response.refusal.delta",
            "sequence_number": 4,
            "output_index": 0,
            "content_index": 0,
            "item_id": "msg_fixture",
            "delta": "do that",
        },
    ]

    def peer(socket):
        assert json.loads(socket.recv(timeout=4)) == {"type": "response.create", "input": "synthetic"}
        for f in frames:
            socket.send(json.dumps(f))
        # No done or terminal exists to repair the view under test.

    with script_server(peer) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "synthetic"})
            acc = ResponsesWebSocketAccumulator()
            observed = []
            for frame in frames[:3]:
                event = await driver.call(lane, "recv")
                original = deepcopy(event.to_dict(exclude_unset=True))
                assert original == frame
                acc.add_event(event)
                assert event.to_dict(exclude_unset=True) == original
                observed.append((event, original))
            prior = acc.detailed_snapshot()
            # Detailed item metadata excludes content, which is represented
            # once as the separate indexed content rows.
            assert prior["output"][0]["item"] == {
                "type": "message",
                "id": "msg_fixture",
                "role": "assistant",
                "status": "in_progress",
            }
            assert prior["output"][0]["content"][0]["part"] == {"type": "refusal", "refusal": ""}
            for frame in frames[3:]:
                event = await driver.call(lane, "recv")
                original = deepcopy(event.to_dict(exclude_unset=True))
                assert original == frame
                acc.add_event(event)
                observed.append((event, original))
            actual = acc.detailed_snapshot()
            assert all(event.to_dict(exclude_unset=True) == frame for event, frame in observed)
            assert prior["output"][0]["content"][0]["part"]["refusal"] == ""
            assert actual["output"][0]["content"][0]["part"]["refusal"] == "Cannot do that"


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_refusal_sparse_seed_done_and_unknown_part_compatibility(mode: str) -> None:
    pos = 2**63 + 31
    address = {"output_index": pos, "content_index": pos + 1, "item_id": "sparse"}
    frames = [
        {"type": "response.refusal.delta", **address, "delta": "provisional", "sequence_number": 1},
        {"type": "response.refusal.done", **address, "refusal": "fixed", "sequence_number": 2},
        {
            "type": "response.content_part.added",
            **address,
            "part": {"type": "refusal", "refusal": None},
            "sequence_number": 3,
        },
        {"type": "response.refusal.delta", **address, "delta": "cannot use malformed seed", "sequence_number": 4},
        {"type": "response.refusal.done", **address, "refusal": "final correction", "sequence_number": 5},
        {
            "type": "response.content_part.done",
            **address,
            "part": {"type": "future_part", "refusal": "caller-visible extra", "retained": [None, False]},
            "sequence_number": 6,
        },
        {"type": "response.refusal.delta", **address, "delta": "must not annotate another type", "sequence_number": 7},
    ]

    def peer(socket):
        assert json.loads(socket.recv(timeout=4)) == {"type": "response.create", "input": "synthetic"}
        for frame in frames:
            socket.send(json.dumps(frame))

    with script_server(peer) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "synthetic"})
            acc = ResponsesWebSocketAccumulator()
            acc.add_event(await driver.call(lane, "recv"))
            saved = acc.detailed_snapshot()
            assert saved["output"] == [
                {
                    "output_index": pos,
                    "item": {"id": "sparse"},
                    "content": [{"content_index": pos + 1, "part": {"refusal": "provisional"}}],
                }
            ]
            assert acc.snapshot().output_text == ""
            acc.add_event(await driver.call(lane, "recv"))
            assert acc.detailed_snapshot()["output"][0]["content"][0]["part"] == {"refusal": "fixed"}
            # Existing raw receipt accepted malformed parts before refusal deltas were supported.
            part_event = await driver.call(lane, "recv")
            before_raw = deepcopy(part_event.to_dict())
            acc.add_event(part_event)
            before = acc.detailed_snapshot()
            assert before["output"][0]["content"][0]["part"] == {"type": "refusal", "refusal": None}
            delta_event = await driver.call(lane, "recv")
            with pytest.raises(ValueError, match="refusal"):
                acc.add_event(delta_event)
            assert acc.detailed_snapshot() == before
            assert part_event.to_dict() == before_raw
            acc.add_event(await driver.call(lane, "recv"))
            assert acc.detailed_snapshot()["output"][0]["content"][0]["part"] == {
                "type": "refusal",
                "refusal": "final correction",
            }
            acc.add_event(await driver.call(lane, "recv"))
            future = acc.detailed_snapshot()
            assert future["output"][0]["content"][0]["part"] == {
                "type": "future_part",
                "refusal": "caller-visible extra",
                "retained": [None, False],
            }
            acc.add_event(await driver.call(lane, "recv"))
            assert acc.detailed_snapshot() == future
            assert saved["output"][0]["content"][0]["part"]["refusal"] == "provisional"
            assert acc.snapshot().output_text == ""
