from __future__ import annotations

import json

import httpx2
import pytest
from pydantic import BaseModel

from openai import OpenAI, AsyncOpenAI, ContentFilterFinishReasonError
from tests.respx2 import MockRouter

from ...conftest import base_url


class Output(BaseModel):
    value: str


ERROR_MESSAGE = "Could not parse response content as the request was rejected by the content filter"


def test_content_filter_error_without_completion() -> None:
    error = ContentFilterFinishReasonError()
    assert error.completion is None
    assert str(error) == ERROR_MESSAGE


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.respx2(base_url=base_url)
async def test_parse_content_filter_completion(
    sync: bool, client: OpenAI, async_client: AsyncOpenAI, respx2_mock: MockRouter
) -> None:
    respx2_mock.post("/chat/completions").mock(
        return_value=httpx2.Response(
            200,
            json={
                "id": "chatcmpl-example",
                "object": "chat.completion",
                "created": 0,
                "model": "gpt-4o-2024-08-06",
                "choices": [
                    {"index": 0, "message": {"role": "assistant", "content": None}, "finish_reason": "content_filter"}
                ],
                "usage": {"prompt_tokens": 5, "completion_tokens": 0, "total_tokens": 5},
            },
        )
    )

    with pytest.raises(ContentFilterFinishReasonError) as exc_info:
        if sync:
            client.chat.completions.parse(model="gpt-4o-2024-08-06", messages=[], response_format=Output)
        else:
            await async_client.chat.completions.parse(model="gpt-4o-2024-08-06", messages=[], response_format=Output)

    error = exc_info.value
    assert error.completion is not None
    assert error.completion.id == "chatcmpl-example"
    assert error.completion.choices[0].finish_reason == "content_filter"
    assert error.completion.usage is not None
    assert error.completion.usage.total_tokens == 5
    assert str(error) == ERROR_MESSAGE


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("partial_content", [None, '{"value": "example'], ids=["immediate", "after_content"])
@pytest.mark.respx2(base_url=base_url)
async def test_stream_content_filter_completion(
    sync: bool,
    partial_content: str | None,
    client: OpenAI,
    async_client: AsyncOpenAI,
    respx2_mock: MockRouter,
) -> None:
    choices: list[dict[str, object]] = []
    if partial_content is not None:
        choices.append({"index": 0, "delta": {"role": "assistant", "content": partial_content}, "finish_reason": None})
    choices.append({"index": 0, "delta": {"role": "assistant"}, "finish_reason": "content_filter"})
    events = [
        {
            "id": "chatcmpl-example",
            "object": "chat.completion.chunk",
            "created": 0,
            "model": "gpt-4o-2024-08-06",
            "choices": [choice],
        }
        for choice in choices
    ]
    response = httpx2.Response(
        200,
        headers={"content-type": "text/event-stream"},
        content="".join(f"data: {json.dumps(event)}\n\n" for event in events) + "data: [DONE]\n\n",
    )
    respx2_mock.post("/chat/completions").mock(return_value=response)

    with pytest.raises(ContentFilterFinishReasonError) as exc_info:
        if sync:
            with client.chat.completions.stream(
                model="gpt-4o-2024-08-06", messages=[], response_format=Output
            ) as stream:
                stream.get_final_completion()
        else:
            async with async_client.chat.completions.stream(
                model="gpt-4o-2024-08-06", messages=[], response_format=Output
            ) as async_stream:
                await async_stream.get_final_completion()

    error = exc_info.value
    assert error.completion is not None
    assert error.completion.id == "chatcmpl-example"
    assert error.completion.choices[0].finish_reason == "content_filter"
    assert error.completion.choices[0].message.content == partial_content
    assert error.completion.usage is None
    assert str(error) == ERROR_MESSAGE
