from __future__ import annotations

import json
from typing import Any

import httpx2
import pytest
from pydantic import BaseModel

import openai
from openai import OpenAI, AsyncOpenAI
from tests.respx2 import MockRouter
from openai.types.chat import ParsedChatCompletion
from openai.lib.streaming.chat import ChatCompletionStreamEvent

from ...conftest import base_url


class ListFilesArgs(BaseModel):
    path: str


@pytest.fixture(params=["initial", "after_role", "empty", "new_choice", "existing_tool", "parallel"])
def tool_call_chunks(request: pytest.FixtureRequest) -> list[dict[str, Any]]:
    scenario = request.param
    chunks: list[dict[str, Any]] = []
    choice_index = 1 if scenario == "new_choice" else 0
    tool_index = 1 if scenario in ("existing_tool", "parallel") else 0

    def chunk(delta: dict[str, Any], index: int = choice_index, finish: str | None = None) -> dict[str, Any]:
        return {
            "id": "chatcmpl-test",
            "object": "chat.completion.chunk",
            "created": 0,
            "model": "gpt-4o-mini",
            "choices": [{"index": index, "delta": delta, "finish_reason": finish}],
        }

    if scenario in ("after_role", "empty", "new_choice"):
        chunks.append(chunk({"role": "assistant", **({"tool_calls": []} if scenario == "empty" else {})}, index=0))

    other_tool = {"index": 0, "id": "call_other", "type": "function", "function": {"name": "other", "arguments": "{}"}}
    if scenario == "existing_tool":
        chunks.append(chunk({"role": "assistant", "tool_calls": [other_tool]}))

    # Match the report: the name and first argument fragment share an index
    # within one chunk. Also split a later argument delta into two entries.
    first_tools = [
        {"index": tool_index, "id": "call_files", "type": "function", "function": {"name": "list_files"}},
        {"index": tool_index, "function": {"arguments": '{"path"'}},
    ]
    if scenario == "parallel":
        first_tools.insert(0, other_tool)
    chunks.extend(
        [
            chunk({"role": "assistant", "tool_calls": first_tools}),
            chunk(
                {
                    "tool_calls": [
                        {"index": tool_index, "function": {"arguments": ": "}},
                        {"index": tool_index, "function": {"arguments": '"."}'}},
                    ]
                }
            ),
            chunk({}, finish="tool_calls"),
        ]
    )
    return chunks


def mock_tool_stream(router: MockRouter, chunks: list[dict[str, Any]]) -> None:
    body = "".join(f"data: {json.dumps(chunk)}\n\n" for chunk in chunks) + "data: [DONE]\n\n"
    router.post("/chat/completions").mock(
        return_value=httpx2.Response(200, text=body, headers={"content-type": "text/event-stream"})
    )


def assert_tool_stream(
    completion: ParsedChatCompletion[None],
    events: list[ChatCompletionStreamEvent[None]],
    chunks: list[dict[str, Any]],
) -> None:
    calls = completion.choices[-1].message.tool_calls
    assert calls is not None
    expected_count = (
        2
        if any(
            tool.get("id") == "call_other"
            for chunk in chunks
            for choice in chunk["choices"]
            for tool in choice["delta"].get("tool_calls", [])
        )
        else 1
    )
    assert len(calls) == expected_count
    assert calls[-1].id == "call_files"
    assert calls[-1].function.name == "list_files"
    assert calls[-1].function.arguments == '{"path": "."}'
    assert calls[-1].function.parsed_arguments == ListFilesArgs(path=".")
    if expected_count == 2:
        assert calls[0].id == "call_other"
        assert calls[0].function.arguments == "{}"

    deltas = [
        event for event in events if event.type == "tool_calls.function.arguments.delta" and event.name == "list_files"
    ]
    assert [event.arguments_delta for event in deltas] == ["", '{"path"', ": ", '"."}']
    done = [
        event for event in events if event.type == "tool_calls.function.arguments.done" and event.name == "list_files"
    ]
    assert len(done) == 1
    assert done[0].arguments == '{"path": "."}'
    assert done[0].parsed_arguments == ListFilesArgs(path=".")
    # Snapshot normalization must not change the raw chunks exposed to callers.
    assert [event.chunk.to_dict() for event in events if event.type == "chunk"] == chunks


@pytest.mark.respx2(base_url=base_url)
def test_duplicate_tool_call_deltas(
    client: OpenAI, respx2_mock: MockRouter, tool_call_chunks: list[dict[str, Any]]
) -> None:
    mock_tool_stream(respx2_mock, tool_call_chunks)
    with client.chat.completions.stream(
        model="gpt-4o-mini", messages=[], tools=[openai.pydantic_function_tool(ListFilesArgs, name="list_files")]
    ) as stream:
        events = list(stream)
        assert_tool_stream(stream.get_final_completion(), events, tool_call_chunks)


@pytest.mark.respx2(base_url=base_url)
async def test_async_duplicate_tool_call_deltas(
    async_client: AsyncOpenAI, respx2_mock: MockRouter, tool_call_chunks: list[dict[str, Any]]
) -> None:
    mock_tool_stream(respx2_mock, tool_call_chunks)
    async with async_client.chat.completions.stream(
        model="gpt-4o-mini", messages=[], tools=[openai.pydantic_function_tool(ListFilesArgs, name="list_files")]
    ) as stream:
        events = [event async for event in stream]
        assert_tool_stream(await stream.get_final_completion(), events, tool_call_chunks)
