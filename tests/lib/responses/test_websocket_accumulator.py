from __future__ import annotations

import json
from typing import cast

import pytest
from websockets.sync.server import ServerConnection

from openai import omit
from openai._compat import model_copy
from openai.types.responses import ResponseStreamEvent
from openai.lib.responses_websocket import ResponsesWebSocketError, ResponsesWebSocketAccumulator
from openai.lib.streaming.responses import ResponseStreamState

from .test_websocket_session import session_for, script_server, response_event


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("terminal", ["completed", "failed", "incomplete"])
@pytest.mark.parametrize("output", ["missing", "null", "empty"])
async def test_opt_in_accumulation_exact_terminals(mode: str, terminal: str, output: str) -> None:
    created = response_event("created")
    frames = [
        {"type": "response.output_text.delta", "output_index": 4, "content_index": 1, "item_id": "msg", "delta": "pre"},
        {"type": "response.output_text.delta", "output_index": 4, "content_index": 1, "item_id": "msg", "delta": "fix"},
        {"type": "response.function_call_arguments.delta", "output_index": 0, "item_id": "fc", "delta": "{"},
        {
            "type": "response.function_call_arguments.done",
            "output_index": 0,
            "item_id": "fc",
            "arguments": '{"fixed":true}',
        },
        {"type": "response.custom_tool_call_input.delta", "output_index": 2, "item_id": "ct", "delta": "draft"},
        {"type": "response.custom_tool_call_input.done", "output_index": 2, "item_id": "ct", "input": "tool data"},
        {
            "type": "response.output_text.done",
            "output_index": 4,
            "content_index": 1,
            "item_id": "msg",
            "text": "corrected",
        },
        {"type": "response.future", "unmodeled": {"keep": True}},
    ]
    final = response_event(terminal)
    if output == "missing":
        del final["response"]["output"]
    elif output == "null":
        final["response"]["output"] = None

    def script(socket: ServerConnection) -> None:
        assert json.loads(socket.recv(timeout=5))["type"] == "response.create"
        for event in [created, *frames, final]:
            socket.send(json.dumps(event))
        # Reset does not release the socket or lane; a next turn can use it.
        assert json.loads(socket.recv(timeout=5))["input"] == "next"
        socket.send(json.dumps(response_event("completed", id="resp_next")))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "model": "test", "input": "first"})
            acc = ResponsesWebSocketAccumulator()
            initial = await driver.call(lane, "recv")
            acc.add_event(initial)
            # The existing SSE state needs item + part scaffolding. Prove it
            # cannot collect the same valid WS text event, then retain that
            # untouched typed event for the caller-fed helper.
            sse: ResponseStreamState[object] = ResponseStreamState(input_tools=omit, text_format=omit)
            sse.handle_event(cast(ResponseStreamEvent, model_copy(initial, deep=True)))
            first = await driver.call(lane, "recv")
            before = first.to_dict()
            with pytest.raises(RuntimeError, match="before receiving its output item"):
                sse.handle_event(cast(ResponseStreamEvent, model_copy(first, deep=True)))
            acc.add_event(first)
            saved = acc.snapshot()
            assert saved.output_text == "pre"
            assert first.to_dict() == before
            with pytest.raises(RuntimeError, match="No terminal"):
                acc.get_final_response()
            for _ in frames[1:]:
                event = await driver.call(lane, "recv")
                before = event.to_dict()
                acc.add_event(event)
                assert event.to_dict() == before
            projected = acc.snapshot()
            assert projected.output_text == "corrected"
            assert projected.terminal_type is None
            assert projected.output[0].arguments == '{"fixed":true}'
            assert projected.output[1].input == "tool data"
            assert saved.output_text == "pre"
            received = await driver.call(lane, "recv")
            original = received.response.to_dict()
            acc.add_event(received)
            result = acc.get_final_response()
            assert result.to_dict() == original
            assert result.status == terminal
            result.id = "caller mutation"
            assert acc.get_final_response().to_dict() == original
            assert received.response.to_dict() == original
            assert acc.snapshot().terminal_type == "response." + terminal
            assert acc.snapshot().output_text == ("" if output == "empty" else "corrected")
            # Existing get_final_response remains a terminal/final-item collector.
            # It must not silently gain delta reconstruction.
            legacy = await driver.call(lane, "get_final_response")
            assert not legacy.output
            acc.reset()
            assert not acc.snapshot().output
            assert saved.output_text == "pre"
            await driver.call(lane, "send", {"type": "response.create", "model": "test", "input": "next"})
            received = await driver.call(lane, "recv")
            acc.add_event(received)
            assert acc.get_final_response().id == "resp_next"


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_opt_in_accumulator_lane_and_item_replacements(mode: str) -> None:
    a_events = [
        response_event("created", "a"),
        {
            "type": "response.output_item.added",
            "stream_id": "a",
            "output_index": 0,
            "item": {
                "type": "message",
                "id": "msg",
                "content": [{"type": "output_text", "text": "first"}, {"type": "output_text", "text": "stale"}],
            },
        },
        {
            "type": "response.output_item.done",
            "stream_id": "a",
            "output_index": 0,
            "item": {"type": "message", "id": "msg", "content": [{"type": "output_text", "text": "fixed"}]},
        },
        {
            "type": "response.output_item.done",
            "stream_id": "a",
            "output_index": 0,
            "item": {"type": "function_call", "id": "msg", "name": "lookup", "call_id": "call", "arguments": "{}"},
        },
        {
            "type": "response.function_call_arguments.delta",
            "stream_id": "a",
            "output_index": 0,
            "item_id": "fc_new",
            "delta": '{"fresh":',
        },
    ]

    def script(socket: ServerConnection) -> None:
        for _ in range(2):
            socket.recv(timeout=5)
        for a in a_events:
            socket.send(json.dumps(a))
            socket.send(
                json.dumps(
                    {
                        "type": "response.output_text.delta",
                        "stream_id": "b",
                        "output_index": 9,
                        "content_index": 4,
                        "item_id": "msg_b",
                        "delta": "b",
                    }
                )
            )
        socket.send(json.dumps(response_event("incomplete", "a", output=None)))
        socket.send(json.dumps(response_event("failed", "b", output=None)))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane_a, lane_b = driver.session.lane("a"), driver.session.lane("b")
            for lane in (lane_a, lane_b):
                await driver.call(lane, "send", {"type": "response.create", "model": "test", "input": "text"})
            a, b = ResponsesWebSocketAccumulator(), ResponsesWebSocketAccumulator()
            saved = a.snapshot()
            for i in range(len(a_events)):
                ea, eb = await driver.call(lane_a, "recv"), await driver.call(lane_b, "recv")
                a.add_event(ea)
                with pytest.raises(ValueError, match="another WebSocket lane"):
                    a.add_event(eb)
                b.add_event(eb)
                if i == 1:
                    saved = a.snapshot()
                    assert saved.output_text == "firststale"
                elif i == 2:
                    assert a.snapshot().output_text == "fixed"
                    assert saved.output_text == "firststale"
                elif i == 3:
                    assert a.snapshot().output_text == ""
                    assert a.snapshot().output[0].arguments == "{}"
                elif i == 4:
                    projected = a.snapshot().output[0]
                    assert projected.item_id == "fc_new" and projected.arguments == '{"fresh":'
                    assert projected.name is None and projected.call_id is None
            a.add_event(await driver.call(lane_a, "recv"))
            b.add_event(await driver.call(lane_b, "recv"))
            assert a.get_final_response().id == "resp_a"
            assert b.get_final_response().id == "resp_b"
            assert a.snapshot().output_text == ""
            assert b.snapshot().output_text == "b" * len(a_events)


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("ending", ["EOF", "error", "missing", "null"])
async def test_opt_in_accumulator_never_invents_a_final(mode: str, ending: str) -> None:
    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(
            json.dumps(
                {
                    "type": "response.output_text.delta",
                    "item_id": "msg",
                    "output_index": 0,
                    "content_index": 0,
                    "delta": "partial",
                }
            )
        )
        if ending == "EOF":
            socket.close()
        elif ending == "error":
            socket.send(
                json.dumps(
                    {
                        "type": "error",
                        "error": {"type": "invalid_request_error", "code": "test", "message": "fixture error"},
                    }
                )
            )
        else:
            event = {"type": "response.completed"}
            if ending == "null":
                event["response"] = None  # type: ignore[assignment]
            socket.send(json.dumps(event))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "test"})
            acc = ResponsesWebSocketAccumulator()
            acc.add_event(await driver.call(lane, "recv"))
            if ending == "EOF":
                with pytest.raises(EOFError):
                    await driver.call(lane, "recv")
                expected = RuntimeError
            else:
                expected = ResponsesWebSocketError if ending == "error" else ValueError
                received = await driver.call(lane, "recv")
                with pytest.raises(expected):
                    acc.add_event(received)
            with pytest.raises(expected):
                acc.get_final_response()
            assert acc.snapshot().output_text == "partial"
            assert acc.snapshot().terminal_type is None
