from __future__ import annotations

import json

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from tests.respx2 import MockRouter
from openai.types.chat import ChatCompletionToolUnionParam

from ...conftest import base_url


def mock_tool_call(
    respx2_mock: MockRouter, *, streaming: bool = False, strict: bool = True
) -> ChatCompletionToolUnionParam:
    tool: ChatCompletionToolUnionParam = {
        "type": "function",
        "function": {
            "name": "get_weather",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
                "additionalProperties": False,
            },
            "strict": strict,
        },
    }
    tool_call: dict[str, object] = {
        "id": "call-test",
        "type": "function",
        "function": {"name": "get_weather", "arguments": '{"city":"San Francisco"}'},
    }
    message = {"role": "assistant", "content": None, "tool_calls": [tool_call]}
    response: dict[str, object] = {
        "id": "chatcmpl-test",
        "object": "chat.completion.chunk" if streaming else "chat.completion",
        "created": 0,
        "model": "gpt-test",
        "choices": [{"index": 0, "delta" if streaming else "message": message, "finish_reason": "tool_calls"}],
    }
    if streaming:
        tool_call["index"] = 0

    def handle_request(request: httpx2.Request) -> httpx2.Response:
        assert json.loads(request.content)["tools"] == [tool]
        if streaming:
            return httpx2.Response(
                200,
                text=f"data: {json.dumps(response)}\n\ndata: [DONE]\n\n",
                headers={"content-type": "text/event-stream"},
            )
        return httpx2.Response(200, json=response)

    respx2_mock.post("/chat/completions").mock(side_effect=handle_request)
    return tool


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.parametrize("use_async", [False, True])
@pytest.mark.asyncio
async def test_parse_preserves_single_pass_tools(
    client: OpenAI, async_client: AsyncOpenAI, respx2_mock: MockRouter, use_async: bool
) -> None:
    tools = iter([mock_tool_call(respx2_mock)])
    if use_async:
        completion = await async_client.chat.completions.parse(model="gpt-test", messages=[], tools=tools)
    else:
        completion = client.chat.completions.parse(model="gpt-test", messages=[], tools=tools)

    tool_calls = completion.choices[0].message.tool_calls
    assert tool_calls is not None
    assert tool_calls[0].function.parsed_arguments == {"city": "San Francisco"}


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.parametrize("use_async", [False, True])
@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.asyncio
async def test_stream_preserves_single_pass_tools(
    client: OpenAI, async_client: AsyncOpenAI, respx2_mock: MockRouter, use_async: bool, strict: bool
) -> None:
    tools = iter([mock_tool_call(respx2_mock, streaming=True, strict=strict)])
    if use_async:
        async with async_client.chat.completions.stream(model="gpt-test", messages=[], tools=tools) as async_stream:
            completion = await async_stream.get_final_completion()
    else:
        with client.chat.completions.stream(model="gpt-test", messages=[], tools=tools) as stream:
            completion = stream.get_final_completion()

    tool_calls = completion.choices[0].message.tool_calls
    assert tool_calls is not None
    assert tool_calls[0].function.parsed_arguments == ({"city": "San Francisco"} if strict else None)
