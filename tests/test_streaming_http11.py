from __future__ import annotations

import os
import json
import socket
import importlib
import threading
from typing import Any, Iterator
from dataclasses import field, dataclass
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing_extensions import override

import pytest

from openai import OpenAI, AsyncOpenAI


@dataclass
class StreamingServer:
    url: str = ""
    connections: int = 0
    requests: int = 0
    ending: str = "complete"
    release: threading.Event = field(default_factory=threading.Event)


@pytest.fixture
def streaming_server() -> Iterator[StreamingServer]:
    state = StreamingServer()

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        @override
        def setup(self) -> None:
            super().setup()
            state.connections += 1
            self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        def do_POST(self) -> None:
            self.rfile.read(int(self.headers["Content-Length"]))
            state.requests += 1
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Transfer-Encoding", "chunked")
            self.end_headers()

            if self.path.endswith("/responses"):
                event: dict[str, object] = {
                    "type": "response.completed",
                    "sequence_number": 0,
                    "response": {
                        "id": "resp_synthetic",
                        "object": "response",
                        "created_at": 0,
                        "status": "completed",
                        "model": "synthetic",
                        "output": [],
                    },
                }
                payload = f"event: response.completed\ndata: {json.dumps(event)}\n\n".encode()
            else:
                event = {
                    "id": "chatcmpl-synthetic",
                    "object": "chat.completion.chunk",
                    "created": 0,
                    "model": "synthetic",
                    "choices": [{"index": 0, "delta": {"content": "hello"}, "finish_reason": "stop"}],
                }
                payload = f"data: {json.dumps(event)}\n\ndata: [DONE]\n\n".encode()

            try:
                self.wfile.write(f"{len(payload):x}\r\n".encode() + payload + b"\r\n")
                if state.ending == "stall":
                    state.release.wait(timeout=5)
                elif state.ending == "truncate":
                    self.close_connection = True
                    return
                self.wfile.write(b"0\r\n\r\n")
            except ConnectionError:
                self.close_connection = True

        @override
        def log_message(self, format: str, *args: object) -> None:  # noqa: A002
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    state.url = f"http://127.0.0.1:{server.server_port}/v1"
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01})
    thread.start()
    try:
        yield state
    finally:
        state.release.set()
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
        assert not thread.is_alive()


@pytest.fixture(
    params=[
        "httpx2",
        pytest.param(
            "httpx",
            marks=pytest.mark.skipif(
                os.environ.get("OPENAI_TEST_LEGACY_HTTPX") != "1", reason="requires the legacy HTTPX compatibility lane"
            ),
        ),
    ]
)
def http_module(request: pytest.FixtureRequest) -> Any:
    return importlib.import_module(request.param)


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("api", ["chat", "responses"])
async def test_fully_consumed_stream_reuses_http11_connection(
    sync: bool, api: str, http_module: Any, streaming_server: StreamingServer
) -> None:
    if sync:
        with OpenAI(
            api_key="synthetic",
            base_url=streaming_server.url,
            max_retries=0,
            http_client=http_module.Client(trust_env=False, limits=http_module.Limits(max_connections=1)),
        ) as client:
            for _ in range(5):
                if api == "chat":
                    with client.chat.completions.create(model="synthetic", messages=[], stream=True) as stream:
                        assert [chunk.choices[0].delta.content for chunk in stream] == ["hello"]
                else:
                    with client.responses.create(model="synthetic", input="hello", stream=True) as responses_stream:
                        assert [event.type for event in responses_stream] == ["response.completed"]
    else:
        async with AsyncOpenAI(
            api_key="synthetic",
            base_url=streaming_server.url,
            max_retries=0,
            http_client=http_module.AsyncClient(trust_env=False, limits=http_module.Limits(max_connections=1)),
        ) as async_client:
            for _ in range(5):
                if api == "chat":
                    async with await async_client.chat.completions.create(
                        model="synthetic", messages=[], stream=True
                    ) as async_stream:
                        assert [chunk.choices[0].delta.content async for chunk in async_stream] == ["hello"]
                else:
                    async with await async_client.responses.create(
                        model="synthetic", input="hello", stream=True
                    ) as async_responses_stream:
                        assert [event.type async for event in async_responses_stream] == ["response.completed"]

    assert streaming_server.requests == 5
    assert streaming_server.connections == 1


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("ending", ["truncate", "stall"])
async def test_bad_http_ending_preserves_completed_output_and_releases_pool_slot(
    sync: bool, ending: str, http_module: Any, streaming_server: StreamingServer
) -> None:
    streaming_server.ending = ending
    if sync:
        with OpenAI(
            api_key="synthetic",
            base_url=streaming_server.url,
            max_retries=0,
            timeout=http_module.Timeout(5, read=0.05),
            http_client=http_module.Client(trust_env=False, limits=http_module.Limits(max_connections=1)),
        ) as client:
            for _ in range(2):
                with client.chat.completions.create(model="synthetic", messages=[], stream=True) as stream:
                    assert [chunk.choices[0].delta.content for chunk in stream] == ["hello"]
                streaming_server.ending = "complete"
    else:
        async with AsyncOpenAI(
            api_key="synthetic",
            base_url=streaming_server.url,
            max_retries=0,
            timeout=http_module.Timeout(5, read=0.05),
            http_client=http_module.AsyncClient(trust_env=False, limits=http_module.Limits(max_connections=1)),
        ) as async_client:
            for _ in range(2):
                async with await async_client.chat.completions.create(
                    model="synthetic", messages=[], stream=True
                ) as async_stream:
                    assert [chunk.choices[0].delta.content async for chunk in async_stream] == ["hello"]
                streaming_server.ending = "complete"

    assert streaming_server.requests == 2
    assert streaming_server.connections == 2
