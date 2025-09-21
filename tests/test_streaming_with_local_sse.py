import asyncio
import json
import pytest
import httpx

from starlette.applications import Starlette
from starlette.responses import StreamingResponse
from starlette.routing import Route

from openai import AsyncOpenAI
from openai._base_client import HTTPX_DEFAULT_TIMEOUT

def _sse_frame(obj: dict) -> bytes:
    # One JSON object per SSE "data:" frame
    return (f"data: " + json.dumps(obj, separators=(",", ":")) + "\n\n").encode()

def _unified_sequence() -> list[bytes]:
    # Full init (generic output + text channel) before deltas
    return [
        _sse_frame({"type": "response.created",
                    "response": {"id": "rsp_local_1", "type": "response"},
                    "model": "gpt-4o-mini"}),
        _sse_frame({"type": "response.output.created",
                    "output_index": 0,
                    "id": "txt_1",
                    "output": {"index": 0, "id": "txt_1", "type": "output_text"},
                    "output_type": "output_text"}),
        _sse_frame({"type": "response.output_text.created",
                    "output_index": 0, "index": 0, "id": "txt_1"}),
        _sse_frame({"type": "response.output_text.delta",
                    "output_index": 0, "index": 0, "value": "Hello ", "delta": "Hello "}),
        _sse_frame({"type": "response.output_text.delta",
                    "output_index": 0, "index": 0, "value": "World", "delta": "World"}),
        _sse_frame({"type": "response.completed", "id": "rsp_local_1", "status": "ok"}),
        b"data: [DONE]\n\n",
    ]

def _legacy_sequence() -> list[bytes]:
    return [
        _sse_frame({"type": "response.created",
                    "response": {"id": "rsp_local_2", "type": "response"},
                    "model": "gpt-4o-mini"}),
        _sse_frame({"type": "response.output.created",
                    "output_index": 0,
                    "id": "txt_2",
                    "output": {"index": 0, "id": "txt_2", "type": "output_text"},
                    "output_type": "output_text"}),
        _sse_frame({"type": "response.output_text.created",
                    "output_index": 0, "index": 0, "id": "txt_2"}),
        _sse_frame({"type": "response.output_text.delta",
                    "output_index": 0, "index": 0, "value": "X", "delta": "X"}),
        _sse_frame({"type": "response.completed", "id": "rsp_local_2", "status": "ok"}),
        b"data: [DONE]\n\n",
    ]

def _make_app(frames: list[bytes]) -> Starlette:
    async def responses_endpoint(request):
        async def gen():
            for chunk in frames:
                await asyncio.sleep(0)  # tiny yield to simulate I/O
                yield chunk
        return StreamingResponse(gen(), media_type="text/event-stream")
    # IMPORTANT: the SDK will call base_url + "/responses"
    return Starlette(routes=[Route("/v1/responses", responses_endpoint, methods=["POST"])])

def _make_openai_client(app: Starlette) -> AsyncOpenAI:
    # httpx>=0.24 has public ASGITransport; older versions keep it under _transports
    try:
        from httpx import ASGITransport
    except Exception:
        from httpx._transports.asgi import ASGITransport  # type: ignore

    transport = ASGITransport(app=app)
    http_client = httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver/v1",   # so the POST goes to /v1/responses
        timeout=HTTPX_DEFAULT_TIMEOUT,
    )
    return AsyncOpenAI(api_key="test-key", http_client=http_client, base_url="http://testserver/v1")

@pytest.mark.asyncio
async def test_unified_stream_via_local_sse() -> None:
    app = _make_app(_unified_sequence())
    client = _make_openai_client(app)
    assert client._client._base_url.host == "testserver"  # sanity

    parts: list[str] = []
    async with client.responses.stream(model="gpt-4o-mini", input="hi") as stream:
        async for ev in stream:
            # Only aggregate on *delta* events; don't call extract_text on others
            name = getattr(ev, "event", getattr(ev, "type", None))
            if name in ("response.output_text.delta", "output_text.delta"):
                # prefer value; fallback to delta if needed
                val = getattr(ev, "value", None)
                if val is None and hasattr(ev, "delta"):
                    val = ev.delta
                if val:
                    parts.append(val)
            if name in ("response.completed", "completed"):
                break

    await client.close()
    assert "".join(parts) == "Hello World"

@pytest.mark.asyncio
async def test_legacy_stream_via_local_sse() -> None:
    app = _make_app(_legacy_sequence())
    client = _make_openai_client(app)

    got_delta = False
    async with client.responses.stream(model="gpt-4o-mini", input="hi") as stream:
        async for ev in stream:
            name = getattr(ev, "event", getattr(ev, "type", None))
            if name in ("response.output_text.delta", "output_text.delta"):
                got_delta = True
            if name in ("response.completed", "completed"):
                break

    await client.close()
    assert got_delta is True
