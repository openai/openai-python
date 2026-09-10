from __future__ import annotations

import json
import time
import asyncio
from typing import Any
from collections.abc import Iterator, AsyncIterator
from typing_extensions import override

import anyio
import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, BadRequestError
from openai.types.beta.agent_session_event import AgentSessionEvent
from openai.types.beta.agent_session_input_message_param import AgentSessionInputMessageParam


def session(status: str = "idle") -> dict[str, object]:
    return {
        "id": "session_test",
        "object": "agent.session",
        "agent": {
            "id": "agent_test",
            "object": "agent",
            "created_at": 1,
            "updated_at": 1,
            "metadata": {},
            "model": "test-model",
            "multi_agent": {"enabled": True},
            "reasoning": {},
            "service_tier": "default",
            "text": {"format": {"type": "text"}, "verbosity": "medium"},
            "tools": [],
        },
        "created_at": 1,
        "last_active_at": 1,
        "environment": {"type": "none"},
        "metadata": {},
        "required_actions": [],
        "status": status,
        "vault_ids": [],
    }


def turn_event(kind: str, turn_id: str = "turn_root", *, subagent_id: str | None = None) -> dict[str, object]:
    status = "in_progress" if kind == "created" else kind
    return {
        "type": f"agent.session.turn.{kind}",
        "session_id": "session_test",
        "turn_id": turn_id,
        "turn": {
            "id": turn_id,
            "object": "agent.session.turn",
            "agent_id": "agent_test",
            "session_id": "session_test",
            "created_at": 1,
            "status": status,
            "subagent_id": subagent_id,
        },
    }


def idle() -> dict[str, object]:
    return {"type": "agent.session.idle", "session": session()}


def call(arguments: object = '{"query":"test"}', *, call_id: str = "call_test") -> dict[str, object]:
    return {
        "type": "agent.session.turn.item.added",
        "session_id": "session_test",
        "turn_id": "turn_root",
        "item": {
            "id": "item_test",
            "type": "function_call",
            "name": "search",
            "call_id": call_id,
            "arguments": arguments,
            "status": "in_progress",
            "turn_id": "turn_root",
        },
    }


class EventBody(httpx2.SyncByteStream, httpx2.AsyncByteStream):
    def __init__(self, events: list[dict[str, object]]) -> None:
        self.events = events
        self.closed = False
        self.read_count = 0

    @override
    def __iter__(self) -> Iterator[bytes]:
        for index, event in enumerate(self.events):
            self.read_count += 1
            yield f"data: {json.dumps({'event_id': str(index), **event})}\n\n".encode()

    @override
    async def __aiter__(self) -> AsyncIterator[bytes]:
        for chunk in self:
            yield chunk

    @override
    def close(self) -> None:
        self.closed = True

    @override
    async def aclose(self) -> None:
        self.closed = True


class Server:
    def __init__(self) -> None:
        self.body = EventBody([turn_event("created"), turn_event("completed"), idle()])
        self.requests: list[httpx2.Request] = []
        self.status = "idle"
        self.reject_input = False
        self.tool_errors: list[str] = []
        self.lost_responses: set[str] = set()

    def handle(self, request: httpx2.Request) -> httpx2.Response:
        self.requests.append(request)
        if request.method == "GET" and request.url.path.endswith("/events"):
            return httpx2.Response(200, headers={"content-type": "text/event-stream"}, stream=self.body)
        if request.method == "GET":
            return httpx2.Response(200, json=session(self.status))
        assert request.method == "POST"
        submitted = json.loads(request.content)["events"][0]
        delivery = submitted.get("call_id", submitted["type"])
        if delivery in self.lost_responses:
            self.lost_responses.remove(delivery)
            raise httpx2.ReadTimeout("Response lost after accepting the POST", request=request)
        if self.tool_errors and json.loads(request.content)["events"][0]["type"] == "agent.session.input.tool_result":
            return httpx2.Response(
                400, json={"error": {"code": "invalid_request_error", "message": self.tool_errors.pop(0)}}
            )
        if self.reject_input:
            return httpx2.Response(400, json={"error": {"message": "Rejected input", "type": "invalid_request_error"}})
        return httpx2.Response(204)

    def inputs(self) -> list[dict[str, Any]]:
        return [json.loads(request.content)["events"][0] for request in self.requests if request.method == "POST"]


@pytest.fixture
def server() -> Server:
    return Server()


@pytest.fixture(params=[False, True], ids=["sync", "async"])
async def sdk(request: pytest.FixtureRequest, server: Server) -> AsyncIterator[OpenAI | AsyncOpenAI]:
    transport = httpx2.MockTransport(server.handle)
    if request.param:
        async with AsyncOpenAI(
            api_key="synthetic",
            base_url="https://sdk-test.example/v1",
            max_retries=0,
            _strict_response_validation=True,
            http_client=httpx2.AsyncClient(transport=transport, trust_env=False),
        ) as client:
            yield client
    else:
        with OpenAI(
            api_key="synthetic",
            base_url="https://sdk-test.example/v1",
            max_retries=0,
            _strict_response_validation=True,
            http_client=httpx2.Client(transport=transport, trust_env=False),
        ) as client:
            yield client


async def consume(client: OpenAI | AsyncOpenAI, **kwargs: Any) -> list[AgentSessionEvent]:
    if isinstance(client, AsyncOpenAI):
        async with client.beta.agents.sessions.stream("session_test", **kwargs) as stream:
            return [event async for event in stream]
    with client.beta.agents.sessions.stream("session_test", **kwargs) as stream:
        return list(stream)


async def test_input_order_and_options(sdk: OpenAI | AsyncOpenAI, server: Server) -> None:
    events = await consume(
        sdk, input="Hello", extra_headers={"x-test": "kept"}, timeout=12.5, idempotency_key="input-key"
    )
    assert [event.type for event in events] == [
        "agent.session.turn.created",
        "agent.session.turn.completed",
        "agent.session.idle",
    ]
    assert [(r.method, r.url.path) for r in server.requests] == [
        ("GET", "/v1/agents/sessions/session_test"),
        ("GET", "/v1/agents/sessions/session_test/events"),
        ("POST", "/v1/agents/sessions/session_test/events"),
    ]
    assert all(r.headers["x-test"] == "kept" for r in server.requests)
    assert all(r.extensions["timeout"]["read"] == 12.5 for r in server.requests)
    assert server.requests[-1].headers["idempotency-key"] == "input-key"
    assert server.inputs() == [
        {
            "type": "agent.session.input.message",
            "input": [{"role": "user", "content": [{"type": "input_text", "text": "Hello"}]}],
        }
    ]
    assert server.body.closed


async def test_iterable_input_and_until_done(sdk: OpenAI | AsyncOpenAI, server: Server) -> None:
    messages: list[AgentSessionInputMessageParam] = [
        {"role": "user", "content": [{"type": "input_text", "text": "Hello"}]}
    ]
    if isinstance(sdk, AsyncOpenAI):
        async with sdk.beta.agents.sessions.stream("session_test", input=iter(messages)) as stream:
            await stream.until_done()
    else:
        with sdk.beta.agents.sessions.stream("session_test", input=iter(messages)) as stream:
            stream.until_done()
    assert server.inputs()[0]["input"] == messages
    assert server.body.closed


@pytest.mark.parametrize("ending", ["completed", "failed", "cancelled"])
async def test_target_turn_and_idle(sdk: OpenAI | AsyncOpenAI, server: Server, ending: str) -> None:
    server.body = EventBody(
        [
            idle(),
            turn_event("created", "turn_child", subagent_id="subagent_test"),
            turn_event("completed", "turn_child", subagent_id="subagent_test"),
            idle(),
            turn_event("created"),
            turn_event("completed", "other_turn"),
            idle(),
            turn_event(ending),
            idle(),
            turn_event("created", "later_turn"),
        ]
    )
    events = await consume(sdk, input="Hello")
    assert len(events) == 9
    assert events[-2].type == f"agent.session.turn.{ending}"
    assert events[-1].type == "agent.session.idle"
    assert server.body.read_count == 9
    assert server.body.closed


async def test_session_failure_terminates(sdk: OpenAI | AsyncOpenAI, server: Server) -> None:
    server.body = EventBody([{"type": "agent.session.failed", "session": session("failed")}, idle()])
    events = await consume(sdk, input="Hello")
    assert [event.type for event in events] == ["agent.session.failed"]
    assert server.body.closed


@pytest.mark.parametrize("arguments", [{"query": "test"}, '{"query":"test"}'])
@pytest.mark.parametrize("result", ["found", {"rows": [1]}, [{"type": "input_text", "text": "found"}], None])
async def test_tool_results_and_duplicates(
    sdk: OpenAI | AsyncOpenAI, server: Server, arguments: object, result: object
) -> None:
    called: list[dict[str, object]] = []

    def handler(arguments: dict[str, object]) -> object:
        called.append(arguments)
        return result

    repeated = {"event_id": "repeated", **call(arguments)}
    server.body = EventBody(
        [turn_event("created"), repeated, repeated, call(arguments), turn_event("completed"), idle()]
    )
    events = await consume(sdk, input="Hello", tool_handlers={"search": handler}, idempotency_key="input-only")
    assert called == [{"query": "test"}]
    assert len(events) == 5
    outputs = server.inputs()
    assert len(outputs) == 2
    assert outputs[1]["type"] == "agent.session.input.tool_result"
    assert outputs[1]["call_id"] == "call_test"
    assert outputs[1]["turn_id"] == "turn_root"
    assert outputs[1]["success"] is True
    output = outputs[1].get("output")
    if isinstance(result, dict):
        assert isinstance(output, str)
        output = json.loads(output)
    assert output == result
    assert server.requests[-1].headers.get("idempotency-key") != "input-only"
    assert server.body.closed


async def test_missing_handler_does_not_submit_result(sdk: OpenAI | AsyncOpenAI, server: Server) -> None:
    server.body = EventBody([turn_event("created"), call(), turn_event("completed"), idle()])
    events = await consume(sdk, input="Hello")
    assert events[1].type == "agent.session.turn.item.added"
    assert len(server.inputs()) == 1


async def test_handler_error_is_redacted(sdk: OpenAI | AsyncOpenAI, server: Server) -> None:
    def handler(_arguments: dict[str, object]) -> object:
        raise ValueError("synthetic-sensitive-value")

    server.body = EventBody([turn_event("created"), call(), turn_event("completed"), idle()])
    await consume(sdk, input="Hello", tool_handlers={"search": handler})
    result = server.inputs()[1]
    assert result["success"] is False
    assert result["error"]
    assert "synthetic-sensitive-value" not in json.dumps(result)
    assert result.get("output") is None


async def test_input_failure_closes_stream(sdk: OpenAI | AsyncOpenAI, server: Server) -> None:
    server.reject_input = True
    with pytest.raises(BadRequestError):
        await consume(sdk, input="Hello")
    assert server.body.closed
    assert server.body.read_count == 0


@pytest.mark.parametrize("events", [[], [turn_event("created")], [turn_event("created"), turn_event("completed")]])
async def test_premature_eof(sdk: OpenAI | AsyncOpenAI, server: Server, events: list[dict[str, object]]) -> None:
    server.body = EventBody(events)
    with pytest.raises(RuntimeError):
        await consume(sdk, input="Hello")
    assert server.body.closed


async def test_requires_idle_session(sdk: OpenAI | AsyncOpenAI, server: Server) -> None:
    server.status = "in_progress"
    with pytest.raises(ValueError, match="idle"):
        await consume(sdk, input="Hello")
    assert len(server.requests) == 1


async def test_context_exit_close_and_single_use(sdk: OpenAI | AsyncOpenAI, server: Server) -> None:
    if isinstance(sdk, AsyncOpenAI):
        manager = sdk.beta.agents.sessions.stream("session_test", input="Hello")
        async with manager as stream:
            await stream.close()
            assert server.body.closed
        with pytest.raises(RuntimeError):
            async with manager:
                pass
    else:
        sync_manager = sdk.beta.agents.sessions.stream("session_test", input="Hello")
        with sync_manager as sync_stream:
            sync_stream.close()
            assert server.body.closed
        with pytest.raises(RuntimeError):
            with sync_manager:
                pass
    assert len(server.requests) == 3


async def test_early_context_exit(sdk: OpenAI | AsyncOpenAI, server: Server) -> None:
    if isinstance(sdk, AsyncOpenAI):
        async with sdk.beta.agents.sessions.stream("session_test", input="Hello"):
            pass
    else:
        with sdk.beta.agents.sessions.stream("session_test", input="Hello"):
            pass
    assert server.body.closed


async def test_async_handler_and_cancellation(server: Server) -> None:
    async with AsyncOpenAI(
        api_key="synthetic",
        base_url="https://sdk-test.example/v1",
        max_retries=0,
        _strict_response_validation=True,
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(server.handle), trust_env=False),
    ) as client:

        async def handler(_arguments: dict[str, object]) -> str:
            await asyncio.sleep(0)
            return "async result"

        server.body = EventBody([turn_event("created"), call(), turn_event("completed"), idle()])
        await consume(client, input="Hello", tool_handlers={"search": handler})
        assert server.inputs()[1]["output"] == "async result"

        async def cancelled(_arguments: dict[str, object]) -> str:
            raise asyncio.CancelledError()

        server.requests.clear()
        server.body = EventBody([turn_event("created"), call(), turn_event("completed"), idle()])
        with pytest.raises(asyncio.CancelledError):
            await consume(client, input="Hello", tool_handlers={"search": cancelled})
        assert len(server.inputs()) == 1
        assert server.body.closed


@pytest.mark.parametrize("pending", [True, False], ids=["pending-call-race", "other-bad-request"])
async def test_tool_result_retry(
    sdk: OpenAI | AsyncOpenAI, server: Server, monkeypatch: pytest.MonkeyPatch, pending: bool
) -> None:
    delays: list[float] = []

    def handler(_arguments: dict[str, object]) -> str:
        return "result"

    async def sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr(time, "sleep", delays.append)
    monkeypatch.setattr(asyncio, "sleep", sleep)
    monkeypatch.setattr(anyio, "sleep", sleep)
    server.body = EventBody([turn_event("created"), call(call_id="call_1"), turn_event("completed"), idle()])
    server.tool_errors = ["Unknown pending tool call: call_1"] * 3 if pending else ["Invalid tool result"]
    if pending:
        await consume(sdk, input="Hello", tool_handlers={"search": handler})
        assert delays == [0.1, 0.3, 0.6]
        assert len(server.inputs()) == 5
        assert server.inputs()[1:] == [server.inputs()[1]] * 4
        keys = [r.headers["idempotency-key"] for r in server.requests if r.method == "POST"]
        assert keys[1]
        assert keys[1:] == [keys[1]] * 4
        assert keys[0] != keys[1]
    else:
        with pytest.raises(BadRequestError):
            await consume(sdk, input="Hello", tool_handlers={"search": handler})
        assert delays == []
        assert len(server.inputs()) == 2
    assert server.body.closed


@pytest.mark.parametrize("input_key_source", ["automatic", "argument", "header"])
async def test_ambiguous_post_delivery_preserves_idempotency(
    sdk: OpenAI | AsyncOpenAI, server: Server, monkeypatch: pytest.MonkeyPatch, input_key_source: str
) -> None:
    def sleep(_delay: float) -> None:
        pass

    async def async_sleep(_delay: float) -> None:
        pass

    def handler(_arguments: dict[str, object]) -> str:
        return "result"

    monkeypatch.setattr(time, "sleep", sleep)
    monkeypatch.setattr(anyio, "sleep", async_sleep)
    monkeypatch.setattr(asyncio, "sleep", async_sleep)
    client = sdk.copy(max_retries=1)
    logical_keys: list[str] = []
    for invocation in range(2):
        server.body = EventBody(
            [
                turn_event("created"),
                call(call_id="call_1"),
                call(call_id="call_2"),
                turn_event("completed"),
                idle(),
            ]
        )
        server.lost_responses = {"agent.session.input.message", "call_1", "call_2"}
        start = len(server.requests)
        options: dict[str, Any] = {"extra_headers": {"x-test": "preserved"}}
        explicit_key = f"input-{invocation}"
        if input_key_source == "argument":
            options["idempotency_key"] = explicit_key
        elif input_key_source == "header":
            options["extra_headers"]["iDeMpOtEnCy-KeY"] = explicit_key
        await consume(client, input="Hello", tool_handlers={"search": handler}, **options)
        posts = [r for r in server.requests[start:] if r.method == "POST"]
        assert len(posts) == 6
        for first, retry in zip(posts[::2], posts[1::2], strict=True):
            key = first.headers["idempotency-key"]
            assert key
            assert retry.headers["idempotency-key"] == key
            assert retry.content == first.content
            assert first.headers["x-test"] == retry.headers["x-test"] == "preserved"
            logical_keys.append(key)
        if input_key_source != "automatic":
            assert posts[0].headers["idempotency-key"] == explicit_key
        assert server.body.closed
    # Both inputs and every logical tool call need separate keys, including the
    # same call IDs reused by a later turn in the same session.
    assert len(set(logical_keys)) == 6


async def test_long_stream_bounds_event_cache_without_repeating_tools(
    sdk: OpenAI | AsyncOpenAI, server: Server
) -> None:
    calls: list[dict[str, object]] = []

    def handler(arguments: dict[str, object]) -> str:
        calls.append(arguments)
        return "result"

    repeated_call = {"event_id": "original-call", **call()}
    payloads = [turn_event("created"), repeated_call]
    for index in range(5000):
        delta_event: dict[str, object] = {
            "type": "agent.session.turn.output_text.delta",
            "event_id": f"delta-{index}",
            "session_id": "session_test",
            "turn_id": "turn_root",
            "item_id": "message_test",
            "output_index": 0,
            "content_index": 0,
            "delta": str(index),
        }
        payloads.extend([delta_event, delta_event])
    payloads.extend([repeated_call, turn_event("completed"), idle()])
    server.body = EventBody(payloads)
    deltas: list[str] = []
    if isinstance(sdk, AsyncOpenAI):
        async with sdk.beta.agents.sessions.stream(
            "session_test", input="Hello", tool_handlers={"search": handler}
        ) as stream:
            async for event in stream:
                if event.type == "agent.session.turn.output_text.delta":
                    deltas.append(event.delta)
            assert len(stream._state.event_ids) <= 1024
            assert len(stream._state.recent_events) <= 1024
    else:
        with sdk.beta.agents.sessions.stream(
            "session_test", input="Hello", tool_handlers={"search": handler}
        ) as sync_stream:
            for event in sync_stream:
                if event.type == "agent.session.turn.output_text.delta":
                    deltas.append(event.delta)
            assert len(sync_stream._state.event_ids) <= 1024
            assert len(sync_stream._state.recent_events) <= 1024
    assert deltas == [str(index) for index in range(5000)]
    assert calls == [{"query": "test"}]
    assert len(server.inputs()) == 2
    assert server.body.closed


@pytest.mark.parametrize("as_json", [False, True], ids=["object", "json-string"])
async def test_handler_cannot_mutate_retained_event(sdk: OpenAI | AsyncOpenAI, server: Server, as_json: bool) -> None:
    original = {"query": "test", "nested": {"values": [1]}}
    arguments: object = json.dumps(original) if as_json else original
    server.body = EventBody([turn_event("created"), call(arguments), turn_event("completed"), idle()])

    def handler(values: dict[str, Any]) -> str:
        values.pop("query")
        values["nested"]["values"].append(2)
        return "result"

    events = await consume(sdk, input="Hello", tool_handlers={"search": handler})
    added = events[1]
    assert added.type == "agent.session.turn.item.added"
    assert added.item.type == "function_call"
    assert added.item.arguments == arguments
    assert original == {"query": "test", "nested": {"values": [1]}}
    assert server.inputs()[1]["output"] == "result"


async def test_consumer_mutation_does_not_redirect_tool(sdk: OpenAI | AsyncOpenAI, server: Server) -> None:
    server.body = EventBody([turn_event("created"), call({"nested": {"value": 42}}), turn_event("completed"), idle()])
    handled: list[dict[str, Any]] = []

    def handler(values: dict[str, Any]) -> str:
        handled.append(values)
        return "result"

    def change_event(event: AgentSessionEvent) -> None:
        if event.type == "agent.session.turn.item.added" and event.item.type == "function_call":
            assert not handled
            values = event.item.arguments
            assert isinstance(values, dict)
            values["nested"]["value"] = 0
            event.item.name = "redirected"
            event.item.call_id = "redirected_call"
            event.item.turn_id = "redirected_turn"

    if isinstance(sdk, AsyncOpenAI):
        async with sdk.beta.agents.sessions.stream(
            "session_test", input="Hello", tool_handlers={"search": handler}
        ) as stream:
            async for event in stream:
                change_event(event)
    else:
        with sdk.beta.agents.sessions.stream(
            "session_test", input="Hello", tool_handlers={"search": handler}
        ) as sync_stream:
            for sync_event in sync_stream:
                change_event(sync_event)

    assert handled == [{"nested": {"value": 42}}]
    assert server.inputs()[1] == {
        "type": "agent.session.input.tool_result",
        "turn_id": "turn_root",
        "call_id": "call_test",
        "success": True,
        "output": "result",
    }
    assert server.body.closed
