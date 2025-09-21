import json
import httpx
import pytest
from httpx import MockTransport, Request, Response

from openai import AsyncOpenAI
from openai._base_client import HTTPX_DEFAULT_TIMEOUT
from openai._streaming import StreamEvent, extract_text


def _sse(*events):
    """
    Build a mock SSE stream from provided events and append [DONE] sentinel
    so the client knows when to close the stream.
    """
    body = b"".join([b"data: " + json.dumps(e).encode() + b"\n\n" for e in events])
    body += b"data: [DONE]\n\n"  # IMPORTANT: closes the stream
    return body


@pytest.mark.asyncio
async def test_responses_stream_unified_with_mock() -> None:
    """
    Unified streaming should yield StreamEvent objects and concatenate text deltas.
    MUST start with `response.created` to satisfy the streaming state machine.
    """
    async def handler(request: Request) -> Response:  # transport stub
        data = _sse(
            {
                "type": "response.created",
                "response": {"id": "rsp_test", "type": "response"},
                "model": "gpt-4o-mini",
            },
            {"type": "response.output_text.delta", "delta": "Hello "},
            {"type": "response.output_text.delta", "delta": "World"},
            {"type": "response.completed"},
        )
        return Response(200, content=data, headers={"content-type": "text/event-stream"})

    async with httpx.AsyncClient(
        transport=MockTransport(handler),
        timeout=HTTPX_DEFAULT_TIMEOUT,
        base_url="https://api.openai.com",
    ) as httpx_client:
        client = AsyncOpenAI(http_client=httpx_client)
        parts: list[str] = []
        async with client.responses.stream(model="gpt-4o-mini", input="hi", unified=True) as stream:
            async for ev in stream:  # type: StreamEvent
                text = extract_text(ev)
                if ev.type == "output_text.delta" and text:
                    parts.append(text)

    assert "".join(parts) == "Hello World"


@pytest.mark.asyncio
async def test_responses_stream_legacy_shape_with_mock() -> None:
    """
    Legacy streaming should still yield raw events. Consume until completed to avoid pending tasks.
    """
    async def handler(request: Request) -> Response:  # transport stub
        data = _sse(
            {
                "type": "response.created",
                "response": {"id": "rsp_test2", "type": "response"},
                "model": "gpt-4o-mini",
            },
            {"type": "response.output_text.delta", "delta": "X"},
            {"type": "response.completed"},
        )
        return Response(200, content=data, headers={"content-type": "text/event-stream"})

    async with httpx.AsyncClient(
        transport=MockTransport(handler),
        timeout=HTTPX_DEFAULT_TIMEOUT,
        base_url="https://api.openai.com",
    ) as httpx_client:
        client = AsyncOpenAI(http_client=httpx_client)

        got_delta = False
        async with client.responses.stream(model="gpt-4o-mini", input="hi") as stream:
            async for evt in stream:
                if getattr(evt, "type", None) == "response.output_text.delta":
                    got_delta = True
                if getattr(evt, "type", None) == "response.completed":
                    break  # exit cleanly

    assert got_delta is True
