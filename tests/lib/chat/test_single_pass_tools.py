from __future__ import annotations

import json
from typing import Protocol, cast
from collections.abc import Iterator

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from tests.respx2 import MockRouter
from openai.types.chat import ChatCompletionToolUnionParam

from ...conftest import base_url


class MockRequestCall(Protocol):
    request: httpx2.Request


def single_pass_tools() -> Iterator[ChatCompletionToolUnionParam]:
    yield {
        "type": "function",
        "function": {
            "name": "get_weather",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }


TOOL_CALL = {
    "id": "call-test",
    "type": "function",
    "function": {"name": "get_weather", "arguments": '{"city":"San Francisco"}'},
}


def completion_response() -> httpx2.Response:
    return httpx2.Response(
        200,
        json={
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "created": 0,
            "model": "gpt-test",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": None, "tool_calls": [TOOL_CALL], "refusal": None},
                    "logprobs": None,
                    "finish_reason": "tool_calls",
                }
            ],
        },
    )


STREAM_RESPONSE = """\
data: {"id":"chatcmpl-test","object":"chat.completion.chunk","created":0,"model":"gpt-test","choices":[{"index":0,"delta":{"role":"assistant","content":null,"tool_calls":[{"index":0,"id":"call-test","type":"function","function":{"name":"get_weather","arguments":"{\\"city\\":\\"San Francisco\\"}"}}],"refusal":null},"logprobs":null,"finish_reason":null}]}

data: {"id":"chatcmpl-test","object":"chat.completion.chunk","created":0,"model":"gpt-test","choices":[{"index":0,"delta":{},"logprobs":null,"finish_reason":"tool_calls"}]}

data: [DONE]

"""


def assert_request_and_parsed_tool(respx2_mock: MockRouter, parsed_arguments: object) -> None:
    calls = cast("list[MockRequestCall]", respx2_mock.calls)
    body = json.loads(calls[0].request.content)
    assert body["tools"] == list(single_pass_tools())
    assert parsed_arguments == {"city": "San Francisco"}


@pytest.mark.respx2(base_url=base_url)
def test_parse_preserves_single_pass_tools(client: OpenAI, respx2_mock: MockRouter) -> None:
    respx2_mock.post("/chat/completions").mock(return_value=completion_response())

    completion = client.chat.completions.parse(
        model="gpt-test",
        messages=[{"role": "user", "content": "weather"}],
        tools=single_pass_tools(),
    )

    tool_calls = completion.choices[0].message.tool_calls
    assert tool_calls is not None
    assert_request_and_parsed_tool(respx2_mock, tool_calls[0].function.parsed_arguments)


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.asyncio
async def test_async_parse_preserves_single_pass_tools(async_client: AsyncOpenAI, respx2_mock: MockRouter) -> None:
    respx2_mock.post("/chat/completions").mock(return_value=completion_response())

    completion = await async_client.chat.completions.parse(
        model="gpt-test",
        messages=[{"role": "user", "content": "weather"}],
        tools=single_pass_tools(),
    )

    tool_calls = completion.choices[0].message.tool_calls
    assert tool_calls is not None
    assert_request_and_parsed_tool(respx2_mock, tool_calls[0].function.parsed_arguments)


@pytest.mark.respx2(base_url=base_url)
def test_stream_preserves_single_pass_tools(client: OpenAI, respx2_mock: MockRouter) -> None:
    respx2_mock.post("/chat/completions").mock(
        return_value=httpx2.Response(200, text=STREAM_RESPONSE, headers={"content-type": "text/event-stream"})
    )

    with client.chat.completions.stream(
        model="gpt-test",
        messages=[{"role": "user", "content": "weather"}],
        tools=single_pass_tools(),
    ) as stream:
        completion = stream.get_final_completion()

    tool_calls = completion.choices[0].message.tool_calls
    assert tool_calls is not None
    assert_request_and_parsed_tool(respx2_mock, tool_calls[0].function.parsed_arguments)


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.asyncio
async def test_async_stream_preserves_single_pass_tools(async_client: AsyncOpenAI, respx2_mock: MockRouter) -> None:
    respx2_mock.post("/chat/completions").mock(
        return_value=httpx2.Response(200, text=STREAM_RESPONSE, headers={"content-type": "text/event-stream"})
    )

    async with async_client.chat.completions.stream(
        model="gpt-test",
        messages=[{"role": "user", "content": "weather"}],
        tools=single_pass_tools(),
    ) as stream:
        completion = await stream.get_final_completion()

    tool_calls = completion.choices[0].message.tool_calls
    assert tool_calls is not None
    assert_request_and_parsed_tool(respx2_mock, tool_calls[0].function.parsed_arguments)
