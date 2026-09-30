from __future__ import annotations

import sys
import json
from typing import cast

import httpx2
import pytest
from websockets.sync.server import ServerConnection

from openai import OpenAI, AsyncOpenAI, omit
from openai._compat import PYDANTIC_V1, model_copy
from openai.types.responses import ResponseStreamEvent
from openai.lib.responses_websocket import ResponsesWebSocketError, ResponsesWebSocketAccumulator
from openai.lib.streaming.responses import ResponseStreamState
from openai.types.responses.responses_server_event import ResponseTextWsDelta

from .test_websocket_session import session_for, script_server, response_event


@pytest.mark.parametrize("field", ["output_index", "content_index"])
def test_large_sparse_indices_keep_numeric_order_and_prior_snapshots(field: str) -> None:
    acc = ResponsesWebSocketAccumulator()
    size = 2048
    step = sys.hash_info.modulus
    for i in reversed(range(size)):
        acc.add_event(
            ResponseTextWsDelta(
                type="response.output_text.delta",
                output_index=i * step if field == "output_index" else 0,
                content_index=i * step if field == "content_index" else 0,
                item_id="msg",
                delta=str(i) + ",",
                logprobs=[],
                sequence_number=size - i,
            )
        )
    prior = acc.snapshot()
    assert prior.output_text == "".join(str(i) + "," for i in range(size))
    if field == "output_index":
        assert [item.output_index for item in prior.output] == [i * step for i in range(size)]
    else:
        assert [index for index, _ in prior.output[0].text] == [i * step for i in range(size)]
    acc.reset()
    assert not acc.snapshot().output
    assert prior.output_text == "".join(str(i) + "," for i in range(size))


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
        {"type": "response.mcp_call_arguments.delta", "output_index": 6, "item_id": "mcp", "delta": '{"search":'},
        {"type": "response.mcp_call_arguments.done", "output_index": 6, "item_id": "mcp", "arguments": '{"search":1}'},
        {
            "type": "response.output_item.done",
            "output_index": 6,
            "item": {
                "type": "mcp_call",
                "id": "mcp",
                "arguments": '{"search":2}',
                "server_label": "fixture",
                "name": "search",
            },
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
                if event.type == "response.mcp_call_arguments.delta":
                    assert acc.snapshot().output[-1].arguments == '{"search":'
                elif event.type == "response.mcp_call_arguments.done":
                    assert acc.snapshot().output[-1].arguments == '{"search":1}'
            projected = acc.snapshot()
            assert projected.output_text == "corrected"
            assert projected.terminal_type is None
            assert projected.output[0].arguments == '{"fixed":true}'
            assert projected.output[1].input == "tool data"
            assert projected.output[-1].arguments == '{"search":2}'
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
            if output == "empty":
                assert not legacy.output
            else:
                # Only the full MCP item can be recovered by the existing
                # final-item collector; all provisional text/tools stay absent.
                assert legacy.output is not None
                assert len(legacy.output) == 1
                assert legacy.output[0].type == "mcp_call"
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


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "invalid",
    [
        {"type": "response.output_text.delta", "content_index": 0, "delta": None},
        {"type": "response.function_call_arguments.delta", "delta": {"unexpected": True}},
        {"type": "response.custom_tool_call_input.done", "input": 22},
        {"type": "response.output_text.delta", "content_index": 0, "delta": "corrupt", "item_id": None},
        {"type": "response.function_call_arguments.delta", "delta": "corrupt", "item_id": 0},
        {"type": "response.custom_tool_call_input.done", "input": "corrupt", "item_id": {"bad": True}},
    ],
)
async def test_rejects_invalid_fields_without_poisoning_prior_snapshot(mode: str, invalid: dict[str, object]) -> None:
    good = {
        "type": "response.output_text.delta",
        "item_id": "msg",
        "output_index": 0,
        "content_index": 0,
        "delta": "saved",
    }
    bad = {"output_index": 0, "item_id": "msg", **invalid}

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(json.dumps(good))
        socket.send(json.dumps(bad))
        socket.send(json.dumps(response_event("incomplete", output=None)))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "test"})
            acc = ResponsesWebSocketAccumulator()
            acc.add_event(await driver.call(lane, "recv"))
            prior = acc.snapshot()
            received = await driver.call(lane, "recv")
            original = model_copy(received, deep=True)
            with pytest.raises(ValueError, match="must be a string"):
                acc.add_event(received)
            assert acc.snapshot() == prior
            assert received == original
            acc.add_event(await driver.call(lane, "recv"))
            assert acc.get_final_response().status == "incomplete"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "invalid_index",
    [{}, {"content_index": "wrong"}, {"content_index": None}, {"content_index": False}, {"content_index": -1}],
)
@pytest.mark.parametrize(
    "fields",
    [
        {"type": "response.output_text.delta", "delta": "bad"},
        {"type": "response.output_text.done", "text": "bad"},
        {"type": "response.content_part.added", "part": {"type": "output_text", "text": "bad"}},
        {"type": "response.content_part.done", "part": {"type": "output_text", "text": "bad"}},
    ],
)
async def test_invalid_text_position_does_not_replace_previous_item(
    mode: str, fields: dict[str, object], invalid_index: dict[str, object]
) -> None:
    initial = {
        "type": "response.output_text.delta",
        "output_index": 0,
        "content_index": 0,
        "item_id": "original",
        "delta": "saved",
    }

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(json.dumps(initial))
        socket.send(json.dumps({"output_index": 0, "item_id": "replacement", **fields, **invalid_index}))
        socket.send(json.dumps({**initial, "delta": " after"}))
        socket.send(json.dumps(response_event("completed", output=None)))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "test"})
            acc = ResponsesWebSocketAccumulator()
            acc.add_event(await driver.call(lane, "recv"))
            prior = acc.snapshot()
            invalid = await driver.call(lane, "recv")
            untouched = model_copy(invalid, deep=True)
            with pytest.raises(ValueError, match="content_index"):
                acc.add_event(invalid)
            assert acc.snapshot() == prior
            assert invalid == untouched
            acc.add_event(await driver.call(lane, "recv"))
            assert acc.snapshot().output_text == "saved after"
            acc.add_event(await driver.call(lane, "recv"))
            assert acc.get_final_response().status == "completed"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("phase", ["created", "in_progress", "completed", "failed", "incomplete"])
async def test_invalid_lifecycle_replacement_is_atomic(mode: str, phase: str) -> None:
    first = {
        "type": "response.output_text.delta",
        "item_id": "m",
        "output_index": 0,
        "content_index": 0,
        "delta": "safe",
    }
    malformed = [
        {
            "type": "mcp_approval_request",
            "id": "approval",
            "name": "search",
            "server_label": "fixture",
            "arguments": '{"key":1}',
        },
        {"type": "function_call", "id": "f", "name": "bad", "arguments": {"bad": True}, "call_id": "c"},
    ]

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(json.dumps(first))
        socket.send(json.dumps(response_event(phase, output=malformed)))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "test"})
            acc = ResponsesWebSocketAccumulator()
            acc.add_event(await driver.call(lane, "recv"))
            before = acc.snapshot()
            received = await driver.call(lane, "recv")
            untouched = model_copy(received, deep=True)
            with pytest.raises(ValueError, match="arguments"):
                acc.add_event(received)
            assert acc.snapshot() == before
            assert received == untouched
            error = ValueError if phase in {"completed", "failed", "incomplete"} else RuntimeError
            with pytest.raises(error):
                acc.get_final_response()


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "invalid,field",
    [
        pytest.param({"type": "message", "content": "bad"}, "content", id="string-content"),
        pytest.param({"type": "message", "content": 42}, "content", id="numeric-content"),
        pytest.param({"type": "message", "content": {}}, "content", id="object-content"),
        pytest.param({"type": "message", "content": ["bad"]}, "type", id="invalid-part"),
        pytest.param({"type": "message", "content": [{"type": 42}]}, "type", id="invalid-part-type"),
        pytest.param({"type": "function_call", "name": {"bad": True}}, "name", id="function-name"),
        pytest.param({"type": "function_call", "call_id": 42}, "call_id", id="function-call-id"),
        pytest.param({"type": "mcp_call", "name": 42}, "name", id="mcp-name"),
        pytest.param({"type": "mcp_approval_request", "call_id": {"bad": True}}, "call_id", id="mcp-call-id"),
        pytest.param({"type": "custom_tool_call", "name": 42}, "name", id="custom-name"),
    ],
)
async def test_invalid_projected_item_fields_do_not_retire_or_replace_current(
    mode: str, invalid: dict[str, object], field: str
) -> None:
    first = {
        "type": "response.output_text.delta",
        "item_id": "original",
        "output_index": 0,
        "content_index": 0,
        "delta": "kept",
    }
    replacement = {"id": "replacement", **invalid}

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(json.dumps(first))
        for phase in ("added", "done"):
            socket.send(json.dumps({"type": "response.output_item." + phase, "output_index": 0, "item": replacement}))
        socket.send(json.dumps({**first, "delta": " more"}))
        # A lifecycle carrying an invalid later item cannot commit the earlier
        # valid item or a final, and must retain its validation error.
        socket.send(json.dumps(response_event("completed", output=[{"type": "message", "id": "valid"}, replacement])))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "test"})
            acc = ResponsesWebSocketAccumulator()
            acc.add_event(await driver.call(lane, "recv"))
            before = acc.snapshot()
            for _ in range(2):
                received = await driver.call(lane, "recv")
                original = model_copy(received, deep=True)
                with pytest.raises(ValueError, match=field):
                    acc.add_event(received)
                assert acc.snapshot() == before
                assert received == original
            acc.add_event(await driver.call(lane, "recv"))
            assert before.output_text == "kept"
            assert acc.snapshot().output_text == "kept more"
            before = acc.snapshot()
            received = await driver.call(lane, "recv")
            original = model_copy(received, deep=True)
            with pytest.raises(ValueError, match=field) as failure:
                acc.add_event(received)
            assert acc.snapshot() == before
            assert received == original
            with pytest.raises(ValueError) as final:
                acc.get_final_response()
            assert final.value is failure.value


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("nullable", [{}, {"content": None, "name": None, "call_id": None}])
async def test_nullable_message_content_and_projected_metadata(mode: str, nullable: dict[str, object]) -> None:
    message: dict[str, object] = {"type": "message", "id": "message", **nullable}

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(json.dumps({"type": "response.output_item.done", "output_index": 0, "item": message}))
        socket.send(json.dumps(response_event("completed", output=[message])))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "test"})
            acc = ResponsesWebSocketAccumulator()
            for _ in range(2):
                received = await driver.call(lane, "recv")
                untouched = model_copy(received, deep=True)
                acc.add_event(received)
                projection = acc.snapshot()
                assert projection.output_text == ""
                assert projection.output[0].name is None and projection.output[0].call_id is None
                assert received == untouched
                if received.type == "response.completed":
                    assert acc.get_final_response().to_dict() == received.response.to_dict()


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "invalid",
    [
        {"type": "response.mcp_call_arguments.delta", "output_index": False, "item_id": "approval", "delta": "bad"},
        {"type": "response.mcp_call_arguments.delta", "output_index": -1, "item_id": "approval", "delta": "bad"},
        {
            "type": "response.output_item.done",
            "output_index": -1,
            "item": {"type": "message", "id": "bad", "content": [{"type": "output_text", "text": "bad"}]},
        },
    ],
)
async def test_mcp_approval_items_keep_pending_arguments_and_reject_invalid_output_index(
    mode: str, invalid: dict[str, object]
) -> None:
    approval = {
        "type": "mcp_approval_request",
        "id": "approval",
        "name": "search",
        "server_label": "fixture",
        "arguments": '{"key":1}',
    }

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(json.dumps({"type": "response.output_item.added", "output_index": 0, "item": approval}))
        socket.send(json.dumps(invalid))
        socket.send(json.dumps(response_event("completed", output=None)))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "test"})
            acc = ResponsesWebSocketAccumulator()
            acc.add_event(await driver.call(lane, "recv"))
            before = acc.snapshot()
            assert before.output[0].arguments == '{"key":1}'
            with pytest.raises(ValueError, match="output_index"):
                acc.add_event(await driver.call(lane, "recv"))
            assert acc.snapshot() == before
            terminal = await driver.call(lane, "recv")
            acc.add_event(terminal)
            assert acc.get_final_response().to_dict() == terminal.response.to_dict()


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("item_field", [{}, {"item": None}])
async def test_empty_output_item_keeps_previous_projection(mode: str, item_field: dict[str, object]) -> None:
    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(
            json.dumps(
                {"type": "response.function_call_arguments.delta", "output_index": 0, "item_id": "fc", "delta": "{"}
            )
        )
        for phase in ("added", "done"):
            socket.send(json.dumps({"type": "response.output_item." + phase, "output_index": 0, **item_field}))
        socket.send(
            json.dumps(
                {"type": "response.function_call_arguments.delta", "output_index": 0, "item_id": "fc", "delta": "}"}
            )
        )
        socket.send(json.dumps(response_event("completed", output=None)))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "test"})
            acc = ResponsesWebSocketAccumulator()
            acc.add_event(await driver.call(lane, "recv"))
            prior = acc.snapshot()
            for _ in range(2):
                received = await driver.call(lane, "recv")
                before = model_copy(received, deep=True)
                acc.add_event(received)
                assert acc.snapshot() == prior
                assert received == before
            acc.add_event(await driver.call(lane, "recv"))
            assert acc.snapshot().output[0].arguments == "{}"
            acc.add_event(await driver.call(lane, "recv"))
            assert acc.get_final_response().status == "completed"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("bad_item", [0, True, "not an item", ["bad"], {"missing": "type"}])
async def test_invalid_item_shape_preserves_retained_projection(mode: str, bad_item: object) -> None:
    delta = {"type": "response.function_call_arguments.delta", "output_index": 0, "item_id": "fc", "delta": "saved"}

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(json.dumps(delta))
        for phase in ("added", "done"):
            socket.send(json.dumps({"type": "response.output_item." + phase, "output_index": 0, "item": bad_item}))
        socket.send(json.dumps(response_event("completed", output=None)))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "test"})
            acc = ResponsesWebSocketAccumulator()
            acc.add_event(await driver.call(lane, "recv"))
            prior = acc.snapshot()
            for _ in range(2):
                received = await driver.call(lane, "recv")
                original = model_copy(received, deep=True)
                with pytest.raises(ValueError, match="type"):
                    acc.add_event(received)
                assert acc.snapshot() == prior
                assert received == original
            acc.add_event(await driver.call(lane, "recv"))
            assert acc.snapshot().output[0].arguments == "saved"
            assert acc.get_final_response().status == "completed"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("terminal_output", ["null", "authoritative"])
async def test_retired_items_do_not_revert_full_or_incremental_replacements(mode: str, terminal_output: str) -> None:
    delta = {"type": "response.output_text.delta", "output_index": 0, "content_index": 0, "item_id": "a", "delta": "A"}
    replacement = {
        "type": "response.output_item.done",
        "output_index": 0,
        "item": {"type": "message", "id": "b", "role": "assistant", "content": [{"type": "output_text", "text": "B"}]},
    }
    stale_a = {
        "type": "message",
        "id": "a",
        "role": "assistant",
        "content": [{"type": "output_text", "text": "Final A"}],
    }
    frames = [
        delta,
        replacement,
        {**delta, "delta": "stale A"},
        {"type": "response.output_item.added", "output_index": 0, "item": stale_a},
        {"type": "response.output_item.done", "output_index": 0, "item": stale_a},
        {**delta, "item_id": "b", "delta": " continued"},
        {**delta, "item_id": "c", "delta": "C"},
        {**delta, "item_id": "b", "delta": "stale B"},
        {**delta, "delta": "stale A"},
        response_event("completed", output=None if terminal_output == "null" else [stale_a]),
    ]

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        for frame in frames:
            socket.send(json.dumps(frame))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "test"})
            acc = ResponsesWebSocketAccumulator()
            for expected in ("A", "B", "B", "B", "B", "B continued", "C", "C", "C"):
                received = await driver.call(lane, "recv")
                original = model_copy(received, deep=True)
                acc.add_event(received)
                assert acc.snapshot().output_text == expected
                assert received == original
            terminal = await driver.call(lane, "recv")
            acc.add_event(terminal)
            assert acc.snapshot().output_text == ("C" if terminal_output == "null" else "Final A")
            assert acc.get_final_response().to_dict() == terminal.response.to_dict()


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("phase", ["created", "in_progress", "completed", "failed", "incomplete"])
@pytest.mark.parametrize("bad_id", [42, ["not", "an", "id"], {"value": "bad"}])
async def test_invalid_response_id_cannot_commit_lifecycle_output(mode: str, phase: str, bad_id: object) -> None:
    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(
            json.dumps(
                {
                    "type": "response.output_text.delta",
                    "output_index": 0,
                    "content_index": 0,
                    "item_id": "a",
                    "delta": "saved",
                }
            )
        )
        socket.send(json.dumps(response_event(phase, id=bad_id, output=[])))
        if phase in {"created", "in_progress"}:
            socket.send(json.dumps(response_event("completed", id="valid", output=None)))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "test"})
            acc = ResponsesWebSocketAccumulator()
            acc.add_event(await driver.call(lane, "recv"))
            prior = acc.snapshot()
            received = await driver.call(lane, "recv")
            original = model_copy(received, deep=True)
            if PYDANTIC_V1 and bad_id == 42:
                # V1 normalizes the wire number before it reaches this helper.
                # Keep accepting the resulting string, as on any other event.
                assert received.response.id == "42"
                acc.add_event(received)
                assert acc.snapshot().response_id == "42"
                assert received == original
                if phase in {"completed", "failed", "incomplete"}:
                    assert acc.get_final_response().to_dict() == received.response.to_dict()
                return
            with pytest.raises(ValueError, match="id"):
                acc.add_event(received)
            assert acc.snapshot() == prior
            assert received == original
            if phase in {"created", "in_progress"}:
                acc.add_event(await driver.call(lane, "recv"))
                assert acc.get_final_response().id == "valid"
                assert acc.snapshot().output_text == "saved"
            else:
                with pytest.raises(ValueError, match="id"):
                    acc.get_final_response()


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("id_field", [{}, {"id": None}])
async def test_nullable_response_id_keeps_exact_final(mode: str, id_field: dict[str, object]) -> None:
    final = response_event("completed", output=None)
    del final["response"]["id"]
    final["response"].update(id_field)

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(json.dumps(response_event("created", id="prior")))
        socket.send(json.dumps(final))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "test"})
            acc = ResponsesWebSocketAccumulator()
            acc.add_event(await driver.call(lane, "recv"))
            received = await driver.call(lane, "recv")
            original = model_copy(received, deep=True)
            acc.add_event(received)
            assert acc.snapshot().response_id == "prior"
            assert acc.get_final_response().to_dict() == received.response.to_dict()
            assert received == original


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("bad_id", [42, ["not", "an", "id"], {"value": "bad"}])
@pytest.mark.parametrize("first_kind", ["delta", "completed"])
@pytest.mark.parametrize("next_lane", [None, "next"])
async def test_raw_connection_invalid_stream_id_cannot_bind(
    mode: str, bad_id: object, first_kind: str, next_lane: str | None
) -> None:
    delta = {
        "type": "response.output_text.delta",
        "output_index": 0,
        "content_index": 0,
        "item_id": "a",
        "delta": "saved",
    }
    first = {**(delta if first_kind == "delta" else response_event("completed")), "stream_id": bad_id}

    def script(socket: ServerConnection) -> None:
        for frame in (
            first,
            response_event("created", next_lane),
            {**delta, "stream_id": next_lane},
            response_event("completed", next_lane, output=None),
        ):
            socket.send(json.dumps(frame))

    with script_server(script) as url:
        if mode == "sync":
            with (
                OpenAI(
                    api_key="fake-accumulator-key", base_url=url, http_client=httpx2.Client(trust_env=False)
                ) as client,
                client.responses.connect() as connection,
            ):
                events = [connection.recv() for _ in range(4)]
        else:
            async with (
                AsyncOpenAI(
                    api_key="fake-accumulator-key", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
                ) as async_client,
                async_client.responses.connect() as async_connection,
            ):
                events = [await async_connection.recv() for _ in range(4)]
        acc = ResponsesWebSocketAccumulator()
        prior = acc.snapshot()
        malformed = events[0]
        original = model_copy(malformed, deep=True)
        if isinstance(malformed.stream_id, str):
            # Pydantic may normalize a number before this helper sees it.
            assert bad_id == 42 and malformed.stream_id == "42"
            acc.add_event(malformed)
            assert acc.snapshot().stream_id == "42"
            acc.reset()
        else:
            with pytest.raises(ValueError, match="stream_id"):
                acc.add_event(malformed)
            assert acc.snapshot() == prior
            with pytest.raises(RuntimeError, match="No terminal"):
                acc.get_final_response()
        assert malformed == original
        for event in events[1:]:
            original = model_copy(event, deep=True)
            acc.add_event(event)
            assert event == original
        assert prior.stream_id is None and not prior.output
        assert acc.snapshot().stream_id == next_lane
        assert acc.snapshot().output_text == "saved"
        assert acc.get_final_response().id == f"resp_{next_lane or 'default'}"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("unknown_type", [["response.future"], {"type": "response.future"}])
async def test_raw_connection_unknown_unhashable_events_are_ignored(mode: str, unknown_type: object) -> None:
    def script(socket: ServerConnection) -> None:
        socket.send(
            json.dumps(
                {
                    "type": "response.output_text.delta",
                    "output_index": 0,
                    "content_index": 0,
                    "item_id": "a",
                    "delta": "saved",
                }
            )
        )
        socket.send(json.dumps({"type": unknown_type, "stream_id": "unregistered"}))
        socket.send(json.dumps(response_event("completed", output=None)))

    with script_server(script) as url:
        # Test the public raw connection: session.recv() has its own handling
        # before it passes any decoded event to this opt-in helper.
        if mode == "sync":
            with (
                OpenAI(
                    api_key="fake-accumulator-key", base_url=url, http_client=httpx2.Client(trust_env=False)
                ) as client,
                client.responses.connect() as connection,
            ):
                events = [connection.recv() for _ in range(3)]
        else:
            async with (
                AsyncOpenAI(
                    api_key="fake-accumulator-key", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
                ) as async_client,
                async_client.responses.connect() as async_connection,
            ):
                events = [await async_connection.recv() for _ in range(3)]
        acc = ResponsesWebSocketAccumulator()
        acc.add_event(events[0])
        prior = acc.snapshot()
        unknown = model_copy(events[1], deep=True)
        acc.add_event(events[1])
        assert acc.snapshot() == prior
        assert events[1] == unknown
        acc.add_event(events[2])
        assert acc.snapshot().output_text == "saved"
        assert acc.get_final_response().status == "completed"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("phase", ["created", "in_progress", "completed", "failed", "incomplete"])
@pytest.mark.parametrize("bad_output", [{}, 42, "bad"])
async def test_nonlist_lifecycle_output_is_never_a_valid_final(mode: str, phase: str, bad_output: object) -> None:
    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(
            json.dumps(
                {
                    "type": "response.output_text.delta",
                    "output_index": 0,
                    "content_index": 0,
                    "item_id": "a",
                    "delta": "saved",
                }
            )
        )
        socket.send(json.dumps(response_event(phase, output=bad_output)))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "test"})
            acc = ResponsesWebSocketAccumulator()
            acc.add_event(await driver.call(lane, "recv"))
            prior = acc.snapshot()
            received = await driver.call(lane, "recv")
            original = model_copy(received, deep=True)
            with pytest.raises(ValueError, match="output"):
                acc.add_event(received)
            assert acc.snapshot() == prior
            assert received == original
            error = ValueError if phase in {"completed", "failed", "incomplete"} else RuntimeError
            with pytest.raises(error):
                acc.get_final_response()


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("part_phase", ["added", "done"])
async def test_nontext_part_correction_clears_only_its_own_text_position(mode: str, part_phase: str) -> None:
    delta = {
        "type": "response.output_text.delta",
        "output_index": 0,
        "content_index": 0,
        "item_id": "a",
        "delta": "saved",
    }
    frames = [
        delta,
        {**delta, "content_index": 1, "delta": "neighbor"},
        {
            "type": "response.content_part." + part_phase,
            "output_index": 0,
            "content_index": 0,
            "item_id": "a",
            "part": {"type": "refusal", "refusal": "corrected"},
        },
        response_event("completed", output=None),
    ]

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        for frame in frames:
            socket.send(json.dumps(frame))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "test"})
            acc = ResponsesWebSocketAccumulator()
            for _ in range(2):
                acc.add_event(await driver.call(lane, "recv"))
            prior = acc.snapshot()
            correction = await driver.call(lane, "recv")
            original = model_copy(correction, deep=True)
            acc.add_event(correction)
            assert correction == original
            assert prior.output_text == "savedneighbor"
            assert acc.snapshot().output[0].text == ((1, "neighbor"),)
            terminal = await driver.call(lane, "recv")
            acc.add_event(terminal)
            assert acc.snapshot().output_text == "neighbor"
            assert acc.get_final_response().to_dict() == terminal.response.to_dict()


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "bad_part",
    [{}, {"part": None}, {"part": "bad"}, {"part": 42}, {"part": []}, {"part": {}}, {"part": {"type": 7}}],
)
async def test_invalid_part_never_replaces_current_item(mode: str, bad_part: dict[str, object]) -> None:
    delta = {
        "type": "response.output_text.delta",
        "output_index": 0,
        "content_index": 0,
        "item_id": "a",
        "delta": "kept",
    }

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(json.dumps(delta))
        for phase in ("added", "done"):
            socket.send(
                json.dumps(
                    {
                        "type": "response.content_part." + phase,
                        "output_index": 0,
                        "content_index": 0,
                        "item_id": "b",
                        **bad_part,
                    }
                )
            )
        socket.send(json.dumps({**delta, "delta": " more"}))
        socket.send(json.dumps(response_event("completed", output=None)))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "test"})
            acc = ResponsesWebSocketAccumulator()
            acc.add_event(await driver.call(lane, "recv"))
            before = acc.snapshot()
            for _ in range(2):
                received = await driver.call(lane, "recv")
                original = model_copy(received, deep=True)
                with pytest.raises(ValueError, match="type"):
                    acc.add_event(received)
                assert acc.snapshot() == before
                assert received == original
            acc.add_event(await driver.call(lane, "recv"))
            assert before.output_text == "kept"
            assert acc.snapshot().output_text == "kept more"
            terminal = await driver.call(lane, "recv")
            acc.add_event(terminal)
            assert acc.get_final_response().to_dict() == terminal.response.to_dict()


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("nullable", [{}, {"text": None}])
async def test_nullable_finalized_text_does_not_block_exact_terminal(mode: str, nullable: dict[str, object]) -> None:
    item: dict[str, object] = {
        "id": "msg",
        "type": "message",
        "role": "assistant",
        "content": [
            {"type": "output_text", "text": "hello", "annotations": []},
            {"type": "output_text", "annotations": [], **nullable},
            {"type": "output_text", "text": " world", "annotations": []},
        ],
    }

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(
            json.dumps(
                {
                    "type": "response.output_text.delta",
                    "item_id": "msg",
                    "output_index": 0,
                    "content_index": 0,
                    "delta": "old",
                }
            )
        )
        socket.send(json.dumps({"type": "response.output_item.done", "output_index": 0, "item": item}))
        socket.send(json.dumps(response_event("incomplete", output=[item])))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "test"})
            acc = ResponsesWebSocketAccumulator()
            acc.add_event(await driver.call(lane, "recv"))
            for _ in range(2):
                received = await driver.call(lane, "recv")
                before = model_copy(received, deep=True)
                acc.add_event(received)
                assert acc.snapshot().output_text == "hello world"
                assert received == before
                if received.type == "response.incomplete":
                    assert acc.get_final_response().to_dict() == received.response.to_dict()
            assert acc.get_final_response().output_text == "hello world"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("foreign_first", [True, False])
async def test_default_lane_foreign_events_can_be_inspected_without_feeding_the_projection(
    mode: str, foreign_first: bool
) -> None:
    own = {
        "type": "response.output_text.delta",
        "item_id": "msg",
        "output_index": 0,
        "content_index": 0,
        "delta": "default",
    }
    foreign = {**own, "stream_id": "unregistered", "delta": "foreign"}

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        for frame in [foreign, own] if foreign_first else [own, foreign]:
            socket.send(json.dumps(frame))
        socket.send(json.dumps(response_event("completed", output=None)))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "input": "test"})
            accumulator = ResponsesWebSocketAccumulator()
            expected_stream_id = None
            observed: list[str] = []
            for _ in range(3):
                event = await driver.call(lane, "recv")
                if event.type == "response.output_text.delta":
                    observed.append(event.delta)
                if getattr(event, "stream_id", None) != expected_stream_id:
                    continue
                accumulator.add_event(event)
            assert set(observed) == {"default", "foreign"}
            assert accumulator.snapshot().output_text == "default"
            assert accumulator.get_final_response().status == "completed"
