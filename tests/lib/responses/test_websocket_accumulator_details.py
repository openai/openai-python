from __future__ import annotations

import sys
import json
from copy import deepcopy

import pytest
from websockets.sync.server import ServerConnection

from openai.lib.responses_websocket import ResponsesWebSocketAccumulator

from .test_websocket_session import session_for, script_server, response_event


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_partial_details_over_the_wire_preserve_metadata_and_typed_logprobs(mode: str) -> None:
    # WS delta logprobs legitimately have no 'bytes'. Never manufacture a
    # ResponseOutputText (its final Logprob requires bytes/top_logprobs).
    pos = sys.hash_info.modulus * 3
    delta = {
        "type": "response.output_text.delta",
        "output_index": pos,
        "content_index": pos + 1,
        "item_id": "msg_fixture",
        "delta": "h",
        "logprobs": [{"token": "h", "logprob": -0.3, "extra_fixture": [1]}],
    }
    frames = [
        response_event("created", output=None, metadata={"fixture": "before"}, model="fixture-model"),
        delta,
        {**delta, "delta": "i", "logprobs": [{"token": "i", "logprob": -0.4, "top_logprobs": None}]},
        {
            "type": "response.output_text.annotation.added",
            "output_index": pos,
            "content_index": pos + 1,
            "item_id": "msg_fixture",
            "annotation_index": pos + 2,
            "annotation": {
                "type": "url_citation",
                "title": "fixture",
                "url": "https://example.com/fixture",
                "start_index": 0,
                "end_index": 2,
                "extra_fixture": {"known": False},
            },
        },
        {
            "type": "response.output_text.done",
            "output_index": pos,
            "content_index": pos + 1,
            "item_id": "msg_fixture",
            "text": "corrected",
            "logprobs": [{"token": "corrected", "logprob": -0.2}],
        },
        response_event("incomplete", output=None, metadata={"fixture": "after"}),
    ]

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        for frame in frames:
            socket.send(json.dumps(frame))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "synthetic fixture"})
            acc = ResponsesWebSocketAccumulator()
            for _ in range(4):
                event = await driver.call(lane, "recv")
                original = deepcopy(event.to_dict())
                acc.add_event(event)
                assert event.to_dict() == original
            frozen = acc.snapshot()
            frozen_hash = hash(frozen)
            saved = acc.detailed_snapshot()
            row = saved["output"][0]
            assert saved["response"]["metadata"] == {"fixture": "before"}
            assert saved["response"]["model"] == "fixture-model"
            assert "output" not in saved["response"]
            assert row["output_index"] == pos and row["item"]["id"] == "msg_fixture"
            assert "type" not in row["item"]  # Missing setup never fabricates a type.
            assert row["content"][0]["content_index"] == pos + 1
            part = row["content"][0]["part"]
            assert part["text"] == "hi"
            assert part["logprobs"] == [
                {"token": "h", "logprob": -0.3, "extra_fixture": [1]},
                {"token": "i", "logprob": -0.4, "top_logprobs": None},
            ]
            assert part["annotations"] == [{"annotation_index": pos + 2, "annotation": frames[3]["annotation"]}]
            untouched = deepcopy(saved)
            # Both received events and returned mutable snapshots may be freely
            # changed without damaging later progress or old frozen snapshots.
            saved["response"]["metadata"]["fixture"] = "caller"
            part["logprobs"][0]["extra_fixture"].append(99)
            part["annotations"][0]["annotation"]["extra_fixture"]["known"] = True
            assert acc.detailed_snapshot() == untouched
            acc.add_event(await driver.call(lane, "recv"))
            detailed = acc.detailed_snapshot()
            part = detailed["output"][0]["content"][0]["part"]
            assert part["text"] == "corrected"
            assert part["logprobs"] == [{"token": "corrected", "logprob": -0.2}]
            assert part["annotations"] == untouched["output"][0]["content"][0]["part"]["annotations"]
            terminal = await driver.call(lane, "recv")
            acc.add_event(terminal)
            assert acc.detailed_snapshot()["response"]["metadata"] == {"fixture": "after"}
            assert acc.detailed_snapshot()["terminal_type"] == "response.incomplete"
            assert acc.get_final_response().to_dict() == terminal.response.to_dict()
            assert acc.snapshot().output_text == "corrected"
            assert frozen.output_text == "hi" and hash(frozen) == frozen_hash
            acc.reset()
            assert not acc.detailed_snapshot()["output"]
            assert acc.detailed_snapshot()["response"] is None
            assert untouched["response"]["metadata"] == {"fixture": "before"}


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_details_replaced_at_part_item_and_response_boundaries(mode: str) -> None:
    pos = sys.hash_info.modulus
    fixture_parts: list[dict[str, object]] = [
        {"type": "output_text", "text": "first", "annotations": [], "logprobs": None},
        {"type": "refusal", "refusal": "fixture refusal"},
        {"type": "future_fixture_part", "raw_fixture": [True]},
    ]
    message: dict[str, object] = {
        "id": "fixture",
        "type": "message",
        "role": "assistant",
        "status": "in_progress",
        "source_note": {"fixture": [1]},
        "content": fixture_parts,
    }
    replacement = {
        "type": "mcp_call",
        "id": "fixture_new",
        "name": "search",
        "arguments": "{}",
        "server_label": "fixture_server",
        "call_id": "fixture_call",
        "output": None,
        "error": None,
    }
    frames: list[dict[str, object]] = [
        {"type": "response.output_item.added", "output_index": pos, "item": message},
        {
            "type": "response.output_text.annotation.added",
            "output_index": pos,
            "content_index": 0,
            "item_id": "fixture",
            "annotation_index": pos,
            "annotation": {"type": "future_fixture_citation", "raw_fixture": [1]},
        },
        {
            "type": "response.content_part.done",
            "output_index": pos,
            "content_index": 0,
            "item_id": "fixture",
            "part": {"type": "output_text", "text": "final", "annotations": [], "logprobs": []},
        },
        {"type": "response.output_item.done", "output_index": pos, "item": replacement},
        {
            "type": "response.output_text.annotation.added",
            "output_index": pos,
            "content_index": 0,
            "item_id": "fixture",
            "annotation_index": 0,
            "annotation": None,
        },
        response_event("completed", output=[]),
    ]

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        for frame in frames:
            socket.send(json.dumps(frame))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "synthetic fixture"})
            acc = ResponsesWebSocketAccumulator()
            acc.add_event(await driver.call(lane, "recv"))
            first = acc.detailed_snapshot()
            out = first["output"][0]
            assert out["item"] == {k: v for k, v in message.items() if k != "content"}
            assert [row["part"] for row in out["content"]] == message["content"]
            assert out["content"][0]["part"]["logprobs"] is None
            acc.add_event(await driver.call(lane, "recv"))
            assert len(acc.detailed_snapshot()["output"][0]["content"][0]["part"]["annotations"]) == 1
            acc.add_event(await driver.call(lane, "recv"))
            parts = acc.detailed_snapshot()["output"][0]["content"]
            assert [row["part"] for row in parts] == [frames[2]["part"], *fixture_parts[1:]]
            assert first["output"][0]["content"][0]["part"]["text"] == "first"
            acc.add_event(await driver.call(lane, "recv"))
            saved = acc.detailed_snapshot()
            assert saved["output"] == [{"output_index": pos, "item": replacement, "content": []}]
            # A retired item's late annotation cannot replace the new item.
            acc.add_event(await driver.call(lane, "recv"))
            assert acc.detailed_snapshot() == saved
            terminal = await driver.call(lane, "recv")
            acc.add_event(terminal)
            assert acc.detailed_snapshot()["output"] == []
            assert acc.get_final_response().to_dict() == terminal.response.to_dict()


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("bad_position", [None, -1, False, "fixture-invalid"])
async def test_malformed_new_annotation_does_not_break_old_projection_or_retire_item(
    mode: str, bad_position: object
) -> None:
    delta = {
        "type": "response.output_text.delta",
        "output_index": 0,
        "content_index": 0,
        "item_id": "fixture",
        "delta": "ok",
    }

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        for event in [
            delta,
            {
                "type": "response.output_text.annotation.added",
                "output_index": 0,
                "content_index": 0,
                "item_id": "replacement",
                "annotation_index": bad_position,
                "annotation": {"type": "future_fixture_annotation"},
            },
            {**delta, "delta": " next"},
            response_event("completed", output=None),
        ]:
            socket.send(json.dumps(event))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "synthetic fixture"})
            acc = ResponsesWebSocketAccumulator()
            acc.add_event(await driver.call(lane, "recv"))
            prior = acc.detailed_snapshot()
            event = await driver.call(lane, "recv")
            # Even if Pydantic normalizes false to 0, this other item's
            # annotation cannot replace the original or end its progress.
            acc.add_event(event)
            assert acc.detailed_snapshot() == prior
            acc.add_event(await driver.call(lane, "recv"))
            assert acc.snapshot().output_text == "ok next"
            acc.add_event(await driver.call(lane, "recv"))
            assert acc.get_final_response().status == "completed"


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_unknown_full_items_keep_their_content_field_and_never_become_final(mode: str) -> None:
    future = {
        "type": "future_fixture_item",
        "id": "fixture_future",
        "content": {"shape": ["not", "a", "message"], "value": None},
    }

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(json.dumps({"type": "response.output_item.done", "output_index": 3, "item": future}))
        socket.close()

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "synthetic fixture"})
            acc = ResponsesWebSocketAccumulator()
            acc.add_event(await driver.call(lane, "recv"))
            assert acc.detailed_snapshot()["output"] == [{"output_index": 3, "item": future, "content": []}]
            with pytest.raises(EOFError):
                await driver.call(lane, "recv")
            with pytest.raises(RuntimeError, match="No terminal"):
                acc.get_final_response()
            assert acc.detailed_snapshot()["terminal_type"] is None


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("annotation_first", [False, True])
async def test_annotation_cannot_start_a_turn_or_retire_an_unrelated_item(mode: str, annotation_first: bool) -> None:
    delta = {
        "type": "response.output_text.delta",
        "output_index": 0,
        "content_index": 0,
        "item_id": "fixture_original",
        "delta": "kept",
    }
    annotation: dict[str, object] = {
        "type": "response.output_text.annotation.added",
        "output_index": 0,
        "content_index": 0,
        "annotation_index": 0,
        "item_id": "fixture_other",
    }
    if annotation_first:
        annotation["stream_id"] = "unregistered"
        annotation["annotation"] = {"type": "future_fixture"}

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        for event in [annotation, delta] if annotation_first else [delta, annotation]:
            socket.send(json.dumps(event))
        socket.send(json.dumps({**delta, "delta": " more"}))
        socket.send(json.dumps(response_event("completed", output=None)))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "synthetic fixture"})
            acc = ResponsesWebSocketAccumulator()
            for _ in range(3):
                acc.add_event(await driver.call(lane, "recv"))
            assert acc.snapshot().output_text == "kept more"
            assert acc.detailed_snapshot()["output"][0]["item"]["id"] == "fixture_original"
            assert "annotations" not in acc.detailed_snapshot()["output"][0]["content"][0]["part"]
            acc.add_event(await driver.call(lane, "recv"))
            assert acc.get_final_response().status == "completed"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("content_case", ["missing", "null", "empty"])
async def test_message_content_presence_preserved_before_terminal(mode: str, content_case: str) -> None:
    item: dict[str, object] = {"type": "message", "id": "fixture", "role": "assistant"}
    if content_case != "missing":
        item["content"] = None if content_case == "null" else []

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(json.dumps({"type": "response.output_item.done", "output_index": 1, "item": item}))
        socket.send(json.dumps(response_event("completed", output=None)))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "synthetic fixture"})
            acc = ResponsesWebSocketAccumulator()
            acc.add_event(await driver.call(lane, "recv"))
            row = acc.detailed_snapshot()["output"][0]
            assert row["item"] == {"type": "message", "id": "fixture", "role": "assistant"}
            if content_case == "missing":
                assert "content" not in row
            else:
                assert row["content"] == item["content"]
            acc.add_event(await driver.call(lane, "recv"))
            assert acc.get_final_response().status == "completed"
