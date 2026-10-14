from __future__ import annotations

import json
import asyncio
from typing import Any, cast

import httpx2
import pytest
from pydantic import Field, BaseModel

from openai import OpenAI, AsyncOpenAI, pydantic_responses_function_tool
from openai.types.responses import ResponseInputParam, EasyInputMessageParam
from openai.lib.tool_diagnostics import ToolDiagnostic
from openai.lib.responses_tool_runner import (
    FunctionResult,
    ToolRunnerError,
    RegisteredFunction,
    ResponsesToolLedger,
    ResponsesToolRunner,
    AsyncRegisteredFunction,
    ResponsesToolCheckpoint,
    AsyncResponsesToolLedger,
    AsyncResponsesToolRunner,
)
from openai.types.responses.response_create_params import ContextManagement, ResponseCreateParamsNonStreaming

from .test_responses_tool_runner import TOOL, FINAL, PARAMS, fn, sse, resp


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("stream", [False, True])
async def test_failed_request_has_one_content_free_diagnostic(lane: str, stream: bool) -> None:
    requests = 0
    diagnostics: list[ToolDiagnostic] = []

    def handler(_request: httpx2.Request) -> httpx2.Response:
        nonlocal requests
        requests += 1
        return httpx2.Response(500, json={"error": {"message": "private failure detail"}})

    if lane == "sync":
        with OpenAI(
            api_key="fake", max_retries=0, http_client=httpx2.Client(transport=httpx2.MockTransport(handler))
        ) as client:
            with pytest.raises(ToolRunnerError):
                ResponsesToolRunner().run(client, PARAMS, stream=stream, on_diagnostic=diagnostics.append)
    else:
        async with AsyncOpenAI(
            api_key="fake", max_retries=0, http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
        ) as async_client:
            with pytest.raises(ToolRunnerError):
                await AsyncResponsesToolRunner().run(
                    async_client, PARAMS, stream=stream, on_diagnostic=diagnostics.append
                )
    assert requests == 1
    assert len(diagnostics) == 1
    assert diagnostics[0]["stage"] == "request"
    assert diagnostics[0]["reason"] == "api_failed"
    assert diagnostics[0]["usage"] is None
    assert diagnostics[0]["duration_ms"] >= 0
    assert "private failure detail" not in json.dumps(diagnostics)


@pytest.mark.parametrize("stream", [False, True])
async def test_cancelled_request_has_one_diagnostic(stream: bool) -> None:
    diagnostics: list[ToolDiagnostic] = []

    async def handler(_request: httpx2.Request) -> httpx2.Response:
        raise asyncio.CancelledError

    async with AsyncOpenAI(
        api_key="fake", max_retries=0, http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
    ) as client:
        with pytest.raises(asyncio.CancelledError):
            await AsyncResponsesToolRunner().run(client, PARAMS, stream=stream, on_diagnostic=diagnostics.append)
    assert len(diagnostics) == 1
    assert diagnostics[0]["reason"] == "cancelled"
    assert diagnostics[0]["usage"] is None


class Booking(BaseModel):
    seats: int = Field(ge=1, le=6)


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("stream", [False, True])
@pytest.mark.parametrize("outcome", ["valid", "invalid_arguments", "invalid_output"])
async def test_existing_pydantic_tool_parser_receipts_and_wire_body(lane: str, stream: bool, outcome: str) -> None:
    effects: list[Booking] = []
    requests: list[dict[str, Any]] = []
    checkpoints: list[ResponsesToolCheckpoint] = []
    diagnostics: list[ToolDiagnostic] = []

    def execute(args: Booking) -> FunctionResult:
        effects.append(args)
        return "reserved" if outcome != "invalid_output" else cast(FunctionResult, object())

    async def aexecute(args: Booking) -> FunctionResult:
        return execute(args)

    async def save(value: ResponsesToolCheckpoint) -> None:
        checkpoints.append(value)

    error: pytest.ExceptionInfo[ToolRunnerError] | None = None
    tool = pydantic_responses_function_tool(Booking, name="reserve")

    def handler(request: httpx2.Request) -> httpx2.Response:
        data = json.loads(request.content)
        requests.append(data)
        reply = resp([fn("reserve", "reserve-1", seats=9 if outcome == "invalid_arguments" else 2)], "r1")
        response = reply if len(requests) == 1 else FINAL
        if stream:
            return httpx2.Response(200, headers={"content-type": "text/event-stream"}, content=sse(response))
        return httpx2.Response(200, json=response)

    if lane == "sync":
        runner = ResponsesToolRunner(functions=[RegisteredFunction.from_tool(tool, execute=execute)])
        with OpenAI(api_key="fake", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
            if outcome == "valid":
                runner.run(
                    client,
                    PARAMS,
                    stream=stream,
                    ledger=ResponsesToolLedger("receipt", checkpoints.append),
                    on_diagnostic=diagnostics.append,
                )
            else:
                with pytest.raises(ToolRunnerError) as error:
                    runner.run(
                        client,
                        PARAMS,
                        stream=stream,
                        ledger=ResponsesToolLedger("receipt", checkpoints.append),
                        on_diagnostic=diagnostics.append,
                    )
    else:
        runner_async = AsyncResponsesToolRunner(functions=[AsyncRegisteredFunction.from_tool(tool, execute=aexecute)])
        async with AsyncOpenAI(
            api_key="fake", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
        ) as client_async:
            if outcome == "valid":
                await runner_async.run(
                    client_async,
                    PARAMS,
                    stream=stream,
                    ledger=AsyncResponsesToolLedger("receipt", save),
                    on_diagnostic=diagnostics.append,
                )
            else:
                with pytest.raises(ToolRunnerError) as error:
                    await runner_async.run(
                        client_async,
                        PARAMS,
                        stream=stream,
                        ledger=AsyncResponsesToolLedger("receipt", save),
                        on_diagnostic=diagnostics.append,
                    )
    assert [entry.seats for entry in effects] == ([] if outcome == "invalid_arguments" else [2])
    assert requests[0]["tools"] == [dict(tool)]
    recorded_requests = [event for event in diagnostics if event["stage"] == "request"]
    assert len(recorded_requests) == len(requests)
    assert all(event["usage"] is None for event in recorded_requests)
    assert "seats" not in json.dumps(diagnostics)
    if outcome == "valid":
        assert checkpoints[-1]["phase"] == "final"
        assert requests[1]["input"][-1] == {
            "type": "function_call_output",
            "call_id": "reserve-1",
            "output": "reserved",
        }
    elif outcome == "invalid_output":
        assert len(requests) == 1
        assert error is not None
        assert error.value.attempted_call_ids == ("reserve-1",)
        assert error.value.completed_call_ids == ()
        assert checkpoints[-1]["phase"] == "pending"
        assert checkpoints[-1]["attempted_call_ids"] == ["reserve-1"]


def test_parse_only_and_untyped_adapters_fail_at_registration() -> None:
    tool = pydantic_responses_function_tool(Booking)
    with pytest.raises(ValueError, match="executor"):
        ResponsesToolRunner(functions=cast(Any, [tool]))
    with pytest.raises(ValueError, match="Pydantic"):
        RegisteredFunction.from_tool(TOOL, execute=lambda _args: "done")
    with pytest.raises(ValueError, match="executor"):
        RegisteredFunction.from_tool(tool, execute=cast(Any, None))


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_ordinary_executor_can_reuse_buffer_without_rewriting_prior_output(lane: str) -> None:
    requests: list[dict[str, Any]] = []
    buffer: FunctionResult = [{"type": "input_text", "text": ""}]

    def execute(args: dict[str, object]) -> FunctionResult:
        text = args["text"]
        assert isinstance(text, str) and isinstance(buffer, list)
        buffer[:] = [{"type": "input_text", "text": text}]
        return buffer

    async def aexecute(args: dict[str, object]) -> FunctionResult:
        return execute(args)

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(json.loads(request.content))
        first = resp([fn("record", "one", text="first"), fn("record", "two", text="second")], "first")
        return httpx2.Response(200, json=first if len(requests) == 1 else FINAL)

    if lane == "sync":
        runner = ResponsesToolRunner(functions=[RegisteredFunction(TOOL, execute)])
        with OpenAI(api_key="fake", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
            runner.run(client, PARAMS)
    else:
        async_runner = AsyncResponsesToolRunner(functions=[AsyncRegisteredFunction(TOOL, aexecute)])
        async with AsyncOpenAI(
            api_key="fake", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
        ) as async_client:
            await async_runner.run(async_client, PARAMS)
    outputs = [item for item in requests[1]["input"] if item.get("type") == "function_call_output"]
    assert outputs == [
        {"type": "function_call_output", "call_id": "one", "output": [{"type": "input_text", "text": "first"}]},
        {"type": "function_call_output", "call_id": "two", "output": [{"type": "input_text", "text": "second"}]},
    ]


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("iterable", [False, True], ids=["list", "generator"])
async def test_ordinary_admitted_nested_input_and_metadata_survive_executor_mutation(lane: str, iterable: bool) -> None:
    requests: list[dict[str, Any]] = []
    original: EasyInputMessageParam = {"role": "user", "content": [{"type": "input_text", "text": "admitted task"}]}
    input_list: ResponseInputParam = [original]
    metadata = {"ticket": "admitted"}
    management: list[ContextManagement] = [{"type": "compaction", "compact_threshold": 4096}]
    # The helper also accepts iterable input at runtime, beyond the generated List annotation.
    inputs = cast(ResponseInputParam, (item for item in input_list)) if iterable else input_list

    def execute(_args: dict[str, object]) -> FunctionResult:
        original["content"] = [{"type": "input_text", "text": "later task"}]
        metadata["ticket"] = "later"
        management[0]["compact_threshold"] = 8192
        return "ok"

    async def aexecute(args: dict[str, object]) -> FunctionResult:
        return execute(args)

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(json.loads(request.content))
        first = resp([fn("record", "one", text="run")], "first")
        return httpx2.Response(200, json=first if len(requests) == 1 else FINAL)

    params: ResponseCreateParamsNonStreaming = {
        **PARAMS,
        "input": inputs,
        "metadata": metadata,
        "context_management": (item for item in management) if iterable else None,
    }
    if lane == "sync":
        runner = ResponsesToolRunner(functions=[RegisteredFunction(TOOL, execute)])
        with OpenAI(api_key="fake", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
            runner.run(client, params)
    else:
        async_runner = AsyncResponsesToolRunner(functions=[AsyncRegisteredFunction(TOOL, aexecute)])
        async with AsyncOpenAI(
            api_key="fake", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
        ) as async_client:
            await async_runner.run(async_client, params)
    assert len(requests) == 2
    assert requests[1]["input"][0] == {"role": "user", "content": [{"type": "input_text", "text": "admitted task"}]}
    assert requests[1]["metadata"] == {"ticket": "admitted"}
    expected_management = [{"type": "compaction", "compact_threshold": 4096}] if iterable else None
    assert requests[0]["context_management"] == expected_management
    assert requests[1]["context_management"] == expected_management
