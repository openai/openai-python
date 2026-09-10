from __future__ import annotations

import json
from typing import Any, Callable, Iterator, AsyncIterator
from typing_extensions import override

import httpx2
from pydantic import BaseModel

from openai import OpenAI, AsyncOpenAI

# High memory use is intentional: valid API payloads must not be rejected by
# arbitrary body, event, or line caps. Keep this above 32 MiB; do not shrink it
# to make a cap pass. This is a regression probe, not an API maximum. Generate
# data in memory and keep the transport and helper cases sequential.
PAYLOAD_SIZE = 32 * 1024 * 1024 + 1


class TextResult(BaseModel):
    value: str


def assert_intact(actual: str | None, expected: str) -> None:
    # Do not dump a 32 MiB string into pytest's assertion diagnostics.
    intact = actual == expected
    assert intact, "The large API payload was truncated or changed"


def response_body(text: str) -> dict[str, Any]:
    return {
        "id": "resp_test",
        "created_at": 0,
        "model": "gpt-4o-mini",
        "object": "response",
        "parallel_tool_calls": True,
        "status": "completed",
        "tool_choice": "auto",
        "tools": [],
        "output": [
            {
                "type": "message",
                "id": "msg_test",
                "role": "assistant",
                "status": "completed",
                "content": [{"type": "output_text", "text": text, "annotations": []}],
            }
        ],
    }


def sync_client(respond: Callable[[httpx2.Request], httpx2.Response]) -> OpenAI:
    return OpenAI(
        api_key="test-key",
        max_retries=0,
        base_url="https://example.test/v1",
        http_client=httpx2.Client(
            transport=httpx2.MockTransport(respond),
        ),
    )


def async_client(respond: Callable[[httpx2.Request], httpx2.Response]) -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key="test-key",
        max_retries=0,
        base_url="https://example.test/v1",
        http_client=httpx2.AsyncClient(
            transport=httpx2.MockTransport(respond),
        ),
    )


def check_blocking_json() -> None:
    text = "x" * PAYLOAD_SIZE
    with sync_client(lambda _: httpx2.Response(200, json=response_body(text))) as client:
        response = client.responses.create(model="gpt-4o-mini", input="Hello")
        assert_intact(response.output_text, text)


async def check_structured_json() -> None:
    value = "x" * PAYLOAD_SIZE
    text = json.dumps({"value": value})
    # Responses and Chat Completions have distinct structured-output parsers.
    async with async_client(lambda _: httpx2.Response(200, json=response_body(text))) as client:
        response = await client.responses.parse(model="gpt-4o-mini", input="Hello", text_format=TextResult)
        assert_intact(response.output_text, text)
        assert response.output_parsed is not None
        assert_intact(response.output_parsed.value, value)
    with sync_client(
        lambda _: httpx2.Response(
            200,
            json={
                "id": "chatcmpl_test",
                "object": "chat.completion",
                "created": 0,
                "model": "gpt-4o-mini",
                "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": text}}],
            },
        )
    ) as chat_client:
        completion = chat_client.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            response_format=TextResult,
        )
        message = completion.choices[0].message
        assert_intact(message.content, text)
        assert message.parsed is not None
        assert_intact(message.parsed.value, value)


def sse_body(events: Iterator[dict[str, Any]]) -> Iterator[bytes]:
    for event in events:
        data = json.dumps(event).encode()
        yield b"data: "
        # Fragment the large JSON line across ordinary transport-sized chunks.
        for start in range(0, len(data), 64 * 1024):
            yield data[start : start + 64 * 1024]
        yield b"\n\n"
    yield b"data: [DONE]\n\n"


class AsyncSSE(httpx2.AsyncByteStream):
    def __init__(self, events: Iterator[dict[str, Any]]) -> None:
        self.events = events

    @override
    async def __aiter__(self) -> AsyncIterator[bytes]:
        for chunk in sse_body(self.events):
            yield chunk


async def check_responses_stream() -> None:
    text = "x" * PAYLOAD_SIZE

    def events() -> Iterator[dict[str, Any]]:
        initial = response_body("")
        message = initial["output"].pop()
        initial["status"] = message["status"] = "in_progress"
        part = message["content"].pop()
        yield {"type": "response.created", "sequence_number": 0, "response": initial}
        yield {"type": "response.output_item.added", "sequence_number": 1, "output_index": 0, "item": message}
        yield {
            "type": "response.content_part.added",
            "sequence_number": 2,
            "item_id": "msg_test",
            "output_index": 0,
            "content_index": 0,
            "part": part,
        }
        yield {
            "type": "response.output_text.delta",
            "sequence_number": 3,
            "delta": text,
            "item_id": "msg_test",
            "output_index": 0,
            "content_index": 0,
            "logprobs": [],
        }
        yield {
            "type": "response.output_text.done",
            "sequence_number": 4,
            "text": text,
            "item_id": "msg_test",
            "output_index": 0,
            "content_index": 0,
            "logprobs": [],
        }
        yield {"type": "response.completed", "sequence_number": 5, "response": response_body(text)}

    async with async_client(
        lambda _: httpx2.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=AsyncSSE(events()),
        )
    ) as client:
        async with client.responses.stream(model="gpt-4o-mini", input="Hello") as stream:
            saw_delta = saw_done = False
            async for event in stream:
                if event.type == "response.output_text.delta":
                    saw_delta = True
                    assert_intact(event.delta, text)
                    assert_intact(event.snapshot, text)
                elif event.type == "response.output_text.done":
                    saw_done = True
                    assert_intact(event.text, text)
            assert saw_delta and saw_done
            assert_intact((await stream.get_final_response()).output_text, text)


def check_chat_stream() -> None:
    value = "x" * PAYLOAD_SIZE
    text = json.dumps({"value": value})

    def events() -> Iterator[dict[str, Any]]:
        for content, finish_reason in [("", None), (text[:-1], None), (text[-1:], "stop")]:
            yield {
                "id": "chatcmpl_test",
                "object": "chat.completion.chunk",
                "created": 0,
                "model": "gpt-4o-mini",
                "choices": [
                    {"index": 0, "finish_reason": finish_reason, "delta": {"role": "assistant", "content": content}}
                ],
            }

    with sync_client(
        lambda _: httpx2.Response(
            200,
            headers={"content-type": "text/event-stream"},
            content=sse_body(events()),
        )
    ) as client:
        with client.chat.completions.stream(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            response_format=TextResult,
        ) as stream:
            completion = stream.get_final_completion()
            message = completion.choices[0].message
            assert_intact(message.content, text)
            assert message.parsed is not None
            assert_intact(message.parsed.value, value)


async def test_large_payload_contract() -> None:
    # One test prevents pytest-xdist from running high-memory cases together.
    check_blocking_json()
    await check_structured_json()
    await check_responses_stream()
    check_chat_stream()
