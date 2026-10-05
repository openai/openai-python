from __future__ import annotations

import json
import asyncio
import inspect
from typing import Any

import pytest
from pydantic import BaseModel

from openai import OpenAI, AsyncOpenAI, BadRequestError
from openai.lib.beta.agents import function_tool
from tests.lib.streaming.agents.test_results import ResultServer, message
from tests.lib.streaming.agents.test_streams import EventBody, sdk as sdk, call, idle, session, turn_event


@pytest.fixture
def server() -> ResultServer:
    return ResultServer()


async def create(sdk: OpenAI | AsyncOpenAI, **kwargs: Any) -> Any:
    result = sdk.beta.agents.sessions.create(
        agent={"model": "test-model"}, environment={"type": "none"}, input="Question", stream=True, **kwargs
    )
    return await result if inspect.isawaitable(result) else result


class Answer(BaseModel):
    answer: str


@pytest.mark.parametrize("iterate", [False, True])
async def test_creation_dispatches_and_collects(sdk: OpenAI | AsyncOpenAI, server: ResultServer, iterate: bool) -> None:
    seen: list[str] = []

    @function_tool(name="search")
    def search(query: str) -> str:
        seen.append(query)
        return "found"

    state = session("requires_action")
    state["required_actions"] = [
        {
            "type": "function_call",
            "turn_id": "turn_root",
            "call_id": "call_test",
            "name": "search",
            "arguments": {"query": "test"},
        }
    ]
    server.body = EventBody(
        [
            turn_event("created"),
            call(),
            call(),
            {"type": "agent.session.requires_action", "session": state},
            call(call_id="second"),
            message('{"answer":"found"}'),
            turn_event("completed"),
            idle(),
        ]
    )
    stream = await create(sdk, tool_handlers={"search": search}, output_type=Answer)
    if iterate:
        stream.with_result_collection()
    if isinstance(sdk, AsyncOpenAI):
        async with stream:
            if iterate:
                async for event in stream:
                    if event.type == "agent.session.turn.item.added":
                        event.item.call_id = "mutated"
            result = await stream.get_final_result()
    else:
        with stream:
            if iterate:
                for event in stream:
                    if event.type == "agent.session.turn.item.added":
                        event.item.call_id = "mutated"
            result = stream.get_final_result()
    assert seen == ["test", "test"]
    assert result.output_parsed == Answer(answer="found")
    assert [r.method for r in server.requests] == ["POST", "POST", "POST"]
    assert "tool_handlers" not in json.loads(server.requests[0].content)
    outputs = [json.loads(r.content)["events"][0] for r in server.requests[1:]]
    assert [o["call_id"] for o in outputs] == ["call_test", "second"]
    assert all(r.url.path.endswith("/session_test/events") for r in server.requests[1:])
    assert server.body.closed


async def test_creation_handler_retry_uses_distinct_key(sdk: OpenAI | AsyncOpenAI, server: ResultServer) -> None:
    server.body = EventBody([turn_event("created"), call(), turn_event("completed"), idle()])
    server.tool_errors = ["Unknown pending tool call: call_test"]
    seen: list[object] = []

    async def asynchronous(arguments: object) -> str:
        seen.append(arguments)
        return "found"

    def synchronous(arguments: object) -> str:
        seen.append(arguments)
        return "found"

    stream = await create(
        sdk,
        tool_handlers={"search": asynchronous if isinstance(sdk, AsyncOpenAI) else synchronous},
        extra_headers={"iDeMpOtEnCy-KeY": "creation-key", "x-test": "preserved"},
    )
    if isinstance(sdk, AsyncOpenAI):
        async with stream:
            await stream.get_final_result()
    else:
        with stream:
            stream.get_final_result()
    assert len(seen) == 1
    keys = [r.headers["idempotency-key"] for r in server.requests]
    assert keys[0] == "creation-key"
    assert keys[1] == keys[2] != keys[0]
    assert all(r.headers["x-test"] == "preserved" for r in server.requests)


async def test_close_before_resuming_does_not_dispatch(sdk: OpenAI | AsyncOpenAI, server: ResultServer) -> None:
    server.body = EventBody([call()])
    seen: list[object] = []

    def handler(args: dict[str, Any]) -> None:
        seen.append(args)

    stream = await create(sdk, tool_handlers={"search": handler})
    if isinstance(sdk, AsyncOpenAI):
        await stream.__anext__()
        await stream.close()
        async for _ in stream:
            pass
    else:
        next(stream)
        stream.close()
        list(stream)
    assert not seen
    assert len(server.requests) == 1


async def test_handler_failure_sanitized_and_api_failure_propagates(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer
) -> None:
    def fail(_arguments: object) -> str:
        raise ValueError("SYNTHETIC_PRIVATE_DETAIL")

    server.body = EventBody([call()])
    server.tool_errors = ["Rejected tool output"]
    stream = await create(sdk, tool_handlers={"search": fail})
    with pytest.raises(BadRequestError, match="Rejected tool output"):
        if isinstance(sdk, AsyncOpenAI):
            async with stream:
                async for _ in stream:
                    pass
        else:
            with stream:
                list(stream)
    output = json.loads(server.requests[1].content)["events"][0]
    assert output["success"] is False
    assert "SYNTHETIC_PRIVATE_DETAIL" not in server.requests[1].content.decode()
    assert server.body.closed


async def test_nonstreaming_rejects_handlers(sdk: OpenAI | AsyncOpenAI, server: ResultServer) -> None:
    with pytest.raises(ValueError, match="stream=True"):
        if isinstance(sdk, AsyncOpenAI):
            await sdk.beta.agents.sessions.create(environment={"type": "none"}, tool_handlers={})
        else:
            sdk.beta.agents.sessions.create(environment={"type": "none"}, tool_handlers={})
    assert not server.requests


async def test_raw_wrapper_does_not_forward_response_control(sdk: OpenAI | AsyncOpenAI, server: ResultServer) -> None:
    server.body = EventBody([call(), turn_event("created"), turn_event("completed"), idle()])

    def handler(_arguments: object) -> str:
        return "found"

    if isinstance(sdk, AsyncOpenAI):
        async with sdk.beta.agents.sessions.with_streaming_response.create(
            agent={"model": "test-model"},
            environment={"type": "none"},
            input="Question",
            stream=True,
            tool_handlers={"search": handler},
        ) as response:
            stream = await response.parse()
            await stream.get_final_result()
    else:
        with sdk.beta.agents.sessions.with_streaming_response.create(
            agent={"model": "test-model"},
            environment={"type": "none"},
            input="Question",
            stream=True,
            tool_handlers={"search": handler},
        ) as response:
            stream = response.parse()
            stream.get_final_result()
    assert len(server.requests) == 2
    assert "x-stainless-raw-response" not in server.requests[1].headers
    assert server.body.closed


async def test_raw_iteration_cancellation_closes_creation(sdk: OpenAI | AsyncOpenAI, server: ResultServer) -> None:
    def sync_cancel(_arguments: object) -> str:
        raise asyncio.CancelledError()

    async def async_cancel(_arguments: object) -> str:
        raise asyncio.CancelledError()

    server.body = EventBody([call()])
    stream = await create(sdk, tool_handlers={"search": async_cancel if isinstance(sdk, AsyncOpenAI) else sync_cancel})
    with pytest.raises(asyncio.CancelledError):
        if isinstance(sdk, AsyncOpenAI):
            async for _ in stream:
                pass
        else:
            list(stream)
    assert len(server.requests) == 1
    assert server.body.closed
